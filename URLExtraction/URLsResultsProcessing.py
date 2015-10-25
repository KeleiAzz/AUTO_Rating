__author__ = 'keleigong'

from openpyxl import load_workbook
from openpyxl import Workbook
import operator
import json

class SearchQuery(object):
    def __init__(self, company, query):
        self.company = company
        self.keyword = ' '.join(query['query'].split(' ')[len(company.split(' ')):])
        self.id = query['id']
        self.results = []
        for result in query['results']:
            if result['link_type'] == 'results' and result['link'][0:4] == 'http':
                self.results.append(SearchResult(company, result, self.keyword))

class SearchResult(object):
    def __init__(self, company, result, keyword):
        self.company = company
        self.domain = result['domain']
        self.id = result['id']
        self.link = result['link']
        self.link_type = result['link_type']
        self.rank = result['rank']
        self.serp_id = result['serp_id']
        self.snippet = result['snippet']
        self.title = result['title']
        self.visible_link = result['visible_link']
        self.count = 1
        self.keywords = [keyword]

    def set_link(self, link):
        self.link = link

    def __eq__(self, other):
        # print(self.link, other.link)
        if (isinstance(other, self.__class__)) and self.link == other.link:
            other.count += 1
            other.rank = min(self.rank, other.rank)
            other.keywords.append(self.keywords[0])
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

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
    return write_to_excel(urls_with_frequencies, filename)



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

def get_company_names(file_path):
    file = open(file_path, 'r')
    companies_names = file.read()
    file.close()
    companies_names = companies_names.split('\n')
    for i in range(len(companies_names)):
        company_splited = companies_names[i].split(' ')
        if company_splited[-1] in ["INC"]:
            companies_names[i] = ' '.join(company_splited[0:-1])
            # print(companies_names[i])
    return companies_names

def json_processing(json_file, company_file):
    file = open(json_file)
    json_str = file.read()
    file.close()
    json_data = json.loads(json_str)
    company_names = get_company_names(company_file)
    company_json = {}
    for name in company_names:
        company_json[name] = []
    for line in json_data:
        for name in company_names:
            if name in line['query']:
                company_json[name].append(line)
                break
    return company_json


def query_processing(company_json):
    company_querys = {}
    for company in company_json.keys():
        company_querys[company] = []
    for company, querys in company_json.items():
        for query in querys:
            company_querys[company].append(SearchQuery(company, query))
    return company_querys

def remove_irrelevant_urls(company_querys):
    keywords_to_delete = ['linkedin', 'linkup', 'disabledperson', 'indeed', 'simplyhired',
                          'career', 'recruit', 'glassdoor', 'jobs', 'monster.com', 'yelp', 'itunes',
                          'googleadservices', 'wiki', 'www.google.com', 'amazon.com']
    company_all_urls = {}
    for company, querys in company_querys.items():
        company_all_urls[company] = []
        for query in querys:
            for result in query.results:
                if any(k in result.domain for k in keywords_to_delete):
                    continue
                if result in company_all_urls[company]:
                    pass
                else:
                    company_all_urls[company].append(result)
    for company, urls in company_all_urls.items():
        urls.sort(key=lambda x: x.count,reverse=True)
        company_all_urls[company] = list(filter(lambda x: x.count>2, urls))
    return company_all_urls

def write_to_xlsx(company_all_urls, filename):
    wb2 = Workbook(filename)
    sheet = wb2.create_sheet(0, 'output')
    # sheet.append(['link', 'frequency', 'company', 'rank', 'year', 'query',
    #               'link_type', 'title', 'domain', 'snippet', 'year'])
    # sheet.append(company_all_urls)
    for company, urls in company_all_urls.items():
        sheet.append(list(urls[0].__dict__.keys()))
        for url in urls:
            url.keywords = ', '.join(url.keywords)
            row = [value for key, value in url.__dict__.items()]
            sheet.append(row)

    wb2.save(filename)
    return filename

# company_json = json_processing('/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/concinnity_600/1-50.json',
#                                '/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/concinnity_600/1-50')
# company_querys = query_processing(company_json)
#
# company_all_urls = remove_irrelevant_urls(company_querys)
#
# write_to_xlsx(company_all_urls, "1-50.xlsx")
# print(get_company_names('/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/concinnity_600/1-50'))
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
