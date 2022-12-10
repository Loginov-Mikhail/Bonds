﻿# Bonds

Настоящий набор скриптов предназначен для создания скинера российских облигаций в формате xlsx. В полученном скринере рассчитывается доходность рублевых облигаций с погашением или офертой в период временим от текущей до введенной даты при использовании стратегии "Купил и держи до погашения".

## Установка скриптов

Для корректной работы необходим терминал QUIK и Python 3 с установленными пакетами [Pandas](https://pandas.pydata.org/), [lxml](https://lxml.de/), [BeautifulSoup4](https://github.com/wention/BeautifulSoup4), [html5lib](https://github.com/html5lib/html5lib-python), [openpyxl](https://github.com/theorchard/openpyxl).

<!-- termynal -->

```
$ pip install pandas
$ pip install lxml
$ pip install bs4
$ pip install html5lib
$ pip install openpyxl
```

Папку Bonds, содержащую скрипты Python, скопировать в любое удобное место. Папку BondsPrice со скриптом lua скопировать в место доступное для QUIK. Например, при использовании Linux и wine, это может быть ~/.wine/drive_c/Quik/Scripts.

## Формирование скринера

1. Построение списка облигаций с погашением или офертой в период времени от текущей до введенной даты по информации портала bonds.finam.ru осуществляется при помощи скрипта parse.py из папки Bonds. В результате работы скрипта в текущей папке формируется файл input.txt, содержащий URL-адреса с более подробной информацией о выбранных облигациях.

<!-- termynal -->

```
$ cd Bonds
$ python3 parse.py
```

2. Для построения таблицы с данными по облигациям на основе списка из файла input.txt по информации портала bonds.finam.ru используется скрипт bonds.py:


<!-- termynal -->

```
$ python3 bonds.py
```

В результате его работы в текущей папке появляется файл output.csv, который необходимо скопировать в папку BondsPrice для дальнейшей обработки в QUIK.

3. Для получения текущих значений цен облигаций и НКД необходимо запустить QUIK во время торговой сессии. В торговом терминале нужно запустить скрипт BondsPrice.lua. Поскольку при работе терминала передача данных по торгам может начинаться не моментально (личное наблюдение), рекомендуется запускать скрипт до тех пор, пока последние три результата не будут одинаковыми.
Для облегчения дальнейших расчетов принято допущение о цене 200 для облигаций не выставленных на продажу в текущий момент.
Результаты работы скрипта выводятся в таблицу в терминале QUIK и сохраняются в папке скрипта в файл output.csv.

4. Для формирования окончательного вида скринера необходимо скопировать полученный файл output.csv в папку Bonds и запустить скрипт to_excel.py:

<!-- termynal -->

```
$ python3 to_excel.py
```

Результатом является файл output.xlsx, который можно открыть в табличном процессоре Microsoft Excel или LibreOffice Calc. Дальнейшие действия (корректировка суммы покупки, сортировка результатов) осуществляются средствами табличного процессора.

## Планы по доработке
1. Объединение скриптов parse.py и bonds.py.
2. Создание конфигурационного файла для хранения настроек, например, пути к файлу output.csv.
3. Добавление в таблицу даты оферты.
4. Исправление доступа к сайту bonds.finam.ru.
