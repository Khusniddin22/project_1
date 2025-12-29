import datetime
import json
import logging
import os
from datetime import date, timedelta

import pandas as pd
import requests
from dotenv import load_dotenv
from pandas import DataFrame

load_dotenv(".env")


logger_utils = logging.getLogger("utils")
logger_utils.setLevel(logging.DEBUG)  # Устанавливаем уровень логирования
os.makedirs("logs", exist_ok=True)
file_handler = logging.FileHandler("logs/utils.log")  # Указываем путь к файлу с логами
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger_utils.addHandler(file_handler)  # Добавляем обработчик к логгеру


path_file = os.path.join("..", "..", "data", "operations.xlsx")
path_json = os.path.join("..", "..", "data", "user_settings.json")


# Функции для страницы "Главная"


def time_for_greeting() -> str:
    """Функция приветствия относительно текущего часа"""
    logger_utils.info("Вызвана функция time_for_greeting без аргумента")

    now = datetime.datetime.now()
    current_now = now.hour
    if current_now >= 0 and current_now < 4:
        logger_utils.info("Функция time_for_greeting возвращает 'Доброй ночи'")
        return "Доброй ночи"
    elif current_now >= 4 and current_now < 12:
        logger_utils.info("Функция time_for_greeting возвращает 'Доброе утро'")
        return "Доброе утро"
    elif current_now >= 12 and current_now < 17:
        logger_utils.info("Функция time_for_greeting возвращает 'Добрый день'")
        return "Добрый день"
    else:
        logger_utils.info("Функция time_for_greeting возвращает 'Добрый вечер'")
        return "Добрый вечер"


def get_data_time(date_time: str, date_format: str = "%Y-%m-%d %H:%M:%S") -> list[str]:
    """
    Функция возвращает период от начала месяца до выбранной даты в виде СПИСКА
    """
    logger_utils.debug(f"Вызвана функция get_data_time с аргументами {date_time}, {date_format}")

    dt = datetime.datetime.strptime(date_time, date_format)
    beginning_month = dt.replace(day=1)

    logger_utils.info(f"Функция возвращает период {beginning_month} - {dt}")
    return [beginning_month.strftime("%d.%m.%Y %H:%M:%S"), dt.strftime("%d.%m.%Y %H:%M:%S")]


def get_table_period(path_file: str, period: list) -> DataFrame:
    """
    Принимает путь к файлу Excel и период месяца и
    возвращает таблицу (DataFrame) в заданном периоде
    """
    logger_utils.debug(f"Вызвана функция get_table_period с аргументами {path_file}, {period}")

    try:
        df_excel = pd.read_excel(path_file, sheet_name="Отчет по операциям")

        # переводим тип строковые данные колонки "Дата операции" из таблицы excel в тип datetime
        df_excel["Дата операции"] = pd.to_datetime(df_excel["Дата операции"], dayfirst=True)

        # задаем начало и конец периода, взяв список дат из get_data_time
        if len(period) < 2:
            end_date = datetime.datetime.strptime(period[0], "%d.%m.%Y %H:%M:%S")
        else:
            beginning_date = datetime.datetime.strptime(period[0], "%d.%m.%Y %H:%M:%S")
            end_date = datetime.datetime.strptime(period[1], "%d.%m.%Y %H:%M:%S")

        # создаем отфильтрованную таблицу в диапазоне периода
        if len(period) < 2:
            df_filtered_excel = df_excel[df_excel["Дата операции"] <= end_date]
        else:
            df_filtered_excel = df_excel[
                (df_excel["Дата операции"] >= beginning_date) & (df_excel["Дата операции"] <= end_date)
            ]

        # сортируем отфильтрованную таблицу по возрастанию дат
        df_sorted = df_filtered_excel.sort_values(by="Дата операции")
        logger_utils.info("Файл успешно считан и функция возвращает отсортированную таблицу")
        return df_sorted
    except FileNotFoundError:
        logger_utils.error(f"Файл {path_file} не найден. Возвращается пустой DataFrame")
        return pd.DataFrame()
    except ValueError as ve:
        logger_utils.error(
            f"Ошибка в формате даты или пустой период для {path_file}: {ve}. Возвращается пустой DataFrame."
        )
    except Exception as e:
        logger_utils.error(f"Произошла ошибка при чтении файла {path_file}: {e}. Возвращается пустой список")
        return pd.DataFrame()


