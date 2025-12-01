import datetime
import json
import os
import pandas as pd
import numpy as np

path_file = os.path.join('..', 'data', 'operations.xlsx')

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

def financial_operations_json(path_file: str):
    '''Функция считывает данные Excel-файла и переводит в json формат'''
    df_excel =pd.read_excel(path_file)
    print(df_excel)
    df_excel = df_excel.replace({np.nan: None})
    #trans_json = json.dumps(df_excel, ensure_ascii=False)
    #print(trans_json.encode('utf-8').decode('utf-8'))

financial_operations_json(path_file)