import json
import logging
import os.path
import re

import pandas as pd

from project_1.utils import path_file
from src.project_1.utils import get_transactions_for_investment

logger_services = logging.getLogger("services")
logger_services.setLevel(logging.DEBUG)  # Устанавливаем уровень логирования
os.makedirs("logs", exist_ok=True)
file_handler = logging.FileHandler("logs/utils.log")  # Указываем путь к файлу с логами
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger_services.addHandler(file_handler)


def profitable_cashback(path_file: str, year: int, month: int) -> str:
    """
    Выдает информацию о выгодных категориях кешбэка
    """
    logger_services.debug(f"Вызвана функция profitable_cashback с аргументами {path_file}, {year}, {month}")
    try:
        df = pd.read_excel(path_file)
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        df_filtered = df[(df["Дата операции"].dt.year == year) & (df["Дата операции"].dt.month == month)]
        df_filtered = df_filtered[df_filtered["Кэшбэк"] > 0]
        df_filtered = df_filtered[df_filtered["Сумма платежа"] < 0]

        expenses_categories = df_filtered.groupby("Категория")["Сумма платежа"].sum()
        cashback_categories = abs(expenses_categories) // 100

        result = cashback_categories.to_dict()
        logger_services.info("Файл успешно считан и функция возвращает JSON-строку")
        return json.dumps(result, ensure_ascii=False, indent=4)
    except FileNotFoundError:
        logger_services.error(f"Файл {path_file} не найден. Возвращается пустая строка")
        return ""
    except Exception as e:
        logger_services.error(f"Произошла ошибка при чтении файла {path_file}: {e}. Возвращается пустая строка")
        return ""


# print(profitable_cashback(path_file, 2018, 4))

# investment_transactions = [{'2018-01-03': 73.06}, {'2018-01-03': 21.0}, {'2018-01-01': 316.0}, {'2018-01-01': 3000.0}]


def investment_bank(month: str, transactions: list[dict[str, any]], limit: int) -> float:
    """
    Функция позволяет копить через округления трат с учетом порогом округления
    """
    logger_services.info("Вызвана функция investment_bank")
    if transactions == []:
        logger_services.error("Передана пустой список транзакций. Возвращается None")
        return None

    filtered_transactions = []
    for transaction in transactions:
        if month in str(transaction.keys()):
            filtered_transactions.append(transaction)

    amount_of_savings = 0.0
    for transaction in filtered_transactions:
        if (float(str(*transaction.values())) % limit) != 0:
            amount = limit - (float(str(*transaction.values())) % limit)
            amount_of_savings += amount

    logger_services.info(f"Функция investment_bank успешно выполнена")
    return round(amount_of_savings, 2)


def simple_search(search_str: str) -> list:
    """
    Выдает JSON-ответ со всеми транзакциями, содержащими в запрос
    """
    logger_services.info(f"Вызвана функция simple_search со строкой {search_str}")
    if search_str == "":
        logger_services.error("Передана пустая строка. Возвращается пустой список")
        return []

    if type(search_str) != str:
        logger_services.error("Неправильный тип поиска строки. Возвращается пустой список")
        return []

    df = pd.read_excel(path_file)
    df_cleaned = df.dropna(subset=["Категория"])
    search_df = []
    for index, row in df_cleaned.iterrows():
        if (search_str in str(row["Категория"])) or (search_str in str(row["Описание"])):
            dict_tr = {
                "Дата операции": row["Дата операции"],
                "Дата платежа": row["Дата платежа"],
                "Номер карты": row["Номер карты"],
                "Статус": row["Статус"],
                "Сумма операции": row["Сумма операции"],
                "Валюта операции": row["Валюта операции"],
                "Сумма платежа": row["Сумма платежа"],
                "Валюта платежа": row["Валюта платежа"],
                "Кэшбэк": row["Кэшбэк"],
                "Категория": row["Категория"],
                "Описание": row["Описание"],
                "Округление на инвесткопилку": row["Округление на инвесткопилку"],
                "Сумма операции с округлением": row["Сумма операции с округлением"],
            }
            search_df.append(dict_tr)
    result = json.dumps(search_df, ensure_ascii=False, indent=4)

    logger_services.info(f"Функция simple_search успешна выполнена")
    return result


def phone_search(search_str: str) -> list[dict]:
    """
    Выдает JSON-ответ со всеми транзакциями, содержащими в запросе номер телефона
    """
    logger_services.info(f"Вызвана функция phone_search со строкой {search_str}")
    if search_str == "":
        logger_services.error("Передана пустая строка. Возвращается пустой список")
        return []

    if type(search_str) != str:
        logger_services.error("Неправильный тип поиска строки. Возвращается пустой список")
        return []

    phon_pattern = r"[\+\d][\d\s\(\)\-]{10,}"
    phone_desc = re.findall(phon_pattern, search_str)
    str_phone_desc = str(phone_desc).replace("[", "").replace("]", "")
    str_phone_desc = str_phone_desc.strip("'")

    df = pd.read_excel(path_file)
    phone_df = []
    for index, row in df.iterrows():
        if str_phone_desc in str(row["Описание"]):
            dict_tr = {
                "Дата операции": row["Дата операции"],
                "Дата платежа": row["Дата платежа"],
                "Номер карты": row["Номер карты"],
                "Статус": row["Статус"],
                "Сумма операции": row["Сумма операции"],
                "Валюта операции": row["Валюта операции"],
                "Сумма платежа": row["Сумма платежа"],
                "Валюта платежа": row["Валюта платежа"],
                "Кэшбэк": row["Кэшбэк"],
                "Категория": row["Категория"],
                "Описание": row["Описание"],
                "Округление на инвесткопилку": row["Округление на инвесткопилку"],
                "Сумма операции с округлением": row["Сумма операции с округлением"],
            }
            phone_df.append(dict_tr)
    result = json.dumps(phone_df, ensure_ascii=False, indent=4)

    logger_services.info(f"Функция phone_search успешна выполнена")
    return result


def name_search(path_file: str, search_str: str) -> str:
    """
    Функция возвращает JSON со всеми транзакциями, которые относятся к переводам физлицам
    """
    name_pattern = r"[A-Яа-яA-Za-z]+\s[A-ЯA-Z]\."
    name_matches = re.findall(name_pattern, search_str)

    if not name_matches:
        logger_services.warning(f"Имя не найдено в строке поиска: {search_str}")
        return json.dumps([], ensure_ascii=False)

    str_name_desc = name_matches[0]

    try:
        df = pd.read_excel(path_file)
        mask = (df["Категория"] == "Переводы") & (df["Описание"].str.contains(str_name_desc, na=False, regex=False))
        filtered_df = df[mask]

        result_list = filtered_df.to_dict(orient="records")
        result = json.dumps(result_list, ensure_ascii=False, indent=4)

        logger_services.info(f"Функция name_search успешно выполнена")
        return result

    except Exception as e:
        logger_services.error(f"Ошибка в name_search: {e}")
        return json.dumps([], ensure_ascii=False)
