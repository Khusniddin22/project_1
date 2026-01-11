import pandas as pd

from src.project_1.utils import get_expenses, get_income


# Тесты для функции get_expenses
def test_get_expenses_empty_df():
    """Тест для пустого DataFrame."""
    df = pd.DataFrame()
    result = get_expenses(df)
    assert result == {}


def test_get_expenses_only_transfers_and_cash():
    """Тест на случай, когда есть только 'переводы' и 'наличные'."""
    df = pd.DataFrame(
        {
            "Сумма операции": [-100.0, -50.0, -200.0, 500.0],
            "Категория": ["Переводы", "Наличные", "Переводы", "Зарплата"],
        }
    )
    result = get_expenses(df)
    expected_trans_cash = [{"category": "Переводы", "amount": 300.0}, {"category": "Наличные", "amount": 50.0}]
    assert result["total_amount"] == 350.0
    assert result["main"] == []
    assert result["transfers_and_cash"] == expected_trans_cash


def test_get_expenses_only_one_expenses():
    """Тест на одну единственную операцию расхода"""
    df = pd.DataFrame({"Сумма операции": [-100.0], "Категория": ["Супермаркеты"]})
    result = get_expenses(df)
    expected_result_category = [{"category": "Супермаркеты", "amount": 100.0}]
    assert result["total_amount"] == 100.0
    assert result["main"] == expected_result_category
    assert result["transfers_and_cash"] == []


# Тесты для функции get_income


def test_get_income_empty_df():
    """Тест для пустого DataFrame"""
    df = pd.DataFrame(columns=["Сумма операции", "Категория"])
    result = get_income(df)
    assert result == {}


def test_get_income_only_one_category():
    """Тест с одной категорией поступления"""
    df = pd.DataFrame({"Сумма операции": [500.0, -150.0, 500.0], "Категория": ["Зарплата", "Развлечения", "Зарплата"]})
    result = get_income(df)
    assert result == {
        "total_amount": 1000.0,
        "main": [{"category": "Зарплата", "amount": 1000.0}],
    }


def test_get_income_single_operation():
    """Тест на одну операцию поступления"""
    df = pd.DataFrame({"Сумма операции": [500.0], "Категория": ["Зарплата"]})
    result = get_income(df)
    assert result == {"total_amount": 500.0, "main": [{"category": "Зарплата", "amount": 500.0}]}
