--Скрипт получения данных о текущей цене и НКД облигаций, выбранных для покупки
--
--Создан: 10.03.2020
--Изменен: 24.10.2022

COLUMN_PRICE = 6
COLUMN_ACI = 7
COLUMN_ISIN_CODE = 2
LIST_OF_CLASS_CODE = {"EQOB", "TQCB", "TQOB"}

function split_line(line)
  local i = 1
  local part1 = ""
  local part2 = ""
  local code = ""
  for substring in string.gmatch(line, "[^;]+") do
    if i < COLUMN_PRICE then
      if i > 1 then
        part1 = part1..";"..substring
      else
        part1 = substring
      end
    end
    if i > COLUMN_ACI then
      if i - 1 > COLUMN_ACI then
        part2 = part2..";"..substring
      else
        part2 = substring
      end
    end
    if i == COLUMN_ISIN_CODE then
      code = substring
    end
    i = i + 1
  end
  return code, part1, part2
end

function read_csv(fileName)
  local tableResult = {}
  local title = ""
  local i = 0
  local fileCSV = io.open(fileName,"r")
  for line in fileCSV:lines() do
    if i == 0 then
      title = tostring(line)
    else
      tableResult[i] = {}
      tableResult[i]["codeISIN"], tableResult[i]["startPart"], tableResult[i]["lastPart"] = split_line(tostring(line))
    end
    i = i + 1
  end
  fileCSV:close()
  return title, tableResult
end

function read_tickers()
  local k = getNumberOf("securities")
  local i = 1
  local tableTickers = {}
  while (i < k) do
    secCode = getItem("securities",i)
    tableTickers[i] = {}
    tableTickers[i]["codeISIN"] = secCode["isin_code"]
    tableTickers[i]["ticker"] = secCode["code"]
    i = i + 1
  end
  return tableTickers
end

function search_ticker(codeISIN, tableTickers)
  local result = " "
  for i = 1, #tableTickers do
    if codeISIN == tableTickers[i]["codeISIN"] then
      result = tableTickers[i]["ticker"]
      break
    end
  end
  return result
end

function get_parameter_value(ticker, parameter)
  local value = 0
  for i, classCode in ipairs(LIST_OF_CLASS_CODE) do
    Status =  getParamEx(classCode, ticker, parameter)
    if tonumber(Status["param_value"]) > value then
      value = tonumber(Status["param_value"])
    end
    Status =  getParamEx2(classCode, ticker, parameter)
    if tonumber(Status["param_value"]) > value then
      value = tonumber(Status["param_value"])
    end
  end
  return value
end

function save_csv(title, tableResult, fileName)
  f = io.open(fileName,"w")
  f:write(title.."\n")
  for i = 1, #tableResult do
    f:write(tableResult[i]["startPart"]..";"..tableInfo[i]["price"]..";"..tableInfo[i]["ACI"]..";"..tableResult[i]["lastPart"].."\n")
  end
  f:close()
end

--Создание таблицы для вывода результатов на экран
function show_table(tableResult)
  t_results=AllocTable()
  AddColumn(t_results, 1, "ISIN", true, QTABLE_STRING_TYPE, 10)
  AddColumn(t_results, 2, "Цена", true, QTABLE_STRING_TYPE, 20)
  AddColumn(t_results, 3, "НКД", true, QTABLE_STRING_TYPE, 20)
  CreateWindow(t_results)
  SetWindowCaption(t_results, "Цены и НКД для выбора облигаций на покупку")
  for i = 1, #tableResult do
    row = InsertRow(t_results, -1)
    SetCell(t_results, row, 1, tableResult[i]["codeISIN"])
    SetCell(t_results, row, 2, tostring(tableInfo[i]["price"]))
    SetCell(t_results, row, 3, tostring(tableInfo[i]["ACI"]))
  end
end

function main()
  tickers = read_tickers()
  title, tableInfo = read_csv(getScriptPath().."\\output.csv")
  for i = 1, #tableInfo do
    ticker = search_ticker(tableInfo[i]["codeISIN"], tickers)
    if ticker == " " then
      price = 200
      aci = 0
    else
      aci = get_parameter_value(ticker, "accruedint")
      price = get_parameter_value(ticker, "offer")
    end
    if price == 0 then
      price = 200
    end
    tableInfo[i]["price"] = price
    tableInfo[i]["ACI"] = aci
  end
  save_csv(title, tableInfo, getScriptPath().."\\output.csv")
  show_table(tableInfo)
end
