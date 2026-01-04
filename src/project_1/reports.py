import json
from datetime import date, timedelta, datetime

import time

import pandas as pd
from typing import Optional

from project_1.utils import get_data_time, get_last_three_month, get_df_transactions, path_file


def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None)->str:
    """
    Функция возвращает траты по заданной категории за последние три месяца (от переданной даты)
    """
    if date is None:
        to_day = time.strftime("%d.%m.%Y %H:%M:%S")
    else:
        to_day = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    end_date = to_day.strftime("%d.%m.%Y %H:%M:%S")

    starting_date = get_last_three_month(str(to_day))
    starting_date = starting_date.strftime("%d.%m.%Y %H:%M:%S")

    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)
    filtered_transactions = transactions[
        (transactions["Дата операции"] >= starting_date) &
        (transactions["Дата операции"] <= end_date)
    ]
    sort_transactions = filtered_transactions[filtered_transactions["Категория"] == category]
    json_string = sort_transactions.to_json(orient='records', force_ascii=False, indent=4, date_format='iso')
    return json_string

df = get_df_transactions(path_file)

#print(spending_by_category(df, "Ж/д билеты", "2018-05-20 00:00:00"))


def spending_by_weekday(transactions: pd.DataFrame,
                        date: Optional[str] = None):
    """
        Функция возвращает средние траты в каждый из дней недели за последние три месяца (от переданной даты)
    """
    if date is None:
        to_day = time.strftime("%d.%m.%Y %H:%M:%S")
    else:
        to_day = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    end_date = to_day.strftime("%d.%m.%Y %H:%M:%S")

    starting_date = get_last_three_month(str(to_day))
    starting_date = starting_date.strftime("%d.%m.%Y %H:%M:%S")

    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    filtered_transactions = transactions[
        (transactions["Дата операции"] >= starting_date) &
        (transactions["Дата операции"] <= end_date)
        ]

    sort_transactions = filtered_transactions[filtered_transactions["Сумма операции"] < 0].copy()
    sort_transactions["День недели"] = sort_transactions["Дата операции"].dt.day_name()
    counts = sort_transactions["День недели"].value_counts()
    counts_dict = counts.sort_index()

    result = sort_transactions.groupby("День недели")["Сумма операции"].sum()
    result_dict = result.to_dict()

    for key in result_dict.keys():
        result_dict[key] = abs(round((result_dict[key] / counts_dict[key]), 2))

    json_str = json.dumps(result_dict, ensure_ascii=False, indent=4)

    return json_str


#print(spending_by_weekday(df, "2018-05-20 00:00:00"))


def spending_by_workday(transactions: pd.DataFrame,
                        date: Optional[str] = None) -> str:
    """
        Функция выводит средние траты в рабочий и в выходной день за последние три месяца
    """
    if date is None:
        to_day = time.strftime("%d.%m.%Y %H:%M:%S")
    else:
        to_day = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    end_date = to_day.strftime("%d.%m.%Y %H:%M:%S")

    starting_date = get_last_three_month(str(to_day))
    starting_date = starting_date.strftime("%d.%m.%Y %H:%M:%S")

    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    filtered_transactions = transactions[
        (transactions["Дата операции"] >= starting_date) &
        (transactions["Дата операции"] <= end_date)
        ]

    sort_transactions = filtered_transactions[filtered_transactions["Сумма операции"] < 0].copy()
    sort_transactions["День недели"] = sort_transactions["Дата операции"].dt.day_name()
    workday_weekend = []

    for index, row in sort_transactions.iterrows():
        if row["День недели"] in ("Saturday", "Sunday"):
            workday_weekend.append("Weekend")
        else:
            workday_weekend.append("Workday")

    sort_transactions["Work/weekend"] = workday_weekend
    counts = sort_transactions["Work/weekend"].value_counts()
    counts_dict = counts.sort_index()

    result = sort_transactions.groupby("Work/weekend")["Сумма операции"].sum()
    result_dict = result.to_dict()

    for key in result_dict.keys():
        result_dict[key] = abs(round((result_dict[key] / counts_dict[key]), 2))

    json_str = json.dumps(result_dict, ensure_ascii=False, indent=4)

    return json_str

#print(spending_by_workday(df, "2018-05-20 00:00:00"))