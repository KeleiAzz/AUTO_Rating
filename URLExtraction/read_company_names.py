__author__ = 'keleigong'
from os import listdir
from os.path import isfile, join
from openpyxl import load_workbook
from openpyxl import Workbook


mypath = '/Users/keleigong/Google Drive/SCRC 2015 work/2014_data/third run/d.sentences/ES/'
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
if onlyfiles.count('.DS_Store') > 0:
    onlyfiles.pop(onlyfiles.index('.DS_Store'))
onlyfiles.pop(onlyfiles.index('ES.csv'))
onlyfiles = [name.replace('.txt', '').strip() for name in onlyfiles if name.count('txt')]

# print(onlyfiles)

wb = load_workbook('/Users/keleigong/Google Drive/SCRC 2015 work/2014_data/third run/human_rating_all.xlsx')
ws = wb.get_active_sheet()

out = Workbook(write_only=True)
rating = out.create_sheet(0, 'rating')

dir_num = 0
rating_num = 0
names = []
rating.append(['company', 'sm', 'ss', 'cm', 'srm', 'lhr', 'es'])
for row in ws.rows:
    if any(x in row[0].value for x in onlyfiles):
        rating.append([cell.value for cell in row])
        names.append(row[0].value)

for i in range(len(onlyfiles)):
    if names.count(onlyfiles[i]) == 0:
        print(onlyfiles[i])

out.save('es.xlsx')