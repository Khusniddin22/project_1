import json
from unittest.mock import patch

import pandas as pd
import pytest

from project_1.utils import path_file
from src.project_1.services import (investment_bank, name_search, phone_search,
                                    profitable_cashback, simple_search)


@pytest.fixture
def sample_df():
    """Фикстура для создания тестового DataFrame"""
    return pd.DataFrame(
        {
            "Дата операции": ["01.01.2023 12:00:00", "05.01.2023 15:00:00", "10.02.2023 10:00:00"],
            "Категория": ["Супермаркеты", "Аптеки", "Супермаркеты"],
            "Кэшбэк": [100, 50, 0],
            "Сумма платежа": [-1500, -2050, -500],
        }
    )


@patch("pandas.read_excel")
@patch("src.project_1.services.logger_services")  # Указан полный путь к логгеру
def test_profitable_cashback_success(mock_logger, mock_read_excel, sample_df):
    """
    Тест успешного выполнения функции
    """
    # Настраиваем мок для чтения excel
    mock_read_excel.return_value = sample_df

    result_json = profitable_cashback(path_file, 2023, 1)
    result = json.loads(result_json)

    assert result["Супермаркеты"] == 15
    assert result["Аптеки"] == 20
    assert "10.02.2023" not in result_json


@patch("pandas.read_excel")
def test_profitable_cashback_file_not_found(mock_read_excel):
    """Тест ситуации, когда файл не найден"""
    mock_read_excel.side_effect = FileNotFoundError
    result = profitable_cashback("wrong_path.xlsx", 2023, 1)
    assert result == ""


@patch("pandas.read_excel")
def test_profitable_cashback_empty_period(mock_read_excel, sample_df):
    """Тест, если за указанный период нет данных"""
    mock_read_excel.return_value = sample_df
    # Ищем 2025 год, которого нет в данных
    result_json = profitable_cashback(path_file, 2025, 1)
    assert result_json == "{}"


# 2. ТЕСТЫ ДЛЯ investment_bank


def test_investment_bank_success():
    """Тест логики округления"""
    transactions = [
        {"2018-01-03": 73.06},  # До 100 не хватает 26.94
        {"2018-01-03": 21.0},  # До 100 не хватает 79.0
        {"2018-02-01": 316.0},  # 2 месяц, а не 1
    ]

    result = investment_bank("2018-01", transactions, 100)

    # (100 - 73.06) + (100 - 21.0) = 26.94 + 79.0 = 105.94
    assert result == 105.94


def test_investment_bank_no_rounding_needed():
    """округление 0"""
    transactions = [{"2018-01-01": 100.0}, {"2018-01-02": 50.0}]
    result = investment_bank("2018-01", transactions, 50)
    assert result == 0.0


def test_investment_bank_empty_list():
    """Тест на пустой список транзакций"""
    assert investment_bank("2018-01", [], 50) is None


def test_investment_bank_zero_limit():
    """Тест на деление на ноль (если лимит 0) —
    хорошо бы добавить обработку в саму функцию, но проверим поведение"""
    transactions = [{"2018-01-01": 10.5}]
    with pytest.raises(ZeroDivisionError):
        investment_bank("2018-01", transactions, 0)


@pytest.fixture
def mock_excel_data():
    return pd.DataFrame(
        {
            "Дата операции": ["01.01.2023", "02.01.2023", "03.01.2023"],
            "Дата платежа": ["01.01.2023", "02.01.2023", "03.01.2023"],
            "Номер карты": ["*1111", "*2222", "*3333"],
            "Статус": ["OK", "OK", "OK"],
            "Сумма операции": [100, 200, 300],
            "Валюта операции": ["RUB", "RUB", "RUB"],
            "Сумма платежа": [-100, -200, -300],
            "Валюта платежа": ["RUB", "RUB", "RUB"],
            "Кэшбэк": [1, 2, 3],
            "Категория": ["Супермаркеты", "Транспорт", None],  # Один None для проверки dropna
            "Описание": ["Покупка в Пятерочке", "Оплата такси +79001112233", "Перевод"],
            "Округление на инвесткопилку": [0, 0, 0],
            "Сумма операции с округлением": [100, 200, 300],
        }
    )


# 3. Тесты простого поиска


@patch("pandas.read_excel")
@patch("src.project_1.services.logger_services")
def test_simple_search_success(mock_logger, mock_read_excel, mock_excel_data):
    mock_read_excel.return_value = mock_excel_data

    result_json = simple_search("Супермаркеты")
    result = json.loads(result_json)

    assert len(result) == 1
    assert result[0]["Категория"] == "Супермаркеты"

    result_json = simple_search("такси")
    result = json.loads(result_json)
    assert result[0]["Описание"] == "Оплата такси +79001112233"


@patch("src.project_1.services.logger_services")
def test_simple_search_invalid_input(mock_logger):
    # Тест на пустую строку
    assert simple_search("") == []
    # Не строка (например, число)
    assert simple_search(123) == []


@patch("pandas.read_excel")
def test_simple_search_no_results(mock_read_excel, mock_excel_data):
    mock_read_excel.return_value = mock_excel_data
    result_json = simple_search("Несуществующий текст")
    assert json.loads(result_json) == []


# 4. Тесты простого поиска по телефону


