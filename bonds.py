# ******************************************************************************
#   Программа bonds.py считывает из файла input.txt URL-адреса, скачивает с
# сайта bonds.finam.ru страницы с информацией об облигациях, выбирает оттуда
# необходимые данные и выводит их на экран, а также сохраняет эту информацию в
# файл output.txt. Полученный файл можно открыть в табличном процессоре
# (например, MS Excel) для дальнейшей обработки.
#   Для запуска программы необходим Python 3.0
#   При выполнении в командной строке:
#   python3 bonds.py
#                Copyright (c) 2018 - 2020 Логинов М.Д.
#  Разработчик: Логинов М.Д.
#  Модифицирован: 7 января 2020 г.
# ******************************************************************************

# -*- coding: utf-8 -*-
import urllib.request
import datetime

# Ключевая ставка ЦБ РФ.
KEY_RATE = 6.5
# Дата, с которой купоны корпоративных облигаций освобождены от НДФЛ, если
# ставка купона не превышает на 5 п.п. ключевую ставку.
FREE_TAX = datetime.datetime(2017, 1, 1)


# ******************************************************************************
# Процедура сохранения страницы во временный файл
# ******************************************************************************
def load_url(url):
    response = urllib.request.urlopen(url).read().decode('cp1251')
    f = open('temp.html', 'w', encoding='cp1251')
    f.write(response)
    f.close()


# ******************************************************************************
# Функция определения налогового коэффициента. Для государственных и муници-
# пальных облигаций возвращает 0, в остальных случаях - 1.
# ******************************************************************************
def tax_rate(strName):
    result = "1"
    if strName.lower().count('министерство') > 0:
        result = "0"
    if strName.lower().count('республика') > 0:
        result = "0"
    if strName.lower().count('край') > 0:
        result = "0"
    if strName.lower().count('область') > 0:
        result = "0"
    return result


# ******************************************************************************
# Функция определения суммы налога подлежащего уплате.
# ******************************************************************************
def tax(coupon, rate, taxRating, datePlacement):
    if taxRating > 0:
        arrayDate = datePlacement.split('.')
        dtDate = datetime.datetime(int(arrayDate[2]), int(arrayDate[1]),
                                   int(arrayDate[0]))
        if dtDate > FREE_TAX:
            if KEY_RATE + 5 >= rate:
                result = 0
            else:
                standard = (KEY_RATE + 5) * coupon / rate
                result = 0.35 * (coupon - standard)
        else:
            if KEY_RATE + 5 >= rate:
                result = 0.13 * coupon
            else:
                standard = (KEY_RATE + 5) * coupon / rate
                result = 0.13 * standard + 0.35 * (coupon - standard)
    else:
        result = 0
    result = int(100 * result) / 100
    return result


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
        if i == 2:
            placementDate = line.split('span>')[1][:-2]  # Дата размещения
            i = 0
        if i == 3:
            redemption = line.split('span>')[1][:-2]  # Дата погашения
            i = 0
        if i == 4:
            fullName = line.split('td>')[1][:-2]  # Полное наименование
            taxRate = tax_rate(fullName)
            i = 0
        if line.count('h3') > 0:
            line2 = line.replace('>', '<')
            str1 = line2.split('<')
            name = str1[2]  # Название облигации
        if line.count('ISIN код:') > 0:
            i = 1
        if line.count('Дата начала размещения:') > 0:
            i = 2
        if line.count('Дата погашения:') > 0:
            i = 3
        if line.count('Номинал:') > 0:  # Номинал
            nominal = int(line.split('span>')[1][:-2].replace('\xa0', ''))
        if line.count('Полное&nbsp;наименование') > 0:
            i = 4
    f.close()
    return name + ';' + codeISIN + ';' + placementDate + ';' + redemption + \
        ';' + str(nominal) + ';' + taxRate


# ******************************************************************************
# Функция парсинга страниц bonds.finam.ru с информацией о платежах по облига-
# ции. Результат - строка с совокупным купонным доходом, очищенным от налогов.
# ******************************************************************************
def parse_payments(fileName, taxRating, datePlacement):
    f = open(fileName, 'r', encoding='cp1251')
    sumPayments = 0
    for line in f:
        if line.count('<table border=0 cellspacing=0') > 0:
            for row in line.split('<tr'):
                if row.count('bline bg') > 0:
                    cell = row.split('<td')
                    rate = float(cell[3].replace('>', '&').replace(',', '.').
                                 split('&')[1][:-1])  # Ставка
                    coupon = float(cell[5].replace('>', '&').replace(',',
                                   '.').split('&')[1])  # Купон
                    sumPayments = sumPayments + coupon - tax(coupon, rate,
                                                             taxRating,
                                                             datePlacement)
    f.close()
    return str(sumPayments)


# ******************************************************************************
# Функция парсинга страниц bonds.finam.ru с информацией о результатах торгов по
# облигации. Результат - строка с ценой и НКД. Данные разделены точкой с
# запятой.
# ******************************************************************************
def parse_auction_result(fileName):
    f = open(fileName, 'r', encoding='cp1251')
    i = 0
    closePrice = 200
    askPrice = 200
    ACI = 200
    for line in f:
        if i == 1:
            row = line.replace('>', '<').split('<')[2].split('&')[0]
            if row.count('--') > 0:
                closePrice = 200
            else:
                closePrice = float(row.replace(',', '.'))
            i = 0
        if i == 2:
            row = line.replace('>', '<').split('<')[2].split('&')[0]
            if row.count('--') > 0:
                askPrice = 200
            else:
                askPrice = float(row.replace(',', '.'))
            i = 0
        if i == 3:  # НКД
            row = line.replace('>', '<').split('<')[2].split('&')[0]
            if row.count('--') > 0:
                ACI = 200
            else:
                ACI = float(row.replace(',', '.'))
            break
        if line.count('lose:') > 0:
            i = 1
        if line.count('Ask:') > 0:
            i = 2
        if line.count('&nbsp;НКД&nbsp;(руб):') > 0:
            i = 3
    f.close()
    if (closePrice == 200) or (closePrice < askPrice):
        closePrice = askPrice  # Цена закрытия
    return str(closePrice) + ';' + str(ACI)


# ******************************************************************************
#                       Текст основной программы
# ******************************************************************************

fileInput = open('input.txt', 'r')
fileOutput = open('output.txt', 'w')
i = 0
for line in fileInput:
    url = line.replace('/default.asp', '00001/default.asp')
    load_url(url)
    newData = parse_info('temp.html')
    arrInfo = newData.split(';')
    url = line.replace('/default.asp', '00002/default.asp')
    load_url(url)
    payments = parse_payments('temp.html', int(arrInfo[5]), arrInfo[2])
    result = newData.replace(arrInfo[2] + ';', '')[:-1]
    url = line.replace('/default.asp', '00008/default.asp')
    load_url(url)
    newData = parse_auction_result('temp.html')
    i = i + 1
    result = result + payments.replace('.', ',') + ';' + newData.replace('.',
                                                                         ',')
    print(str(i) + ';' + result)
    fileOutput.write(result + '\n')
fileInput.close()
fileOutput.close()
