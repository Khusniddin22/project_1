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
    path_json
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
        # 'cards': cards,
        # 'top_transactions': top_transactions,
        # 'currency_rates': currency_rates,
        'stock_prices': stock_prices
    }
    json_data = json.dumps(data, ensure_ascii=False, indent=4)


    return json_data


