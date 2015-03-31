__author__ = 'keleigong'

from openpyxl import load_workbook
from openpyxl import Workbook
import operator


def urls_processing(filename):
    '''
    Preprocessing the urls, delete unreliable urls, change the table format,
    count the frequency, etc.
    :param filename(path):
    :return: create a excel file to store the result.
    '''
    wb = load_workbook(filename=filename)
    ws = wb.get_active_sheet()  # ws is now an IterableWorksheet

    column_index = get_column_index(ws)
    # print(column_index)
    urls_with_frequencies = worksheet_processing(ws, column_index)
    # print(urls_with_frequencies)
    write_to_excel(urls_with_frequencies, filename)


def worksheet_processing(ws, ci):
    '''

    :param ws:
    :param ci:
    :return:
    '''
    years = ['2011', '2012', '2013', '2014', '2015']
    keywords_to_delete = ['linkedin', 'linkup', 'disabledperson', 'indeed', 'simplyhired',
                          'career', 'recruit', 'glassdoor', 'jobs', 'monster.com', 'yelp', 'itunes',
                          'googleadservices', 'wiki', 'www.google.com']
    urls_with_frequencies = {}
    for row in ws.rows:

        if row[ci['domain']].value is not None and any(k in row[ci['domain']].value for k in keywords_to_delete):
            pass
        else:
            # print(row[ci['query']].value)
            if row[ci['company']].value not in urls_with_frequencies.keys():
                company = row[ci['company']].value
                urls_with_frequencies[company]= {}
            else:
                company = row[ci['company']].value

            if row[ci['link']].value not in urls_with_frequencies[company].keys():
                urls_with_frequencies[company][row[ci['link']].value] = [1,
                                                                row[ci['company']].value,
                                                                row[ci['rank']].value,
                                                                row[ci['query']].value,
                                                                row[ci['link_type']].value,
                                                                row[ci['title']].value,
                                                                row[ci['domain']].value,
                                                                row[ci['snippet']].value]
                if row[ci['snippet']].value is not None:
                    year = [y for y in years if y in row[ci['snippet']].value[:15]]
                else:
                    year = []
                if len(year) > 0:
                    urls_with_frequencies[company][row[ci['link']].value].insert(3, year[0])
                else:
                    urls_with_frequencies[company][row[ci['link']].value].insert(3, ' ')
                # if any(x in row[snippet][:15] for x in years):
                    # urls_with_frequencies[row[link].value].append
            else:
                urls_with_frequencies[company][row[ci['link']].value][0] += 1
                urls_with_frequencies[company][row[ci['link']].value][4] += ', ' + row[ci['query']].value
    urls_with_frequencies.pop('company')
    print(urls_with_frequencies.keys())
    for company in urls_with_frequencies.keys():
        urls_with_frequencies[company] = sorted(urls_with_frequencies[company].items(),
                                                key=lambda x: x[1][0], reverse=True)
    return urls_with_frequencies


def get_column_index(ws):
    column_name = list(map(lambda c: c.value, ws.rows[0]))
    column_index = {}
    column_index['company'] = column_name.index('company')
    column_index['query'] = column_name.index('query')
    column_index['link_type'] = column_name.index('link_type')
    column_index['domain'] = column_name.index('domain')
    column_index['link'] = column_name.index('link')
    column_index['snippet'] = column_name.index('snippet')
    column_index['rank'] = column_name.index('rank')
    column_index['title'] = column_name.index('title')

    return column_index


def write_to_excel(urls, filename):
    # wb2 = Workbook(write_only=True)
    wb2 = load_workbook(filename)
    sheet = wb2.create_sheet(0, 'output')
    sheet.append(['link', 'frequency', 'company', 'rank', 'year', 'query',
                  'link_type', 'title', 'domain', 'snippet', 'year'])
    for company in urls.keys():
        for url in urls[company]:
            url[1].insert(0, url[0])
            sheet.append(url[1])
            pass
    wb2.save(filename)
    return filename

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
