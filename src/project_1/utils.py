import datetime
from datetime import date, timedelta
import json
import os

import requests
import pandas as pd
from pandas import DataFrame

from dotenv import load_dotenv
load_dotenv(".env")

path_file = os.path.join('..', '..', 'data', 'operations.xlsx')
path_json = os.path.join('..', '..', 'data', 'user_settings.json')


def time_for_greeting()->str:
    '''Функция приветствия относительно текущего часа'''
    now = datetime.datetime.now()
    current_now = now.hour
    if current_now >= 0 and current_now < 4:
        return 'Доброй ночи'
    elif current_now >= 4 and current_now < 12:
        return 'Доброе утро'
    elif current_now >= 12 and current_now < 17:
        return 'Добрый день'
    else:
        return 'Добрый вечер'


def get_data_time(date_time: str, date_format: str="%Y-%m-%d %H:%M:%S")->list[str]:
    '''
    Функция возвращает период от начала месяца до выбранной даты в виде СПИСКА
    '''
    dt = datetime.datetime.strptime(date_time, date_format)
    beginning_month = dt.replace(day=1)

    return [
        beginning_month.strftime("%d.%m.%Y %H:%M:%S"),
        dt.strftime("%d.%m.%Y %H:%M:%S")
    ]


def get_period(path_file: str, period: list)->DataFrame:
    '''
    Принимает путь к файлу Excel и списку дат и
    возвращает таблицу (DataFrame) в заданном периоде
    '''
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

    return df_sorted


def get_cost_of_card(df_sorted: DataFrame)->list[dict]:
    '''
    Функция принимает отсортированную таблицу по периоде из функции get_period и
    возвращает список словаря, в котором хранятся
    последние 4 цифры карты, сумма затрат и общий кешбэк
    '''
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

    return card_transactions


def get_top_transactions(df_sorted: DataFrame, number)->list[dict]:
    '''
    Функция принимает таблицу (DataFrame) и количество транзакций и
    возвращает указанное количество топ транзакций
    '''
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

    return top_transactions


def get_currency_rates(path_json: str)->list[dict]:
    '''
    Функция принимает путь до json-файла и возвращает курс валют
    '''
    currency_rates = []
    with open(path_json, 'r', encoding='utf-8') as f_cur:
        data = json.load(f_cur)
        currencies = data['user_currencies']

        for currency in currencies:
            API_KEY_CURRENCY = os.getenv("API_KEY_CURRENCY")
            rub = "RUB"
            headers = {
                'apikey': API_KEY_CURRENCY
            }
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
    return currency_rates


def get_stock_prices(path_json: str)->list[dict]:
    '''
    Функция принимает путь до json-файла и возвращает цена на акции
    '''
    stock_prices = []
    with open(path_json, 'r', encoding='utf-8') as f_st:
        data = json.load(f_st)
        stocks = data['user_stocks']
        day = date.today()
        yesterday = str(day - timedelta(days=1))

        for stock in stocks:
            API_KEY_STOCK = os.getenv('API_KEY_STOCK')
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
    return stock_prices


