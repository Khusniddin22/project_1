import json
from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest

from project_1.reports import (spending_by_category, spending_by_weekday,
                               spending_by_workday)

@pytest.fixture
def sample_transactions():
    return pd.DataFrame(
        {
            "Дата операции": [
                "01.12.2023 10:00:00",
                "01.11.2023 10:00:00",
                "01.01.2022 10:00:00",  # Изменили год на 2022, чтобы точно не попало
                "15.11.2023 12:00:00",
            ],
            "Категория": ["Супермаркеты", "Супермаркеты", "Супермаркеты", "Транспорт"],
            "Сумма": [100, 200, 500, 300],
        }
    )


@pytest.mark.parametrize(
    "category, input_date, expected_count",
    [
        ("Супермаркеты", "2023-12-31 23:59:59", 2),
        ("Супермаркеты", "2024-05-01 00:00:00", 0),
        ("Аптеки", "2023-12-31 23:59:59", 0),
        ("Транспорт", "2023-12-31 23:59:59", 1),
    ],
)
@patch("src.project_1.reports.get_last_three_month")  # Укажите правильный путь к функции
def test_spending_by_category_success(mock_get_date, category, input_date, expected_count, sample_transactions):

    mock_get_date.return_value = datetime.strptime("2023-10-01 00:00:00", "%Y-%m-%d %H:%M:%S")

    result_json = spending_by_category(sample_transactions, category, input_date)

    result_list = json.loads(result_json)
    assert isinstance(result_list, list)
    assert len(result_list) == expected_count

    if expected_count > 0:
        for item in result_list:
            assert item["Категория"] == category


def test_spending_by_category_empty_df():
    """Тест на пустой DataFrame"""
    df_empty = pd.DataFrame()
    result = spending_by_category(df_empty, "Любая", "2023-01-01 00:00:00")
    assert result == "Нет данных"


def test_spending_by_category_invalid_date_format(sample_transactions):
    """Тест на ошибку формата даты"""
    with pytest.raises(ValueError):
        spending_by_category(sample_transactions, "Супермаркеты", "31-12-2023")  # Неверный формат


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