@patch("pandas.read_excel")
@patch("src.project_1.services.logger_services")
def test_phone_search_success(mock_logger, mock_read_excel, mock_excel_data):
    mock_read_excel.return_value = mock_excel_data

    # Ищем номер, который есть в описании (функция вырежет его из строки поиска)
    result_json = phone_search("МТС +79001112233")
    result = json.loads(result_json)

    assert len(result) == 1
    assert "+79001112233" in result[0]["Описание"]


@patch("src.project_1.services.logger_services")
def test_phone_search_invalid_input(mock_logger):
    assert phone_search("") == []
    assert phone_search(None) == []


@patch("pandas.read_excel")
def test_phone_search_not_found(mock_read_excel, mock_excel_data):
    mock_read_excel.return_value = mock_excel_data

    # Номер есть в поиске, но его нет в Excel описаниях
    result_json = phone_search("БИ +79990000000")
    assert json.loads(result_json) == []


@patch("pandas.read_excel")
def test_phone_search_regex_logic(mock_read_excel, mock_excel_data):
    mock_read_excel.return_value = mock_excel_data

    # Проверка, что функция справляется, если в запросе просто номер телефона
    result_json = phone_search("79001112233")
    result = json.loads(result_json)
    assert len(result) == 1


@pytest.mark.parametrize(
    "search_str, expected_len, expected_field, expected_value",
    [
        ("Супермаркеты", 1, "Категория", "Супермаркеты"),  # Поиск по категории
        ("такси", 1, "Описание", "Оплата такси +79001112233"),  # Поиск по описанию
        ("Перевод", 0, None, None),  # Категория None, dropna её удалит, результат 0
        ("Apple", 0, None, None),
        ("", 0, None, None),
    ],
)
@patch("pandas.read_excel")
@patch("src.project_1.services.logger_services")
def test_simple_search_param(
    mock_logger, mock_read_excel, search_str, expected_len, expected_field, expected_value, mock_excel_data
):
    mock_read_excel.return_value = mock_excel_data
    result_raw = simple_search(search_str)

    if isinstance(result_raw, list):
        assert len(result_raw) == expected_len
    else:
        result = json.loads(result_raw)
        assert len(result) == expected_len
        if expected_len > 0:
            assert result[0][expected_field] == expected_value


# Тесты для name_search
@pytest.fixture
def mock_excel_data_name():
    """Фикстура с тестовыми данными для поиска по имени"""
    return pd.DataFrame(
        {
            "Категория": ["Переводы", "Переводы", "Еда", "Переводы"],
            "Описание": [
                "Перевод Иван И.",
                "Оплата Петру П.",
                "Иван И. купил бургер",  # Категория не "Переводы"
                "Перевод Марии С.",
            ],
            "Сумма": [100, 200, 300, 400],
        }
    )


@patch("pandas.read_excel")
def test_name_search_success(mock_read_excel, mock_excel_data_name):
    """Проверка успешного поиска при наличии совпадения"""
    mock_read_excel.return_value = mock_excel_data_name

    result_json = name_search("path.xlsx", "Нужно найти Иван И. в строке")
    result = json.loads(result_json)

    assert len(result) == 1
    assert result[0]["Описание"] == "Перевод Иван И."
    assert result[0]["Категория"] == "Переводы"


@patch("pandas.read_excel")
def test_name_search_no_name_in_query(mock_read_excel):
    """Проверка ситуации, когда в поисковой строке нет паттерна 'Имя И.'"""
    result_json = name_search("path.xlsx", "Просто какой-то текст")
    result = json.loads(result_json)

    assert result == []
    # Проверяем, что pandas даже не вызывался, так как поиск упал раньше
    mock_read_excel.assert_not_called()


@patch("pandas.read_excel")
def test_name_search_exception(mock_read_excel):
    """Проверка обработки исключений (например, файл не найден)"""
    mock_read_excel.side_effect = Exception("File not found")

    result_json = name_search("invalid_path.xlsx", "Иван И.")
    result = json.loads(result_json)

    assert result == []


@pytest.mark.parametrize(
    "search_str, expected_count, first_match_desc",
    [
        # 1. Валидное имя, есть в базе
        ("Перевод для Иван И.", 1, "Перевод Иван И."),
        # 2. Имя есть в запросе, но нет в базе (Петр П. есть в базе, но мы ищем Сидор С.)
        ("Сидор С.", 0, None),
        # 3. Имя есть в базе, но категория не "Переводы" (Иван И. в категории "Еда" проигнорируется)
        # В базе останется только один Иван И. из категории Переводы
        ("Иван И.", 1, "Перевод Иван И."),
        # 4. Латиница (регулярка поддерживает [A-Za-z])
        ("John D.", 0, None),
        # 5. Некорректный формат имени в поиске (нет точки или пробела)
        ("ИванИ", 0, None),
        ("Иван И", 0, None),
    ],
)
@patch("pandas.read_excel")
def test_name_search_parametrized(mock_read_excel, search_str, expected_count, first_match_desc, mock_excel_data_name):
    mock_read_excel.return_value = mock_excel_data_name

    result_json = name_search("fake.xlsx", search_str)
    result = json.loads(result_json)

    assert len(result) == expected_count
    if expected_count > 0:
        assert result[0]["Описание"] == first_match_desc
