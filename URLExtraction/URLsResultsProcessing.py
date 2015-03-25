__author__ = 'keleigong'

from openpyxl import load_workbook
from openpyxl import Workbook
import operator


wb = load_workbook(filename='/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/ea_all_keywords.xlsx')
ws = wb.get_active_sheet() # ws is now an IterableWorksheet

column_name = list(map(lambda c: c.value, ws.rows[0]))
# print(column_name)
query = column_name.index('query')
print(query)
link_type = column_name.index('link_type')
domain = column_name.index('domain')
link = column_name.index('link')
snippet = column_name.index('snippet')
rank = column_name.index('rank')
title = column_name.index('title')
years = ['2011', '2012', '2013', '2014', '2015']
urls_with_frequencies = {}

keywords_to_delete = ['linkedin', 'linkup', 'disabledperson', 'indeed', 'simplyhired',
                      'career', 'recruit', 'glassdoor', 'jobs', 'monster.com', 'yelp', 'itunes',
                      'googleadservices', 'wiki', 'www.google.com']
for row in ws.rows:
    if any(k in row[domain].value for k in keywords_to_delete):
        pass
    else:
        print(row[query].value)
        if row[query].value.split(' ')[0] not in urls_with_frequencies.keys():
            company = row[query].value.split(' ')[0]
            urls_with_frequencies[row[query].value.split(' ')[0]] = {}
        else:
            company = row[query].value.split(' ')[0]
        if row[link].value not in urls_with_frequencies[company].keys():
            urls_with_frequencies[company][row[link].value] = [1,
                                                            row[query].value.split(' ')[0],
                                                            row[rank].value,
                                                            row[query].value,
                                                            row[link_type].value,
                                                            row[title].value,
                                                            row[domain].value,
                                                            row[snippet].value]
            if row[snippet].value is not None:
                year = [y for y in years if y in row[snippet].value[:15]]
            else:
                year = []
            if len(year) > 0:
                urls_with_frequencies[company][row[link].value].insert(3, year[0])
            else:
                urls_with_frequencies[company][row[link].value].insert(3, ' ')
            # if any(x in row[snippet][:15] for x in years):
                # urls_with_frequencies[row[link].value].append
        else:
            urls_with_frequencies[company][row[link].value][0] += 1
            urls_with_frequencies[company][row[link].value][4] += ', ' + row[query].value
urls_with_frequencies.pop('query')

for company in urls_with_frequencies.keys():
    urls_with_frequencies[company] = sorted(urls_with_frequencies[company].items(),
                                            key=lambda x: x[1][0], reverse=True)


wb2 = Workbook(write_only=True)
sheet = wb2.create_sheet(0, 'output')
sheet.append(['link', 'frequency', 'company', 'rank', 'year', 'query',
              'link_type', 'title', 'domain', 'snippet', 'year'])
for company in urls_with_frequencies.keys():
    for url in urls_with_frequencies[company]:
        url[1].insert(0, url[0])
        sheet.append(url[1])
        pass

wb2.save('URL_with_frequency_ea_all.xlsx')


# company = {}
# count = {}
# for row in ws.rows:
#     tmp = row[0].value.split(' ')[0]
#     if tmp in company.keys():
#         if row[1].value in company[tmp]:
#             count[tmp][company[tmp].index(row[1].value)] += 1
#         else:
#             company[tmp].append(row[1].value)
#             count[tmp].append(1)
#     else:
#         company[tmp] = []
#         count[tmp] = []
# count.pop('query')
# company.pop('query')
