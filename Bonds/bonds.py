# ******************************************************************************
#   Программа bonds.py при помощи API Мосбиржи получает данные о рублевых
# облигациях со сроком погашения до введенной пользователем даты и сохраняет
# эту информацию в файл output.csv для дальнейшей обработки в QUIK.
# файл output.xlsx. Полученный файл можно открыть в табличном процессоре
#   Для запуска программы необходим Python 3.6 и библиотека pandas.
#   При выполнении в командной строке:
#   python3 bonds.py
#                Copyright (c) 2018 - 2022 Логинов М.Д.
#  Разработчик: Логинов М.Д.
#  Модифицирован: 13 декабря 2022 г.
# ******************************************************************************

# -*- coding: utf-8 -*-
import urllib.request
import datetime
import pandas as pd


# ******************************************************************************
# Функция сохранения страницы во временный файл
# ******************************************************************************
def load_url(url):
    response = urllib.request.urlopen(url).read().decode('cp1251')
    f = open('temp.html', 'w', encoding='cp1251')
    f.write(response)
    f.close()


# ******************************************************************************
# Функция получения списка облигаций
# ******************************************************************************
def load_bonds_info():
    # Загрузка данных об ОФЗ
    url = f'https://iss.moex.com/iss/engines/stock/markets/bonds/boards/TQOB' \
          f'/securities.csv?iss.only=securities&securities.columns=' \
          f'SECNAME,SECID,MATDATE,FACEVALUE,COUPONVALUE,OFFERDATE,REGNUMBER,' \
          f'NEXTCOUPON,FACEUNIT'
    load_url(url)
    dfStateBonds = pd.read_csv('temp.html', header=1, encoding='cp1251',
                               sep=';')
    # Загрузка данных о корпоративных облигациях
    url = url.replace('TQOB', 'TQCB')
    load_url(url)
    dfCorporateBonds = pd.read_csv('temp.html', header=1, encoding='cp1251',
                                   sep=';')

    dfAllBonds = pd.concat([dfCorporateBonds, dfStateBonds])
    return dfAllBonds


# ******************************************************************************
# Функция проверки корректности даты
# ******************************************************************************
def validate_date(dateText):
    isValidDate = False
    try:
        if (datetime.datetime.strptime(dateText, '%d.%m.%Y') >
            datetime.datetime.today()):
            isValidDate = True
        else:
            print('Ошибка! Введена прошедшая дата.')
    except ValueError:
        print('Некорректный формат даты, должно быть DD.MM.YYYY')
    return isValidDate


# ******************************************************************************
# Функция ввода диапазона дат
# ******************************************************************************
def input_data():
    isValid = False
    while (not isValid):
        finishDate = input('Введите максимально возможную дату погашения: ')
        isValid = validate_date(finishDate)
    finishDate = datetime.datetime.strptime(finishDate, '%d.%m.%Y')
    startDate = datetime.datetime.now()
    startDate = startDate + datetime.timedelta(days=5)
    return startDate, finishDate


# ******************************************************************************
# Функция фильтрации данных
# ******************************************************************************
def filter_data(df, startDate, finishDate):
    df = df[df['MATDATE'] != '0000-00-00']
    df['MATDATE'] = pd.to_datetime(df['MATDATE'])
    df = df[df['MATDATE'] <= finishDate]
    df = df[df['FACEUNIT'] == 'SUR']
    del df['FACEUNIT']
    # Пока удаляю эти колонки, позднее планирую их использовать
    del df['OFFERDATE']
    del df['REGNUMBER']
    df.info()
    return df


# ******************************************************************************
# Функция подготовки данных к сохранению
# ******************************************************************************
def prepare_data_for_saving(df):
    df.set_axis(['Наименование', 'ISIN код', 'Дата погашения', 'Номинал',
                 'Купон', 'url'],
                axis='columns', inplace=True)
    df['Купон'] = 0.87 * df['Купон']
    df['Цена, %'] = 100.01
    df['НКД'] = 123.01
    df['Покупка'] = list(map(lambda x: f'=F{x + 2}*D{x + 2}/100+G{x + 2}',
                             list(range(len(df)))))
    df['Продажа'] = list(map(lambda x: f'=IF(F{x + 2}<100,D{x + 2}+E{x + 2}'
                                       f'-0.13*(100-F{x + 2})*D{x + 2}/100,'
                                       f'D{x + 2}+E{x + 2})',
                             list(range(len(df)))))
    df['%'] = list(map(lambda x: f'=365*(I{x + 2}-H{x + 2})/(H{x + 2}*'
                                 f'(C{x + 2}-TODAY()))',
                       list(range(len(df)))))
    df['Результат инвестиций'] = list(map(lambda x: f'=ROUNDDOWN($N$1/H{x + 2}'
                                                    f',0)*I{x + 2}',
                                          list(range(len(df)))))
    df['Адрес'] = df['url']
    del df['url']
    return df


# ******************************************************************************
# Функция создания файла output.csv
# ******************************************************************************
def create_csv():
    start, finish = input_data()
    dfBonds = load_bonds_info()
    dfBonds = filter_data(dfBonds, start, finish)
    dfBonds = prepare_data_for_saving(dfBonds)
    dfBonds.to_csv('output.csv', sep=';', index=False, encoding='cp1251',
                   float_format='%10.2f')


# ******************************************************************************
#                       Текст основной программы
# ******************************************************************************
if __name__ == '__main__':
    create_csv()
