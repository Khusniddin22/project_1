import json
from typing import Any, Dict, Optional
from unittest.mock import patch

import pandas as pd

from project_1.utils import path_json
from src.project_1.views import even_info, main_info


@patch("src.project_1.utils.get_stock_prices")
@patch("src.project_1.utils.get_currency_rates")
@patch("src.project_1.utils.get_top_transactions")
@patch("src.project_1.utils.get_cost_of_card")
@patch("src.project_1.utils.get_data_time")
@patch("src.project_1.utils.time_for_greeting")
def test_main_info(mock_greeting, mock_get_data, mock_cost_of_card, mock_top_transactions, mock_currency, mock_stock):
    mock_greeting.return_value = "Доброе утро"
    mock_get_data.return_value = ["2023-01-01 05:00:00", "2023-01-01 05:00:00"]
    mock_cost_of_card.return_value = {}
    mock_top_transactions.return_value = []
    mock_currency.return_value = []
    mock_stock.return_value = []
    result = main_info("2023-01-01 00:00:00")
    assert (
        result
        == '{\n    "greeting": "Доброе утро",\n    "cards": [],\n    "top_transactions": [],\n    "currency_rates": [],\n    "stock_prices": null\n}'
    )


@patch("src.project_1.utils.get_stock_prices")
@patch("src.project_1.utils.get_currency_rates")
@patch("src.project_1.utils.get_income")
@patch("src.project_1.utils.get_expenses")
@patch("src.project_1.utils.get_data_time_with_range")
def test_even_info(mock_get_data_with_range, mock_expenses, mock_income, mock_currency, mock_stock):
    # Настройка моков
    mock_get_data_with_range.return_value = ["2023-01-01 00:00:00", "2023-01-31 23:59:59"]
    mock_expenses.return_value = {}
    mock_income.return_value = {}
    mock_currency.return_value = []
    mock_stock.return_value = []

    # Вызов тестируемой функции
    result = even_info("2023-01-15 12:00:00", range="M")

    # Ожидаемый результат (в виде строки JSON)
    expected_data = {
        "expenses": {},
        "income": {},
        "currency_rates": [],
        "stock_prices": None,
    }
    expected_json = json.dumps(expected_data, ensure_ascii=False, indent=4)
    assert result == expected_json
