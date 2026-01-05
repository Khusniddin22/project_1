import functools
import json
import logging
import os
import time
from datetime import datetime
from typing import Optional

import pandas as pd

from project_1.utils import (get_data_time, get_df_transactions,
                             get_last_three_month, path_file)

logger_reports = logging.getLogger("reports")
logger_reports.setLevel(logging.DEBUG)  # Устанавливаем уровень логирования
os.makedirs("logs", exist_ok=True)
file_handler = logging.FileHandler("logs/utils.log")  # Указываем путь к файлу с логами
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger_reports.addHandler(file_handler)


# Декоратор без параметра
def log_to_file(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        # Формируем запись
        with open("report.txt", "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] Функция: {func.__name__} | Аргументы: {args}, {kwargs} | Результат: {result}\n")
        return result

    return wrapper


# Декоратор с параметром
def log_to_custom_file(filename):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            with open(filename, "a", encoding="utf-8") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] Функция: {func.__name__} | Результат: {result}\n")
            return result

        return wrapper

    return decorator


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> str:
    """
    Функция возвращает траты по заданной категории за последние три месяца (от переданной даты)
    """
    logger_reports.info(f"Вызвана функция spending_by_category с аргументами {transactions, category, date}")

    if transactions.empty:
        logger_reports.error("Ошибка чтения данных из DataFrame. Он пуст")
        return "Нет данных"

    if date is None:
        to_day = time.strftime("%d.%m.%Y %H:%M:%S")
    else:
        to_day = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    end_date = to_day.strftime("%d.%m.%Y %H:%M:%S")

    starting_date = get_last_three_month(str(to_day))
    starting_date = starting_date.strftime("%d.%m.%Y %H:%M:%S")

    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)
    filtered_transactions = transactions[
        (transactions["Дата операции"] >= starting_date) & (transactions["Дата операции"] <= end_date)
    ]
    sort_transactions = filtered_transactions[filtered_transactions["Категория"] == category]
    json_string = sort_transactions.to_json(orient="records", force_ascii=False, indent=4, date_format="iso")

    logger_reports.info("Функция spending_by_category успешно выполнена")
    return json_string


# df = get_df_transactions(path_file)

# print(spending_by_category(df, "Ж/д билеты", "2018-05-20 00:00:00"))


def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> str:
    """
    Функция возвращает средние траты в каждый из дней недели
    за последние три месяца (от переданной даты)
    """
    logger_reports.info(f"Вызвана функция spending_by_weekday с аргументами {transactions, date}")

    if transactions.empty:
        logger_reports.error("Ошибка чтения данных из DataFrame. Он пуст")
        return "Нет данных"

    if date is None:
        to_day = time.strftime("%d.%m.%Y %H:%M:%S")
    else:
        to_day = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    end_date = to_day.strftime("%d.%m.%Y %H:%M:%S")
    starting_date = get_last_three_month(str(to_day))
    starting_date = starting_date.strftime("%d.%m.%Y %H:%M:%S")

    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    filtered_transactions = transactions[
        (transactions["Дата операции"] >= starting_date) & (transactions["Дата операции"] <= end_date)
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

    logger_reports.info("Функция spending_by_weekday успешно выполнена")
    return json_str


# print(spending_by_weekday(df, "2018-05-20 00:00:00"))


def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> str:
    """
    Функция выводит средние траты в рабочий и в выходной день за последние три месяца
    """
    logger_reports.info(f"Вызвана функция spending_by_workday с аргументами {transactions, date}")

    if transactions.empty:
        logger_reports.error("Ошибка чтения данных из DataFrame. Он пуст")
        return "Нет данных"

    if date is None:
        to_day = datetime.now()
    else:
        to_day = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

    starting_date = get_last_three_month(str(to_day))
    end_date = to_day

    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    filtered_transactions = transactions[
        (transactions["Дата операции"] >= starting_date) & (transactions["Дата операции"] <= end_date)
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

    logger_reports.info("Функция spending_by_workday успешно выполнена")
    return json_str


# print(spending_by_workday(df, "2018-05-20 00:00:00"))
