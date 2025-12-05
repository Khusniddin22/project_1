import datetime
from datetime import date, timedelta
import json
import os
import logging
from multiprocessing.util import DEBUG

import requests
import pandas as pd
from pandas import DataFrame

from dotenv import load_dotenv
load_dotenv(".env")

logger_utils = logging.getLogger("utils")
logger_utils.setLevel(logging.DEBUG) #Устанавливаем уровень логирования
os.makedirs("logs", exist_ok=True)
file_handler = logging.FileHandler("logs/utils.log") #Указываем путь к файлу с логами
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger_utils.addHandler(file_handler) #Добавляем обработчик к логгеру


path_file = os.path.join('..', '..', 'data', 'operations.xlsx')
path_json = os.path.join('..', '..', 'data', 'user_settings.json')


def time_for_greeting()->str:
    '''Функция приветствия относительно текущего часа'''
    logger_utils.info(f"Вызвана функция time_for_greeting без аргумента")

    now = datetime.datetime.now()
    current_now = now.hour
    if current_now >= 0 and current_now < 4:
        logger_utils.info(f"Функция time_for_greeting возвращает 'Доброй ночи'")
        return 'Доброй ночи'
    elif current_now >= 4 and current_now < 12:
        logger_utils.info(f"Функция time_for_greeting возвращает 'Доброе утро'")
        return 'Доброе утро'
    elif current_now >= 12 and current_now < 17:
        logger_utils.info(f"Функция time_for_greeting возвращает 'Добрый день'")
        return 'Добрый день'
    else:
        logger_utils.info(f"Функция time_for_greeting возвращает 'Добрый вечер'")
        return 'Добрый вечер'


def get_data_time(date_time: str, date_format: str="%Y-%m-%d %H:%M:%S")->list[str]:
    '''
    Функция возвращает период от начала месяца до выбранной даты в виде СПИСКА
    '''
    logger_utils.debug(f"Вызвана функция get_data_time с аргументами {date_time}, {date_format}")

    dt = datetime.datetime.strptime(date_time, date_format)
    beginning_month = dt.replace(day=1)

    logger_utils.info(f"Функция возвращает период {beginning_month} - {dt}")
    return [
        beginning_month.strftime("%d.%m.%Y %H:%M:%S"),
        dt.strftime("%d.%m.%Y %H:%M:%S")
    ]


def get_table_period(path_file: str, period: list)->DataFrame:
    '''
    Принимает путь к файлу Excel и период месяца и
    возвращает таблицу (DataFrame) в заданном периоде
    '''
    logger_utils.debug(f"Вызвана функция get_table_period с аргументами {path_file}, {period}")

    try:
        df_excel = pd.read_excel(path_file, sheet_name='Отчет по операциям')

        #переводим тип строковые данные колонки "Дата операции" из таблицы excel в тип datetime
        df_excel['Дата операции'] = pd.to_datetime(df_excel['Дата операции'], dayfirst=True)

        #задаем начало и конец периода, взяв список дат из get_data_time
        beginning_date = datetime.datetime.strptime(period[0], "%d.%m.%Y %H:%M:%S")
        end_date = datetime.datetime.strptime(period[1], "%d.%m.%Y %H:%M:%S")

        #создаем отфильтрованную таблицу в диапазоне периода
        df_filetered_excel = df_excel[
            (df_excel['Дата операции'] >= beginning_date) &
            (df_excel['Дата операции'] <= end_date)
        ]

        #сортируем отфильтрованную таблицу по возрастанию дат
        df_sorted = df_filetered_excel.sort_values(by='Дата операции')
        logger_utils.info(f"Файл успешно считан и функция возвращает отсортированную таблицу")
        return df_sorted
    except FileNotFoundError:
        logger_utils.error(f"Файл {path_file} не найден. Возвращается пустой список")
        return []
    except Exception as e:
        logger_utils.error(f"Произошла ошибка при чтении файла {path_file}: {e}. Возвращается пустой список")


def get_cost_of_card(df_sorted: DataFrame)->list[dict]:
    '''
    Функция принимает отсортированную таблицу по периоде из функции get_table_period и
    возвращает список словаря, в котором хранятся
    последние 4 цифры карты, сумма затрат и общий кешбэк
    '''
    logger_utils.debug(f"Вызвана функция get_table_period с аргументом {df_sorted}")
    card_transactions = []
    card_sorted = df_sorted[
        [
            'Номер карты',
            'Сумма операции с округлением',
            'Кэшбэк',
            'Сумма операции',
        ]
    ]

    for index, row in card_sorted.iterrows():
        if row['Сумма операции'] < 0:
            last_digits = str(row['Номер карты']).replace('*', '')
            total_spent = row['Сумма операции с округлением']
            cashback = total_spent / 100
            card_info = {
                'last_digits': f'{last_digits}',
                'total_spent': f'{total_spent}',
                'cashback': f'{cashback}'
            }
            card_transactions.append(card_info)

    logger_utils.info(f"Успешно записана информация по картам")
    return card_transactions


