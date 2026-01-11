import json
from typing import Any, Dict

from project_1.utils import (get_cost_of_card, get_currency_rates,
                             get_data_time, get_data_time_with_range,
                             get_expenses, get_income, get_stock_prices,
                             get_table_period, get_top_transactions, path_json,
                             time_for_greeting)


def main_info(date_time: str) -> Dict[str, Any]:
    """
    Принимает на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS
    и возвращает JSON-ответ
    """
    greeting = time_for_greeting()

    time_period = get_data_time(date_time)
    sorted_df = get_table_period("../../data/operations.xlsx", time_period)

    cards = get_cost_of_card(sorted_df)
    top_transactions = get_top_transactions(sorted_df, 5)
    currency_rates = get_currency_rates(path_json)
    stock_prices = get_stock_prices(path_json)

    data = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
    json_data = json.dumps(data, ensure_ascii=False, indent=4)
    return json_data


def even_info(date_time: str, range: str = "M") -> Dict[str, Any]:
    """
    Принимает на вход строку с датой и диапазоном времени (необязательно) и возвращает
    JSON-ответ
    """
    time_period = get_data_time_with_range(date_time, range=range)
    sorted_df = get_table_period("../../data/operations.xlsx", period=time_period)

    expenses = get_expenses(sorted_df)
    income = get_income(sorted_df)
    currency_rates = get_currency_rates(path_json)
    stock_prices = get_stock_prices(path_json)

    data = {"expenses": expenses, "income": income, "currency_rates": currency_rates, "stock_prices": stock_prices}

    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    return json_data


# print(even_info("2018-01-01 12:49:53"))
