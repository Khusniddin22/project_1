import pandas as pd
from reports import spending_by_category
from services import *
from views import even_info, main_info

if __name__ == "__main__":
    data_request = "2018-05-20 00:00:00"
    result_view = main_info(data_request)
    # print(result_view)

    result_cashback = profitable_cashback("../../data/operations.xlsx", 2018, 5)
    # print(result_cashback)
    investment_transactions = get_transactions_for_investment("../../data/operations.xlsx")
    result_investments = investment_bank(investment_transactions)
    # print(result_investments)

    df = pd.read_excel("../../data/operations.xlsx", sheet_name="Отчет по операциям")
    result_report = spending_by_category(df, "Ж/д билеты", "2018-05-20")
