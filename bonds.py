#******************************************************************************
#   Программа bonds.py считывает из файла new.txt URL-адреса, скачивает с сайта 
# bonds.finam.ru страницы с информацией об облигациях, выбирает оттуда необхо-
# димые данные и выводит их на экран.
#   Для запуска программы необходим Python 3.0
#   При выполнении в командной строке:
#   python bonds.py > bonds.txt
#   полученный файл bonds.txt можно открыть в MS Excel.
# 
#                    Copyright (c) 2018 Логинов М.Д.
# 
#  Разработчик: Логинов М.Д.
#  Модифицирован: 25 июля 2018 г.
#
#******************************************************************************

# -*- coding: utf-8 -*-
import string
import urllib.request

#******************************************************************************
#         Функция получения данных из Интернета и их анализа
#******************************************************************************

def read_new_data_from_internet(url):
	#Read from local file. Need read from Internet
    url1 = url.replace('/default.asp','00008/default.asp')
    response = urllib.request.urlopen(url1).read()
    f = str(response).split('\\r')
    # Следующая строка необходима для отладки offline
    #f=open('pif1.html','w',encoding='utf-8')
    j = 0
    nom = 1001  # Номинал облигации
    closePrice = '--'
    askPrice = '--'
    nkd = '0'
    for line in f:
        if (j == 1) & (len(line)>4):
            line2 = line.replace('>','<')
            str1 = line2.split('<')
            closedate = str1[2]  # Дата погашения
            j = 0
        if (j == 2) & (len(line)>4):
            line2 = line.replace('>','<')
            str1 = line2.split('<')
            closePrice = str1[2].split('&')[0]  # Цена закрытия
            j = 0
        if (j == 3) & (len(line)>4):
            line2 = line.replace('>','<')
            str1 = line2.split('<')
            askPrice = str1[2].split('&')[0]  # Минимальное предложение
            j = 0
        if (j == 4) & (len(line)>4):
            line2 = line.replace('>','<')
            str1 = line2.split('<')
            nkd = str1[2].split('&')[0]  # НКД
            break
        if line.count('h3') > 0:
            line2 = line.replace('>','<')
            str1 = line2.split('<')
            name = str1[2]  # Название облигации
        if line.count('\\xcd\\xee\\xec\\xe8\\xed\\xe0\\xeb') > 0:
            str1 = line.split('span>')
            str2 = str1[1][:-2]
            str3 = str2.split(',')
            k = int(str3[0].replace('\\xa0',''))
            if (nom > k):
                nom = k #Номинал
        if line.count('\\xca\\xee\\xe4 \\xcc\\xcc\\xc2\\xc1:') > 0:
            line2 = line.replace('>','<')
            str1 = line2.split('<')
            code = str1[6].split('&')[0][1:]  # Код ММВБ
        if line.count(
           '\\xc4\\xe0\\xf2\\xe0 \\xef\\xee\\xe3\\xe0\\xf8\\xe5\\xed\\xe8\\xff:'
           ) > 0:
            j = 1
        if line.count('lose:') > 0:
            j = 2
        if line.count('Ask:') > 0:
            j = 3
        if line.count('\\xcd\\xca\\xc4') > 0:
            j = 4
    url1 = url.replace('/default.asp','00002/default.asp')
    response = urllib.request.urlopen(url1).read()
    f = str(response).split('\\r')
    sum = 0  # Совокупный купонный доход
    for line in f:
        if line.count('<table border=0') > 0:
            strArr = line.split('<tr')
            break
    for line in strArr:
        if (line.count('<font color') == 0) & (line.count('bline') > 0):
            str1 = line.split('<td align=right>')
            str2 = str1[3]
            str1 = str2.split('&')
            sum = sum + float(str1[0].replace(',','.'))
    price = '--'
    if (closePrice=='--'):
        last = 200
    else:
        last = float(closePrice.replace(',','.'))
    if (askPrice=='--'):
        ask = 200
    else:
        ask = float(askPrice.replace(',','.'))
    if last == 200:
        last = ask
    if last < ask:
        last = ask
    price = str(last)
    strCSV = code + ';' + closedate + ';' + str(nom).replace('.',',') + ';' + \
             str(sum).replace('.',',') + ';' + price.replace('.',',') + ';' + \
             nkd
    return strCSV

#******************************************************************************
#                       Текст основной программы
#******************************************************************************

f = open('new.txt','r')
for url in f:
    newData = read_new_data_from_internet(url)
    print(newData)
f.close()
