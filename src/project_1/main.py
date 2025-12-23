from views import even_info, main_info
from services import profitable_cashback

if __name__ == "__main__":
    result = profitable_cashback('../../data/operations.xlsx', 2018, 5)
    print(result)
