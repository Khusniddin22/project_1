import json

from typing import Dict, Any

from project_1.utils import (
    time_for_greeting,
    get_data_time,
    get_table_period,
    get_cost_of_card,
    get_top_transactions,
    get_currency_rates,
    get_stock_prices,
    get_expenses,
    get_income,
    path_json, get_data_time_with_range
)


def main_info(date_time: str)->Dict[str, Any]:
    '''
    Принимает на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS
    и возвращает JSON-ответ
    '''
    greeting = time_for_greeting()

    time_period = get_data_time(date_time)
    sorted_df = get_table_period("../../data/operations.xlsx", time_period)

    cards = get_cost_of_card(sorted_df)
    top_transactions = get_top_transactions(sorted_df, 5)
    currency_rates = get_currency_rates(path_json)
    stock_prices = get_stock_prices(path_json)

    data = {
        'greeting': greeting,
        'cards': cards,
        'top_transactions': top_transactions,
        'currency_rates': currency_rates,
        'stock_prices': stock_prices
    }
    json_data = json.dumps(data, ensure_ascii=False, indent=4)


    print(time_period)

main_info("2018-05-20 15:30:00")

def even_info(date_time: str, range: str="Y")->Dict[str, Any]:
    '''
    Принимает на вход строку с датой и диапазоном времени (необязательно) и возвращает
    JSON-ответ
    '''
    time_period = get_data_time_with_range(date_time, range=range)
    sorted_df = get_table_period("../../data/operations.xlsx", period=time_period)
    expenses = get_expenses(sorted_df)
    income = get_income(sorted_df)
    currency_rates = get_currency_rates(path_json)
    stock_prices = get_stock_prices(path_json)
    data = {
        'expenses': expenses,
        'income': income,
        'currency_rates': currency_rates,
        'stock_prices': stock_prices
    }

    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    return json_data

