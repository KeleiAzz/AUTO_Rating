__author__ = 'keleigong'
from openpyxl import load_workbook
from openpyxl import Workbook

wb = load_workbook(filename='/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/URL_with_frequency_LHR_2.xlsx')
ws = wb['output']

column_name = list(map(lambda c: c.value, ws.rows[0]))
domain = column_name.index('domain')

keywords_to_delete = ['linkedin', 'linkup', 'disabledperson', 'indeed', 'simplyhired',
                      'career', 'recruit', 'glassdoor', 'jobs', 'monster.com', 'yelp', 'itunes',
                      'googleadservices', 'wiki', 'www.google.com']

for row in ws.rows:
    if any(k in row[domain].value for k in keywords_to_delete):
        print(row[domain].value)