def get_cost_of_card(df_sorted: DataFrame) -> list[dict]:
    """
    Функция принимает отсортированную таблицу по периоде из функции get_table_period и
    возвращает список словаря, в котором хранятся
    последние 4 цифры карты, сумма затрат и общий кешбэк
    """
    logger_utils.debug(f"Вызвана функция get_table_period с аргументом {df_sorted}")
    # Необходимые колонки
    required_cols = ["Номер карты", "Сумма операции с округлением", "Кэшбэк", "Сумма операции"]
    for col in required_cols:
        if col not in df_sorted.columns:
            logger_utils.error(f"Отсутствует необходимая колонка '{col}' в DataFrame для get_top_transactions.")
            return []

    card_transactions = []
    card_sorted = df_sorted[
        [
            "Номер карты",
            "Сумма операции с округлением",
            "Кэшбэк",
            "Сумма операции",
        ]
    ]

    for index, row in card_sorted.iterrows():
        if row["Сумма операции"] < 0:
            last_digits = str(row["Номер карты"]).replace("*", "")
            total_spent = abs(round(row["Сумма операции с округлением"], 2))
            cashback = round(total_spent / 100, 2)
            card_info = {"last_digits": f"{last_digits}", "total_spent": total_spent, "cashback": cashback}
            card_transactions.append(card_info)

    logger_utils.info("Успешно записана информация по картам")
    return card_transactions


def get_top_transactions(df_sorted: DataFrame, number) -> list[dict]:
    """
    Функция принимает таблицу (DataFrame) и количество транзакций и
    возвращает указанное количество топ транзакций
    """
    logger_utils.info(f"Вызвана функция get_top_transactions с аргументами {df_sorted}, {number}")
    top_transactions = []

    # Необходимые колонки
    required_cols = ["Дата платежа", "Сумма операции", "Категория", "Описание"]
    for col in required_cols:
        if col not in df_sorted.columns:
            logger_utils.error(f"Отсутствует необходимая колонка '{col}' в DataFrame для get_top_transactions.")
            return []

    df_sorted_pay = df_sorted[df_sorted["Сумма операции"] < 0]
    df_sorted_pay = df_sorted_pay.sort_values(by="Сумма операции", ascending=True)
    # оставляем в выборке только number строк таблицы
    top_pay = df_sorted_pay.head(number)

    transactions = top_pay[["Дата платежа", "Сумма операции", "Категория", "Описание"]]

    for index, row in transactions.iterrows():
        top_info = {
            "date": row["Дата платежа"],
            "amount": row["Сумма операции"],
            "category": row["Категория"],
            "description": row["Описание"],
        }
        top_transactions.append(top_info)
    logger_utils.info("Успешно записана информация по транзакциям")
    return top_transactions


def get_currency_rates(path_json: str) -> list[dict]:
    """
    Функция принимает путь до json-файла и возвращает курс валют
    """
    logger_utils.info(f"Вызвана функция get_currency_rates с аргументом {path_json}")
    currency_rates = []
    try:
        with open(path_json, "r", encoding="utf-8") as f_cur:
            data = json.load(f_cur)
            if data is None:
                logger_utils.warning(f"Файл {path_json} является пустым. Возвращается пустой список")
                return []

            currencies = data["user_currencies"]

            for currency in currencies:
                API_KEY_CURRENCY = os.getenv("API_KEY_CURRENCY")
                rub = "RUB"
                headers = {"apikey": API_KEY_CURRENCY}
                if API_KEY_CURRENCY is None:
                    logger_utils.warning("Ошибка чтения API-ключа")
                    return []
                url = f"https://api.apilayer.com/exchangerates_data/convert?to={rub}&from={currency}&amount={1}"
                response = requests.get(url, headers=headers)

                status_code = response.status_code
                if status_code == 200:
                    result = response.json()
                    currency_info = {"currency": result["query"]["from"], "rate": round(result["result"], 2)}
                    currency_rates.append(currency_info)
        logger_utils.info("Успешно загружена информация о курсах валют")
        return currency_rates
    except json.JSONDecodeError:
        logger_utils.error(f"Некорректный формат JSON в файле {path_json}. Возвращается пустой список.")
        return []
    except FileNotFoundError:
        logger_utils.error(f"Ошибка чтении файла: файл {path_json} не найден")
        return []
    except Exception as e:
        logger_utils.error(
            f"Произошла непредвиденная ошибка при чтении файла {path_json}: {e}. Возвращается пустой список."
        )
        return []


