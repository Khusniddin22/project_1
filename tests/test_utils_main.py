import datetime
import json
import os


import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from src.project_1.utils import (
    get_data_time,
    get_table_period,
    get_cost_of_card,
    get_top_transactions,
    get_currency_rates
)


def test_get_data_time():
    assert get_data_time("2018-05-20 15:30:00") == ['01.05.2018 15:30:00', '20.05.2018 15:30:00']
    assert get_data_time("2022-12-22 00:00:00") == ['01.12.2022 00:00:00', '22.12.2022 00:00:00']

# Фикстура для создания тестового DataFrame, который будет возвращать mock pd.read_excel
@pytest.fixture
def mock_excel_data():
    """Возвращает тестовый DataFrame для имитации Excel-файла."""
    data = {
        'Дата операции': [
            '01.01.2023 10:00:00',
            '05.01.2023 16:30:00',
            '10.01.2023 15:45:00',
            '15.01.2023 09:00:00',
            '20.01.2023 11:15:00',
            '25.01.2023 14:00:00',
            '30.01.2023 16:30:00',
            '02.02.2023 10:00:00' # Дата за пределами января
        ],
        'Сумма операции': [-100, -250, -50, -300, -120, -180, -70, -400],
        'Категория': ['Еда', 'Транспорт', 'Развлечения', 'Еда', 'Одежда', 'Транспорт', 'Еда', 'Путешествия']
    }
    df = pd.DataFrame(data)
    # Важно: В функции get_table_period происходит to_datetime, здесь пока строки
    return df

# --- Тесты на успешное выполнение ---

@patch('pandas.read_excel')
def test_get_table_period_two_dates_success(mock_read_excel, mock_excel_data):
    """
    Тестирование успешного получения DataFrame для периода с двумя датами.
    """
    mock_read_excel.return_value = mock_excel_data
    path = os.path.join('..', '..', 'data', 'operations.xlsx')
    period = ["05.01.2023 15:30:00", "20.01.2023 15:30:00"]

    result_df = get_table_period(path, period)

    # Проверяем, что вернулся DataFrame
    assert isinstance(result_df, pd.DataFrame)
    # Проверяем количество строк
    assert len(result_df) == 4 # '05.01', '10.01', '15.01', '20.01'
    # Проверяем, что даты находятся в заданном диапазоне
    start_dt = datetime.datetime.strptime(period[0], "%d.%m.%Y %H:%M:%S")
    end_dt = datetime.datetime.strptime(period[1], "%d.%m.%Y %H:%M:%S")
    assert all(result_df['Дата операции'] >= start_dt)
    assert all(result_df['Дата операции'] <= end_dt)
    # Проверяем сортировку по дате
    assert result_df['Дата операции'].is_monotonic_increasing

# --- Тесты на обработку ошибок ---

@patch('pandas.read_excel')
def test_get_table_period_file_not_found(mock_read_excel):
    """
    Тестирование обработки исключения FileNotFoundError.
    """
    mock_read_excel.side_effect = FileNotFoundError(f"Файл не найден")
    path = os.path.join('test.xlsx')
    period = ["01.01.2021 00:00:00", "31.01.2021 00:00:00"]
    result = get_table_period(path, period)
    assert result.empty


@patch('pandas.read_excel')
def test_get_table_period_empty_list(mock_read_excel, mock_excel_data):
    """
    Тестирование обработки ошибки пустого списка периода
    """
    mock_read_excel.return_value = pd.DataFrame
    path = os.path.join('..', '..', 'data', 'operations.xlsx')
    period = []
    result = get_table_period(path, period)
    assert result.empty


@pytest.fixture
def mock_card_and_transaction_data():
    """Возвращает тестовый DataFrame с полными данными для тестирования карт и транзакций."""
    data = {
        'Дата операции': [
            datetime.datetime(2023, 1, 1, 10, 0, 0),
            datetime.datetime(2023, 1, 5, 12, 30, 0),
            datetime.datetime(2023, 1, 10, 15, 45, 0),
            datetime.datetime(2023, 1, 15, 9, 0, 0),
            datetime.datetime(2023, 1, 20, 11, 15, 0),
            datetime.datetime(2023, 1, 25, 14, 0, 0),
            datetime.datetime(2023, 1, 30, 16, 30, 0),
            datetime.datetime(2023, 2, 2, 10, 0, 0),
            datetime.datetime(2023, 1, 7, 18, 0, 0) # Позитивная операция
        ],
        'Дата платежа': [ # Добавлена для get_top_transactions
            datetime.datetime(2023, 1, 1, 10, 0, 0),
            datetime.datetime(2023, 1, 5, 12, 30, 0),
            datetime.datetime(2023, 1, 10, 15, 45, 0),
            datetime.datetime(2023, 1, 15, 9, 0, 0),
            datetime.datetime(2023, 1, 20, 11, 15, 0),
            datetime.datetime(2023, 1, 25, 14, 0, 0),
            datetime.datetime(2023, 1, 30, 16, 30, 0),
            datetime.datetime(2023, 2, 2, 10, 0, 0),
            datetime.datetime(2023, 1, 7, 18, 0, 0)
        ],
        'Сумма операции': [
            -100.00, -250.50, -50.00, -300.00, -120.00, -180.00, -70.00, -400.00, 1000.00  # 1000 - пополнение
        ],
        'Сумма операции с округлением': [  # Добавлена для get_cost_of_card
            -100.00, -250.50, -50.00, -300.00, -120.00, -180.00, -70.00, -400.00, 1000.00
        ],
        'Кэшбэк': [5, 12.5, 2.5, 15, 6, 9, 3.5, 20, 0],  # Просто для примера, не используется в текущей логике
        'Номер карты': [
            '**1234', '**5678', '**1234', '**5678', '**9012', '**1234', '**5678', '**9012', '**1234'
        ],
        'Категория': ['Еда', 'Транспорт', 'Развлечения', 'Еда', 'Одежда', 'Транспорт', 'Еда', 'Путешествия',
                      'Пополнение'],
        'Описание': ['Кафе', 'Такси', 'Кино', 'Ресторан', 'Магазин', 'Автобус', 'Продукты', 'Авиабилеты', 'Перевод']
    }
    df = pd.DataFrame(data)
    df['Дата операции'] = pd.to_datetime(df['Дата операции'])
    df['Дата платежа'] = pd.to_datetime(df['Дата платежа'])
    return df


