import xlrd
import re
import pandas, os, shutil
import datetime
import csv
workDir = "C:/Users/Engineer/"
search_text = 'Номер пожара'


def find_first_raw(file_xls):
    print("Searching text")
    workbook = xlrd.open_workbook(workDir+file_xls)
    sheet = workbook.sheet_by_index(0)
    global row_max
    row_max = sheet.nrows # Number of lines
    global column_max
    column_max = sheet.ncols # columns
    row_min = 0 
    column_min = 0 
    while column_min <= column_max-1:
        row_min_min = row_min
        row_max_max = row_max
        while row_min_min <= row_max_max-1:
            data_from_cell = sheet.cell(row_min_min, column_min).value
            data_from_cell = str(data_from_cell)
            regular = search_text
            result = re.findall(regular, data_from_cell)
            if len(result) > 0:
                first_row_of_data = (row_min_min + 2, column_min)
            row_min_min = row_min_min + 1
        column_min = column_min + 1
    return first_row_of_data[0]
def convertCoord(inCoord):
    # Пример входа
    # inCoord = "44°32'06""  132°45'14"" "
    try:
        latLong = inCoord.split("  ")

        lat = latLong[0].split("°")
        lat23 = lat[1].split("'")
        latDecimal = float(lat[0]) + (float(lat23[0])/60) + (float(lat23[0])/3600)

        long = latLong[1].split("°")
        long23 = long[1].split("'")
        longDecimal = float(long[0]) + (float(long23[0])/60) + (float(long23[0])/3600)
        result = "["+ str(longDecimal) + "," + str(latDecimal) + "]"
    except Exception:
        result = ""
    return result

try:
    for fileName in os.listdir(workDir):
        if fileName.endswith(".xls"):
            global file_xls
            file_xls = fileName
            excel_data = pandas.read_excel(workDir+fileName, skiprows=find_first_raw(file_xls), header=None)
            print("opening file")
            dataFrame_data = pandas.DataFrame(excel_data)
            # Drop last row
            dataFrame_data.drop(dataFrame_data.tail(1).index,inplace=True)
            len_df = len(dataFrame_data)
            # Create new column 
            dataFrame_data['coord'] = dataFrame_data.apply(lambda row: convertCoord(row[1]) , axis=1)
            dataFrame_data.to_csv(workDir + 'outcome/'+file_xls+'.csv')
            with open(workDir + 'success.csv', mode="a", encoding='utf-8') as w_file:
                file_writer = csv.writer(w_file, delimiter = ",", lineterminator="\r")
                file_writer.writerow([datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'), file_xls, row_max, column_max, len_df])
            shutil.move(workDir+file_xls, workDir+'processed/'+file_xls)
except Exception as exc:
    with open(workDir + 'error.log', 'a') as err_file:
        print(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'), fileName , "FAILED because", exc, file = err_file)