def get_stock_prices(path_json: str) -> list[dict]:
    """
    Функция принимает путь до json-файла и возвращает цена на акции
    """
    logger_utils.info(f"Вызвана функция get_stock_prices с аргументом {path_json}")
    stock_prices = []
    try:
        with open(path_json, "r", encoding="utf-8") as f_st:
            data = json.load(f_st)
            if data is None:
                logger_utils.warning(f"Файл {path_json} является пустым. Возвращается пустой список")
                return []
            stocks = data["user_stocks"]
            day = date.today()
            yesterday = str(day - timedelta(days=1))

            for stock in stocks:
                API_KEY_STOCK = os.getenv("API_KEY_STOCK")
                if API_KEY_STOCK is None:
                    logger_utils.warning("Ошибка чтения API-ключа: ключ пустой))")
                    return []

                URL = f"https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={stock}&interval={10}min&apikey={API_KEY_STOCK}"
                response = requests.get(URL)

                status_code = response.status_code
                if status_code == 200:
                    result = response.json()
                    stock_info = {"stock": stock, "price": result["Weekly Time Series"][yesterday]["2. high"]}
                    stock_prices.append(stock_info)
        if stock_prices == []:
            logger_utils.warning("Ошибка записи информации об акциях. Возвращается пустой список")
            return []
        return stock_prices
    except json.JSONDecodeError:
        logger_utils.error(f"Некорректный формат JSON в файле {path_file}. Возвращается пустой список.")
        return []
    except FileNotFoundError:
        logger_utils.error(f"Ошибка чтении файла: файл {path_json} не найден")
    except Exception as e:
        logger_utils.error(
            f"Произошла непредвиденная ошибка при чтении файла {path_file}: {e}. Возвращается пустой список."
        )


# Функции для страницы "События"

def get_data_time_with_range(date_time: str, date_format: str = "%Y-%m-%d %H:%M:%S", range: str = "M") -> list[str]:
    """
    Функция принимает строку с датой, форматом и диапазон (по умолчанию месяц) и
    возвращает период времени с заданным диапазоном
    """

    logger_utils.debug(f"Вызвана функция get_data_time_with_range с аргументами {date_time}, {date_format}, {range}")
    dt = datetime.datetime.strptime(date_time, date_format)
    if range == "W":
        day_of_week = dt.weekday()
        # Вычисляем начало недели: вычитаем количество дней, прошедших с понедельника
        start_of_week = dt - timedelta(days=day_of_week)
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0)
        return [start_of_week.strftime("%d.%m.%Y %H:%M:%S"), dt.strftime("%d.%m.%Y %H:%M:%S")]
    elif range == "M":
        start_of_month = dt.replace(day=1, hour=0, minute=0, second=0)
        return [start_of_month.strftime("%d.%m.%Y %H:%M:%S"), dt.strftime("%d.%m.%Y %H:%M:%S")]
    elif range == "Y":
        start_of_year = dt.replace(month=1, day=1, hour=0, minute=0, second=0)
        return [start_of_year.strftime("%d.%m.%Y %H:%M:%S"), dt.strftime("%d.%m.%Y %H:%M:%S")]
    else:
        return [dt.strftime("%d.%m.%Y %H:%M:%S")]