def get_top_transactions(df_sorted: DataFrame, number)->list[dict]:
    '''
    Функция принимает таблицу (DataFrame) и количество транзакций и
    возвращает указанное количество топ транзакций
    '''
    logger_utils.info(f"Вызвана функция get_top_transactions с аргументами {df_sorted}, {number}")
    top_transactions = []
    df_sorted_pay = df_sorted.sort_values(by='Сумма операции', ascending=False)

    #оставляем в выборке только number строк таблицы
    top_pay = df_sorted_pay.head(number)

    transactions = top_pay[
        [
            'Дата платежа',
            'Сумма операции',
            'Категория',
            'Описание'
        ]
    ]

    for index, row in transactions.iterrows():
        top_info = {
            'date': row['Дата платежа'],
            'amount': row['Сумма операции'],
            'category': row['Категория'],
            'description': row['Описание']
        }
        top_transactions.append(top_info)

    logger_utils.info(f"Успешно записана информация по транзакциям")
    return top_transactions


def get_currency_rates(path_json: str)->list[dict]:
    '''
    Функция принимает путь до json-файла и возвращает курс валют
    '''
    logger_utils.info(f"Вызвана функция get_currency_rates с аргументом {path_json}")
    currency_rates = []
    try:
        with open(path_json, 'r', encoding='utf-8') as f_cur:
            data = json.load(f_cur)
            if data is None:
                logger_utils.warning(f"Файл {path_json} является пустым. Возвращается пустой список")
                return []

            currencies = data['user_currencies']

            for currency in currencies:
                API_KEY_CURRENCY = os.getenv("API_KEY_CURRENCY")
                rub = "RUB"
                headers = {
                    'apikey': API_KEY_CURRENCY
                }
                if API_KEY_CURRENCY is None:
                    logger_utils.warning(f"Ошибка чтения API-ключа")
                    return []
                url = f"https://api.apilayer.com/exchangerates_data/convert?to={rub}&from={currency}&amount={1}"
                response = requests.get(url, headers=headers)

                status_code = response.status_code
                if status_code == 200:
                    result = response.json()
                    currency_info = {
                        "currency": result['query']['from'],
                        "rate": round(result['result'], 2)
                    }
                    currency_rates.append(currency_info)
        logger_utils.info(f"Успешно загружена информация о курсах валют")
        return currency_rates
    except json.JSONDecodeError:
        logger_utils.error(f"Некорректный формат JSON в файле {path_file}. Возвращается пустой список.")
        return []
    except FileNotFoundError:
        logger_utils.error(f"Ошибка чтении файла: файл {path_json} не найден")
    except Exception as e:
        logger_utils.error(f"Произошла непредвиденная ошибка при чтении файла {path_file}: {e}. Возвращается пустой список.")


def get_stock_prices(path_json: str)->list[dict]:
    '''
    Функция принимает путь до json-файла и возвращает цена на акции
    '''
    logger_utils.info(f"Вызвана функция get_stock_prices с аргументом {path_json}")
    stock_prices = []
    try:
        with open(path_json, 'r', encoding='utf-8') as f_st:
            data = json.load(f_st)
            if data is None:
                logger_utils.warning(f"Файл {path_json} является пустым. Возвращается пустой список")
                return []
            stocks = data['user_stocks']
            day = date.today()
            yesterday = str(day - timedelta(days=1))

            for stock in stocks:
                API_KEY_STOCK = os.getenv('API_KEY_STOCK')
                if API_KEY_STOCK is None:
                    logger_utils.warning(f"Ошибка чтения API-ключа: ключ пустой))")
                    return []

                URL = f'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={stock}&interval={10}min&apikey={API_KEY_STOCK}'
                response = requests.get(URL)

                status_code = response.status_code
                if status_code == 200:
                    result = response.json()
                    stock_info = {
                        "stock": stock,
                        "price": result['Weekly Time Series'][yesterday]['2. high']
                    }
                    stock_prices.append(stock_info)
        if stock_prices == []:
            logger_utils.warning(f"Ошибка записи информации об акциях. Возвращается пустой список")
            return []
        return stock_prices
    except json.JSONDecodeError:
        logger_utils.error(f"Некорректный формат JSON в файле {path_file}. Возвращается пустой список.")
        return []
    except FileNotFoundError:
        logger_utils.error(f"Ошибка чтении файла: файл {path_json} не найден")
    except Exception as e:
        logger_utils.error(
            f"Произошла непредвиденная ошибка при чтении файла {path_file}: {e}. Возвращается пустой список.")