# --- Тесты для get_cost_of_card ---

def test_get_cost_of_card_success(mock_card_and_transaction_data):
    """
    Тестирование успешного получения информации о затратах по картам.
    """
    df_sorted = mock_card_and_transaction_data

    result = get_cost_of_card(df_sorted)

    # Проверяем, что результаты корректны для конкретных карт
    card_1234_transactions = [t for t in result if t['last_digits'] == '1234']
    assert len(card_1234_transactions) == 3  # 3 операции с **1234, последняя операция не отрицательная

    # Проверяем структуру одного элемента
    assert card_1234_transactions[0]['last_digits'] == '1234'
    assert card_1234_transactions[0]['total_spent'] == 100.00
    assert card_1234_transactions[0]['cashback'] == 1.00

    card_5678_transactions = [t for t in result if t['last_digits'] == '5678']
    assert len(card_5678_transactions) == 3
    assert card_5678_transactions[0]['total_spent'] == 250.50
    assert card_5678_transactions[0]['cashback'] == 2.50  # Округление!



def test_get_cost_of_card_missing_columns(mock_card_and_transaction_data):
    """
    Тестирование get_cost_of_card при отсутствии необходимых колонок.
    """
    df_missing_col = mock_card_and_transaction_data.drop(columns=['Номер карты'])
    result = get_cost_of_card(df_missing_col)
    assert result == []

# Тесты для get_top_transactions

def test_get_top_transactions_success(mock_card_and_transaction_data):
    """
    Тестирование успешного топа по затратам
    """
    df_sorted = mock_card_and_transaction_data
    number = 3

    result = get_top_transactions(df_sorted, number)

    assert result[0]['amount'] == -400.00
    assert result[0]['category'] == 'Путешествия'
    assert result[1]['amount'] == -300.00
    assert result[1]['category'] == 'Еда'


def test_get_top_transactions_empty_dataframe():
    """
    Тестирование функции get_top_transactions с пустым DataFrame.
    """
    empty_df = pd.DataFrame(columns=[
        'Дата платежа', 'Сумма операции', 'Категория', 'Описание'
    ])
    result = get_top_transactions(empty_df, 5)
    assert isinstance(result, list)
    assert len(result) == 0


def test_get_top_transactions_missing_columns(mock_card_and_transaction_data):
    """
    Тестирование get_top_transactions при отсутствии необходимых колонок.
    """
    df_missing_col = mock_card_and_transaction_data.drop(columns=['Категория'])
    result = get_top_transactions(df_missing_col, 2)
    assert result == []


# Тесты для функции get_currency_rates

@pytest.fixture
def mock_empty_json_file():
    return {}

@patch('os.getenv')
@patch('requests.get')
@patch('builtins.open')
def test_get_currency_rates_file_not_found(mock_open, mock_requests_get, mock_os_getenv):
    """
    Тестирование обработки FileNotFoundError.
    """
    mock_open.side_effect = FileNotFoundError("File doesn't exist")
    path = "error_path.json"

    result = get_currency_rates(path)

    assert result == []
    mock_open.assert_called_once_with(path, 'r', encoding='utf-8')
    mock_requests_get.assert_not_called() # API не должен вызываться
    mock_os_getenv.assert_not_called() # os.getenv не должен вызываться


@patch('os.getenv')
@patch('requests.get')
@patch('builtins.open')
def test_get_currency_rates_file_empty(mock_open, mock_requests_get, mock_os_getenv, mock_empty_json_file):
    """
    Тестирование обработки открытия пустого JSON-файла
    """
    mock_os_getenv.assert_not_called()
    mock_open.return_value = mock_empty_json_file

    path = "empty.json"
    result = get_currency_rates(path)
    assert result == []
    mock_requests_get.assert_not_called()