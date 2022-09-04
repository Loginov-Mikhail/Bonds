# ******************************************************************************
#   Программа parse.py находит на сайте bonds.finam.ru URL-адреса с информацией
# об облигациях с погашением или офертой до введенного в программу срока и
# подготавливает файл input.txt с исходными данными для дальнейшего сбора
# информации по облигациям программой bonds.py.
#   Для запуска программы необходим Python 3.0
#   При выполнении в командной строке:
#   python3 parse.py
#                Copyright (c) 2020-2022 Логинов М.Д.
#  Разработчик: Логинов М.Д.
#  Создан:        04 декабря 2020 г.
#  Изменен:       04 сентября 2022 г.
# ******************************************************************************


import urllib.request
import datetime


# ******************************************************************************
# Функция парсинга страниц bonds.finam.ru с результатами поиска облигаций, по-
# гашаемых или выкупаемых по оферте к некоторой дате. Результат - список отно-
# сительных URL.
# ******************************************************************************
def parse_file(filename):
    f = open(filename, 'r', encoding='cp1251')
    a = []
    b = True
    result = 0
    for line in f:
        if b:
            i = line.find('Найдено')
            if i >= 0:
                result = int(line.split(';')[2].split('<')[0])
                b = False
        else:
            i = line.find('/issue/details')
            if i >= 0:
                if not (line[i:i+31] in a):
                    a.append(line[i:i+31])
    f.close()
    return result, a


# ******************************************************************************
# Процедура сохранения страницы во временный файл
# ******************************************************************************
def load_url(url):
    response = urllib.request.urlopen(url).read().decode('cp1251')
    f = open('temp.html', 'w', encoding='cp1251')
    f.write(response)
    f.close()


def input_data():
    finishDate = input('Введите максимально возможную дату погашения: ')
    finishDate = finishDate.replace('.', '%2F')
    startDate = datetime.date.today()
    startDate = startDate + datetime.timedelta(days=5)
    startDate = startDate.strftime('%d.%m.%Y').replace('.', '%2F')
    return startDate, finishDate


def select_bonds_by_redemption(startdate, finishdate):
    listA = []
    page = 0
    n = 1
    while 30 * page < n:
        url = f'https://bonds.finam.ru/issue/search/default.asp?page={page}&showEmitter=1&showStatus=&showSector=&' \
              f'showTime=&showOperator=&showMoney=&showYTM=&showLiquid=&emitterCustomName=&status=4&sectorId=&' \
              f'FieldId=0&placementFrom=&placementTo=&paymentFrom={startdate}&paymentTo={finishdate}&' \
              f'registrationDateFrom=&registrationDateTo=&couponRateFrom=&couponRateTo=&couponDateFrom=&' \
              f'couponDateTo=&offerExecDateFrom=&offerExecDateTo=&currencyId=1&volumeFrom=&volumeTo=&' \
              f'faceValueSign=&faceValue=&operatorId=0&operatorIdName=&opemitterCustomName=&operatorTypeId=0&' \
              f'operatorTypeName=&amortization=0&registrationDate=&regNumber=&govRegBody=&emissionForm1=&' \
              f'emissionForm2=&leaderDateFrom=&leaderDateTo=&placementMethod=0&quoteType=1&YTMOffer=on&YTMFrom=&' \
              f'YTMTo=&liquidRange=0&isRPS=0&liquidFrom=&liquidTo=&transactionsFrom=&transactionsTo=&liquidType=0&' \
              f'liquidTop=0&rating=&orderby=3&is_finam_placed='
        load_url(url)
        n, listB = parse_file('temp.html')
        listA = listA + listB
        page = page + 1
        print(n, page)
    return listA


def select_bonds_by_offer(startdate, finishdate):
    listA = []
    page = 0
    n = 1
    while 30 * page < n:
        url = f'https://bonds.finam.ru/issue/search/default.asp?page={page}&showEmitter=1&showStatus=&showSector=&' \
              f'showTime=&showOperator=&showMoney=&showYTM=&showLiquid=&emitterCustomName=&status=4&sectorId=&' \
              f'FieldId=0&placementFrom=&placementTo=&paymentFrom=&paymentTo=&registrationDateFrom=&' \
              f'registrationDateTo=&couponRateFrom=&couponRateTo=&couponDateFrom=&couponDateTo=&' \
              f'offerExecDateFrom={startdate}&offerExecDateTo={finishdate}&currencyId=1&volumeFrom=&volumeTo=&' \
              f'faceValueSign=&faceValue=&operatorId=0&operatorIdName=&opemitterCustomName=&operatorTypeId=0&' \
              f'operatorTypeName=&amortization=0&registrationDate=&regNumber=&govRegBody=&emissionForm1=&' \
              f'emissionForm2=&leaderDateFrom=&leaderDateTo=&placementMethod=0&quoteType=1&YTMOffer=on&YTMFrom=&' \
              f'YTMTo=&liquidRange=0&isRPS=0&liquidFrom=&liquidTo=&transactionsFrom=&transactionsTo=&liquidType=0&' \
              f'liquidTop=0&rating=&orderby=3&is_finam_placed='
        load_url(url)
        n, listB = parse_file('temp.html')
        listA = listA + listB
        page = page + 1
        print(n, page)
    return listA


# ******************************************************************************
#                       Текст основной программы
# ******************************************************************************
start, finish = input_data()
data = select_bonds_by_redemption(start, finish)
data = data + select_bonds_by_offer(start, finish)
fileOutput = open('input.txt', 'w')
for elem in data:
    fileOutput.write(f'https://bonds.finam.ru{elem}\n')
fileOutput.close()
