import json
from datetime import datetime, timedelta
from unittest.mock import patch

import pandas as pd
import pytest

from project_1.reports import (spending_by_category, spending_by_weekday,
                               spending_by_workday)
from project_1.utils import get_last_three_month


@pytest.fixture
def sample_transactions_df():
    data = {
        "Дата операции": [
            "01.01.2023",
            "15.01.2023",
            "01.02.2023",
            "10.02.2023",
            "05.03.2023",
            "20.03.2023",
            "01.04.2023",
            "10.04.2023",
            "05.05.2023",
            "20.05.2023",
            "01.06.2023",
            "15.06.2023",
            "01.07.2023",
            "10.07.2023",
            "05.08.2023",
            "20.08.2023",
            "01.09.2023",
            "10.09.2023",
            "05.10.2023",
            "20.10.2023",
        ],
        "Категория": [
            "Еда",
            "Транспорт",
            "Еда",
            "Развлечения",
            "Еда",
            "Транспорт",
            "Еда",
            "Развлечения",
            "Еда",
            "Транспорт",
            "Еда",
            "Развлечения",
            "Еда",
            "Транспорт",
            "Еда",
            "Развлечения",
            "Еда",
            "Транспорт",
            "Еда",
            "Развлечения",
        ],
        "Сумма": [100, 50, 120, 80, 110, 60, 130, 90, 140, 70, 150, 100, 160, 80, 170, 110, 180, 90, 190, 120],
    }
    return pd.DataFrame(data)


def test_spending_by_category_empty():
    # Тест на пустой DataFrame
    empty_df = pd.DataFrame()
    result = spending_by_category(empty_df, "Еда", "2023-10-20 00:00:00")
    assert result == "Нет данных"


def test_spending_by_category_no_category(sample_transactions_df):
    # Тест на категорию, которой нет
    date = "2023-10-20 00:00:00"
    result = spending_by_category(sample_transactions_df, "Одежда", date)
    parsed_result = json.loads(result)
    assert len(parsed_result) == 0


def test_spending_by_category_with_specific_date(sample_transactions_df):
    date = "2023-10-20 00:00:00"
    category = "Еда"
    result = spending_by_category(sample_transactions_df, category, date)
    parsed_result = json.loads(result)

    assert len(parsed_result) == 3
    assert all(item["Категория"] == category for item in parsed_result)
    assert parsed_result[0]["Дата операции"].startswith("2023-08-05")
    assert parsed_result[1]["Дата операции"].startswith("2023-09-01")
    assert parsed_result[2]["Дата операции"].startswith("2023-10-05")


# Параметризованный тест
@pytest.mark.parametrize(
    "test_date, category, expected_count, expected_first_date, expected_last_date",
    [
        ("2023-10-20 00:00:00", "Еда", 3, "2023-08-05", "2023-10-05"),
        ("2023-07-15 00:00:00", "Транспорт", 2, "2023-05-20", "2023-07-10"),
        ("2023-05-01 00:00:00", "Развлечения", 2, "2023-02-10", "2023-04-10"),
        ("2023-01-01 00:00:00", "Еда", 1, "2023-01-01", "2023-01-01"),
        ("2024-01-01 00:00:00", "Еда", 1, "2023-10-05", "2023-10-05"),
        # Несуществующая категория
        ("2023-10-20 00:00:00", "Несуществующая", 0, None, None),
    ],
)
def test_spending_by_category_param(
    sample_transactions_df, test_date, category, expected_count, expected_first_date, expected_last_date
):
    result = spending_by_category(sample_transactions_df, category, test_date)
    parsed_result = json.loads(result)

    assert len(parsed_result) == expected_count

    if expected_count > 0:
        assert all(item["Категория"] == category for item in parsed_result)
        assert parsed_result[0]["Дата операции"].startswith(expected_first_date)
        assert parsed_result[-1]["Дата операции"].startswith(expected_last_date)


# Тесты к функции spending_by_workday
@pytest.fixture
def workday_transactions():
    """Фикстура с данными для проверки рабочих и выходных дней"""
    return pd.DataFrame(
        {
            "Дата операции": [
                "04.12.2023 10:00:00",
                "05.12.2023 10:00:00",
                "09.12.2023 10:00:00",
                "10.12.2023 10:00:00",
                "06.12.2023 10:00:00",
                "01.01.2020 10:00:00",
            ],
            "Сумма операции": [-100.0, -300.0, -500.0, -500.0, 1000.0, -999.0],
        }
    )


def test_spending_by_workday_empty():
    """Тест на пустой DataFrame"""
    result = spending_by_workday(pd.DataFrame())
    assert result == "Нет данных"


@patch("src.project_1.reports.get_last_three_month")
def test_spending_by_workday_calculation(mock_get_date, workday_transactions):
    """Проверка логики расчетов среднего"""
    # Устанавливаем начало диапазона так, чтобы декабрь 2023 попадал
    mock_get_date.return_value = datetime.strptime("2023-10-01 00:00:00", "%Y-%m-%d %H:%M:%S")

    # Дата "сегодня" - конец декабря
    result_json = spending_by_workday(workday_transactions, "2023-12-31 23:59:59")
    result = json.loads(result_json)

    # Проверяем средние значения (абсолютные величины)
    assert result["Workday"] == 200.0
    assert result["Weekend"] == 500.0


@pytest.mark.parametrize(
    "input_date, mock_start_date, expected_result",
    [
        ("2023-12-31 23:59:59", "2023-10-01 00:00:00", {"Weekend": 500.0, "Workday": 200.0}),
        ("2023-12-07 23:59:59", "2023-12-01 00:00:00", {"Workday": 200.0}),
        ("2021-01-01 23:59:59", "2020-10-01 00:00:00", {}),
    ],
)
@patch("src.project_1.reports.get_last_three_month")  # Замените на ваш путь к функции
def test_spending_by_workday_parametrized(
    mock_get_date, input_date, mock_start_date, expected_result, workday_transactions
):
    mock_get_date.return_value = datetime.strptime(mock_start_date, "%Y-%m-%d %H:%M:%S")
    result_json = spending_by_workday(workday_transactions, input_date)
    result_dict = json.loads(result_json)

    assert result_dict == expected_result


data = {
    "Дата операции": [
        "01.01.2023 12:00:00",  # воскресенье
        "02.01.2023 12:00:00",  # понедельник
        "03.01.2023 12:00:00",  # вторник
        "04.01.2023 12:00:00",  # среда
        "05.01.2023 12:00:00",  # четверг
        "06.01.2023 12:00:00",  # пятница
        "07.01.2023 12:00:00",  # суббота
        "08.01.2023 12:00:00",  # воскресенье
    ],
    "Сумма операции": [-100, -200, -300, -400, -500, -600, -700, -800],
}
df = pd.DataFrame(data)


def test_spending_by_weekday_with_date():
    date = "2023-01-08 12:00:00"
    expected_result = {
        "Monday": 200.0,
        "Tuesday": 300.0,
        "Wednesday": 400.0,
        "Thursday": 500.0,
        "Friday": 600.0,
        "Saturday": 700.0,
        "Sunday": 450.0,
    }
    actual_result = json.loads(spending_by_weekday(df, date))  # Преобразование JSON обратно в словарь
    assert actual_result == expected_result


def test_spending_by_weekday_empty_dataframe():
    empty_df = pd.DataFrame(columns=["Дата операции", "Сумма операции"])
    assert spending_by_weekday(empty_df) == "Нет данных"
