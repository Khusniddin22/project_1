import json

import pandas as pd

def profitable_cashback(path_file: str, year: int, month: int)->dict[str, int]:
    """
    Выдает информацию о выгодных категориях кешбэка
    """
    df = pd.read_excel(path_file)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    df_filtered = df[
        (df["Дата операции"].dt.year == year)
        &
        (df["Дата операции"].dt.month == month)
    ]
    df_filtered = df_filtered[df_filtered["Кэшбэк"] > 0]
    df_filtered = df_filtered[df_filtered["Сумма платежа"] < 0]

    expenses_categories = df_filtered.groupby("Категория")["Сумма платежа"].sum()
    cashback_categories = abs(expenses_categories) // 100

    result = cashback_categories.to_dict()
    return json.dumps(result, ensure_ascii=False, indent=4)




if __name__ == "__main__":
    result = profitable_cashback('../../data/operations.xlsx', 2018, 5)