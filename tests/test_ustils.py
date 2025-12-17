import datetime
from datetime import date, timedelta

from src.project_1.utils import get_data_time


def test_get_data_time():
    assert get_data_time("2018-05-20 15:30:00") == ['01.05.2018 15:30:00', '20.05.2018 15:30:00']
    assert get_data_time("2022-12-22 00:00:00") == ['01.12.2022 00:00:00', '22.12.2022 00:00:00']