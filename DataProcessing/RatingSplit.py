from openpyxl import Workbook, load_workbook

filepath = '/Users/keleigong/Dropbox/Python/AUTO_Rating/DataProcessing/Cleaned data.xlsx'
output_filepath = ''

wb = load_workbook(filepath, read_only=True)

ws = wb['all ratings']

wb2 = Workbook(write_only=True)

ws2 = wb2.create_sheet(0,'ratings')

for row in ws.rows:
    for i in range(1,7,1):
        ws2.append(['1/1/' + str(row[6].value), row[6+i].value, '12/31/' + str(row[6].value), i, row[0].value])

wb2.save('ratings.xlsx')
