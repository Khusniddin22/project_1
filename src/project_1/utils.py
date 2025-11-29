import datetime
import json
import os

path_file = os.path.join()

def greeting()->str:
    '''Функция приветствия относительно текущего часа'''
    now = datetime.datetime.now()
    current_now = now.hour
    if current_now >= 0 and current_now < 4:
        return 'Доброй ночи'
    elif current_now >= 4 and current_now < 12:
        return 'Доброе утро'
    elif current_now >= 12 and current_now < 17:
        return 'Добрый день'
    else:
        return 'Добрый вечер'

def financial_operations(path_file):
    pass

