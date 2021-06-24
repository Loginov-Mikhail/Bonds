# ******************************************************************************
#   Программа bonds.py считывает из файла input.txt URL-адреса, скачивает с
# сайта bonds.finam.ru страницы с информацией об облигациях, выбирает оттуда
# необходимые данные и выводит их на экран, а также сохраняет эту информацию в
# файл output.txt. Полученный файл можно открыть в табличном процессоре
# (например, MS Excel) для дальнейшей обработки.
#   Для запуска программы необходим Python 3.0 и библиотеки pandas, lxml, bs4,
# html5lib.
#   При выполнении в командной строке:
#   python3 bonds.py
#                Copyright (c) 2018 - 2021 Логинов М.Д.
#  Разработчик: Логинов М.Д.
#  Модифицирован: 23 июня 2021 г.
# ******************************************************************************

# -*- coding: utf-8 -*-
import urllib.request
import datetime
import pandas as pd


# ******************************************************************************
# Процедура сохранения страницы во временный файл
# ******************************************************************************
def load_url(url):
    response = urllib.request.urlopen(url).read().decode('cp1251')
    f = open('temp.html', 'w', encoding='cp1251')
    f.write(response)
    f.close()


# ******************************************************************************
# Функция парсинга страниц bonds.finam.ru с общей информацией об облигации.
# Результат - строка с именем, кодом ISIN, датой размещения и погашения облига-
# ции, её номиналом и налоговым коэффициентом. Данные разделены точкой с запя-
# той.
# ******************************************************************************
def parse_info(fileName):
    f = open(fileName, 'r', encoding='cp1251')
    codeISIN = '--'
    i = 0
    for line in f:
        if i == 1:
            codeISIN = line.split('span>')[1][:-2]  # ISIN код
            i = 0
        if i == 3:
            redemption = line.split('span>')[1][:-2]  # Дата погашения
            i = 0
        if line.count('h3') > 0:
            line2 = line.replace('>', '<')
            str1 = line2.split('<')
            name = str1[2]  # Название облигации
        if line.count('ISIN код:') > 0:
            i = 1
        if line.count('Дата погашения:') > 0:
            i = 3
        if line.count('Номинал:') > 0:  # Номинал
            nominal = int(line.split('span>')[1][:-2].replace('\xa0', ''))
    f.close()
    return name + ';' + codeISIN + ';' + redemption + ';' + str(nominal)


# ******************************************************************************
# Функция парсинга страниц bonds.finam.ru с информацией о платежах по облига-
# ции. Результат - строка с совокупным купонным доходом, очищенным от налогов.
# ******************************************************************************
def parse_payments(fileName):
    # Поиск таблицы с данными о платежах
    for i in range(8):
        df = pd.read_html(fileName)[i]
        if df.columns.dtype == 'object':
            break
    # Удаление мусора из найденной таблицы
    df = df.iloc[:, [1, 2, 4]]
    cols = ['date', 'rate', 'coupon']
    df.set_axis(cols, axis='columns', inplace=True)
    df = df.dropna()
    df = df[df['date'].str.len() < 12]
    df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y')
    df['rate'] = df['rate'].str.replace('%', '')
    df['rate'] = df['rate'].str.replace(',', '.')
    df['coupon'] = df['coupon'].str.replace(u'\u00a0RUR', '')
    df['coupon'] = df['coupon'].str.replace(',', '.')
    df['coupon'] = pd.to_numeric(df['coupon'], downcast='float')
    df['rate'] = pd.to_numeric(df['rate'], downcast='float')
    today = datetime.datetime.today()
    df = df[df['date'] > today].reset_index(drop=True)
    # Вычисление совокупного купонного дохода
    sumPayments = 0
    for i in range(len(df)):
        sumPayments += 0.87 * df.loc[i, 'coupon']
    result = '%10.2f' % sumPayments
    return result.strip()


# ******************************************************************************
#                       Текст основной программы
# ******************************************************************************

fileInput = open('input.txt', 'r')
fileOutput = open('output.txt', 'w')
i = 0
for line in fileInput:
    url = line.replace('/default.asp', '00002/default.asp')
    load_url(url)
    newData = parse_info('temp.html')
    payments = parse_payments('temp.html')
    result = newData
    i = i + 1
    result = result + ';' + payments.replace('.', ',') + ';' + url
    print(str(i) + ';' + result[:-1])
    fileOutput.write(result)
fileInput.close()
fileOutput.close()
