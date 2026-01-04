import json
import os.path

import pandas as pd
import re
from project_1.utils import path_file
from src.project_1.utils import get_transactions_for_investment

def profitable_cashback(path_file: str, year: int, month: int)-> str:
    """
    Выдает информацию о выгодных категориях кешбэка
    """
    df = pd.read_excel(path_file)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    df_filtered = df[
        (df["Дата операции"].dt.year == year)
        &
        (df["Дата операции"].dt.month == month)
    ]
    df_filtered = df_filtered[df_filtered["Кэшбэк"] > 0]
    df_filtered = df_filtered[df_filtered["Сумма платежа"] < 0]

    expenses_categories = df_filtered.groupby("Категория")["Сумма платежа"].sum()
    cashback_categories = abs(expenses_categories) // 100

    result = cashback_categories.to_dict()
    return json.dumps(result, ensure_ascii=False, indent=4)

#print(profitable_cashback(path_file, 2018, 4))

#investment_transactions = [{'2018-01-03': 73.06}, {'2018-01-03': 21.0}, {'2018-01-01': 316.0}, {'2018-01-01': 3000.0}]

def investment_bank(month: str, transactions: list[dict[str, any]], limit: int)->float:
    """
    Функция позволяет копить через округления трат с учетом порогом округления
    """
    filtered_transactions = []
    for transaction in transactions:
        if month in str(transaction.keys()):
            filtered_transactions.append(transaction)

    amount_of_savings = 0.0
    for transaction in filtered_transactions:
        if (float(str(*transaction.values())) % limit) != 0:
            amount = limit - (float(str(*transaction.values())) % limit)
            amount_of_savings += amount

    return round(amount_of_savings, 2)


def simple_search(search_str: str)->list:
    """
    Выдает JSON-ответ со всеми транзакциями, содержащими в запрос
    """
    df = pd.read_excel(path_file)
    df_cleaned = df.dropna(subset=['Категория'])
    search_df = []
    for index, row in df_cleaned.iterrows():
        if (search_str in str(row["Категория"])) or (search_str in str(row["Описание"])):
            dict_tr = {
                'Дата операции': row['Дата операции'],
                'Дата платежа': row['Дата платежа'],
                'Номер карты': row['Номер карты'],
                'Статус': row['Статус'],
                'Сумма операции': row['Сумма операции'],
                'Валюта операции': row['Валюта операции'],
                'Сумма платежа': row['Сумма платежа'],
                'Валюта платежа': row['Валюта платежа'],
                'Кэшбэк': row['Кэшбэк'],
                'Категория': row['Категория'],
                'Описание': row['Описание'],
                'Округление на инвесткопилку': row['Округление на инвесткопилку'],
                'Сумма операции с округлением': row['Сумма операции с округлением']
            }
            search_df.append(dict_tr)
    result = json.dumps(search_df, ensure_ascii=False, indent=4)
    return result


def phone_search(search_str: str)->list[dict]:
    """
    Выдает JSON-ответ со всеми транзакциями, содержащими в запросе номер телефона
    """
    phon_pattern = r"[\+\d][\d\s\(\)\-]{10,}"
    phone_desc = re.findall(phon_pattern, search_str)
    str_phone_desc = str(phone_desc).replace("[", "").replace("]", "")
    str_phone_desc = str_phone_desc.strip("'")

    df = pd.read_excel(path_file)
    phone_df = []
    for index, row in df.iterrows():
        if str_phone_desc in str(row["Описание"]):
            dict_tr = {
                'Дата операции': row['Дата операции'],
                'Дата платежа': row['Дата платежа'],
                'Номер карты': row['Номер карты'],
                'Статус': row['Статус'],
                'Сумма операции': row['Сумма операции'],
                'Валюта операции': row['Валюта операции'],
                'Сумма платежа': row['Сумма платежа'],
                'Валюта платежа': row['Валюта платежа'],
                'Кэшбэк': row['Кэшбэк'],
                'Категория': row['Категория'],
                'Описание': row['Описание'],
                'Округление на инвесткопилку': row['Округление на инвесткопилку'],
                'Сумма операции с округлением': row['Сумма операции с округлением']
            }
            phone_df.append(dict_tr)
    result = json.dumps(phone_df, ensure_ascii=False, indent=4)
    return result


def name_search(search_str: str)->list[dict]:
    """
    Функция возвращает JSON со всеми транзакциями, которые относятся к переводам физлицам
    """
    name_pattern = r"[A-Яа-яA-Za-z]+\s[A-ЯA-Z]\."
    name_desc = re.findall(name_pattern, search_str)
    str_name_desc = str(name_desc).replace("[", "").replace("]", "")
    str_name_desc = str_name_desc.strip("'")

    df = pd.read_excel(path_file)
    df_cleaned = df.dropna(subset=['Категория'])
    name_df = []
    for index, row in df_cleaned.iterrows():
        if (str(row["Категория"]) == "Переводы") and (str_name_desc in str(row["Описание"])):
            dict_tr = {
                'Дата операции': row['Дата операции'],
                'Дата платежа': row['Дата платежа'],
                'Номер карты': row['Номер карты'],
                'Статус': row['Статус'],
                'Сумма операции': row['Сумма операции'],
                'Валюта операции': row['Валюта операции'],
                'Сумма платежа': row['Сумма платежа'],
                'Валюта платежа': row['Валюта платежа'],
                'Кэшбэк': row['Кэшбэк'],
                'Категория': row['Категория'],
                'Описание': row['Описание'],
                'Округление на инвесткопилку': row['Округление на инвесткопилку'],
                'Сумма операции с округлением': row['Сумма операции с округлением']
            }
            name_df.append(dict_tr)
    result = json.dumps(name_df, ensure_ascii=False, indent=4)
    return result