def get_expenses(df_sorted: DataFrame) -> dict:
    """
    Функция принимает таблицу Dataframe и
    возвращает список общей суммы затрат, затрат по категориям
    """

    logger_utils.debug("Вызвана функция get_expenses с аргументами df_sorted")
    total_amount = 0
    category_expenses = []
    transfers_and_cash = []
    df_filtered = df_sorted[["Сумма операции", "Категория"]]

    # Находим общую сумму расходов (пополнения не учитываем)
    for index, row in df_filtered.iterrows():
        if row["Сумма операции"] < 0:
            total_amount += abs(row["Сумма операции"])

    # Находим список категорий
    list_of_categories = []
    transfers_and_cash_categories = []
    for index, row in df_filtered.iterrows():
        if (
            (row["Категория"] not in list_of_categories)
            and (row["Категория"] not in transfers_and_cash_categories)
            and (row["Сумма операции"] < 0)
        ):
            # добавляем все категории в список кроме "Переводы" и "Наличные"
            if row["Категория"] not in ["Переводы", "Наличные"]:
                list_of_categories.append(row["Категория"])
            else:
                transfers_and_cash_categories.append(row["Категория"])

    # Создаем список инфы расходов по категориям
    for category in list_of_categories:
        amount_of_category = 0
        for index, row in df_filtered.iterrows():
            if row["Сумма операции"] < 0:
                if category == row["Категория"]:
                    amount_of_category += row["Сумма операции"]
        category_dict = {"category": category, "amount": abs(round(amount_of_category, 2))}
        category_expenses.append(category_dict)

    category_expenses = sorted(category_expenses, key=lambda expensy: expensy["amount"], reverse=True)

    # Если кол-во категорий больше 7, то наименьшие траты попадают в категорию "Остальное"
    if len(category_expenses) > 7:
        other_category = category_expenses[7:]
        amount_other = sum(categ["amount"] for categ in other_category)
        other_category_dict = {"category": "Остальное", "amount": amount_other}
        category_expenses = category_expenses[:7]
        category_expenses.append(other_category_dict)

    # Создаем список инфы расходов "наличных" и "переводов"
    for category in transfers_and_cash_categories:
        amount_of_category = 0
        for index, row in df_filtered.iterrows():
            if row["Сумма операции"] < 0:
                if category == row["Категория"]:
                    amount_of_category += row["Сумма операции"]
        category_dict = {"category": category, "amount": abs(round(amount_of_category, 2))}
        transfers_and_cash.append(category_dict)

    transfers_and_cash = sorted(transfers_and_cash, key=lambda x: x["amount"], reverse=True)

    expenses = {
        "total_amount": round(total_amount, 2),
        "main": category_expenses,
        "transfers_and_cash": transfers_and_cash,
    }

    logger_utils.info("Успешно записана информация по затратам")
    return expenses


def get_income(df_sorted: DataFrame) -> dict:
    """
    Функция принимает таблицу (DataFrame) и
    возвращает поступления на карту
    """
    logger_utils.debug("Вызвана функция get_income с аргументами df_sorted")
    total_amount = 0
    category_income = []
    df_filtered = df_sorted[["Сумма операции", "Категория"]]

    for index, row in df_filtered.iterrows():
        if row["Сумма операции"] > 0:
            total_amount += abs(row["Сумма операции"])

    # Находим список категорий
    list_of_categories = []
    for index, row in df_filtered.iterrows():
        if (row["Категория"] not in list_of_categories) and (row["Сумма операции"] > 0):
            list_of_categories.append(row["Категория"])

    # Создаем список инфы расходов по категориям
    for category in list_of_categories:
        amount_of_category = 0
        for index, row in df_filtered.iterrows():
            if row["Сумма операции"] > 0:
                if category == row["Категория"]:
                    amount_of_category += row["Сумма операции"]
        category_dict = {"category": category, "amount": abs(amount_of_category)}
        category_income.append(category_dict)
    category_income = sorted(category_income, key=lambda x: x["amount"], reverse=True)

    income = {
        "total_amount": total_amount,
        "main": category_income,
    }

    return income


#  --- Функции для Сервисов ---

def get_transactions_for_investment(path: str)->list[dict[str, any]]:
    """
    Функция возвращает список словарей с полями датой и суммой операции
    """
    df = pd.read_excel(path)
    # Меняем строковый данные колонки "Дата операции" из Excel в datetime
    df["Дата операции"] = pd.to_datetime(df["Дата операции"],format="%d.%m.%Y %H:%M:%S").dt.date

    # создаем отфильтрованный df с затратами
    df_filtered = df[df["Сумма операции"] < 0]
    transactions = []
    for index, row in df_filtered.iterrows():
        transact_dict = {
            str(row["Дата операции"]): abs(row["Сумма операции"])
        }
        transactions.append(transact_dict)

    return transactions

