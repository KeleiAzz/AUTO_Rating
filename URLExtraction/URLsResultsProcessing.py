__author__ = 'keleigong'

# from openpyxl import load_workbook
from openpyxl import Workbook
import operator
import json



category = {'Ariba spend management':	['SM', 'SS', 'CM'],
            'Beroe':	['CM'],
            'California Transparency Supply Chain':	['LHR'],
            'Category Management':	['CM'],
            'Category team':	['CM'],
            'Child labor':	['LHR'],
            'citizenship report':	['LHR', 'ES'],
            'Continuous supplier improvement process':	['SS', 'SRM'],
            'Cross-functional category management team':	['CM'],
            'Cross-functional sourcing team':	['SS', 'CM'],
            'CSR report':	['LHR', 'ES'],
            'EDI':	['SM', 'SS'],
            'EHS':	['LHR'],
            'EICC':	['SM', 'SS', 'LHR', 'ES'],
            'Electronic Industry Citizenship Coalition':	['SM', 'SS', 'LHR', 'ES'],
            'Enterprise Resource Planning':	['SM', 'SS', 'CM'],
            'Environmental Sustainability':	['ES'],
            'e-procurement system':	['SM', 'SS'],
            'ERP':	['SM', 'SS', 'CM'],
            'Fair Labor Association':	['LHR'],
            'Global sourcing':	['SRM'],
            'Green effort':	['ES'],
            'Health Safety Security Environment':	['SS'],
            'Human Rights':	['LHR'],
            'Labor Right':	['LHR'],
            'Long-term category strategy':	['CM'],
            'Long-term sourcing strategy':	['SS'],
            'Minimum Wage':	['LHR'],
            'Non-governmental Organization':	['LHR'],
            'Oracle':	['SM', 'SS', 'CM'],
            'Procurement':	['SM', 'SS'],
            'Procurement allocation':	['SS'],
            'Procurement team':	['SM'],
            'Procure-to-Pay system':	['SM', 'SS'],
            'Product life cycle':	['ES'],
            'Responsible sourcing':	['LHR', 'ES'],
            'Responsible supply chain management':	['LHR', 'ES'],
            'SAP':	['SM', 'SS', 'CM'],
            'Second tier supplier audit':	['LHR', 'ES'],
            'Second tier supplier enforcement':	['LHR', 'ES'],
            'Service Level Agreement':	['SM', 'SS'],
            'Source approved vendor list':	['SM', 'SRM'],
            'Sourcing contract management system':	['SM', 'SS'],
            'Sourcing Process':	['SM', 'SS'],
            'Sourcing standards':	['SM', 'SS', 'CM', 'SRM', 'LHR', 'ES'],
            'Sourcing strategy':	['SS'],
            'Spend analytics':	['SM', 'SS', 'CM'],
            'Spend management':	['SM', 'SS', 'CM'],
            'SRM policy':	['SRM'],
            'Strategic sourcing':	['SS'],
            'Supplier':	['SM', 'SS', 'CM', 'SRM'],
            'Supplier  capacity':	['SS', 'CM'],
            'Supplier allocation':	['SM', 'SS', 'CM'],
            'Supplier assessment':	['SM', 'SS'],
            'Supplier audit':	['SM', 'SS'],
            'Supplier award':	['SM', 'SS', 'SRM'],
            'Supplier code of conduct':	['SM', 'SS', 'SRM', 'LHR', 'ES'],
            'Supplier collaboration':	['SS', 'CM', 'SRM'],
            'Supplier continuity planning':	['SS', 'SRM'],
            'Supplier database':	['SM'],
            'Supplier development plan':	['SS', 'SRM'],
            'Supplier diversity program':	['SM', 'SS'],
            'Supplier enforcement program':	['LHR', 'ES'],
            'Supplier environmental engagement':	['ES'],
            'Supplier evaluation':	['SM', 'SS'],
            'Supplier expectation':	['SM', 'SS'],
            'Supplier feedback':	['CM', 'SRM'],
            'Supplier guideline':	['SM', 'SS'],
            'Supplier lawsuit':	['LHR', 'ES'],
            'Supplier list':	['SM', 'SRM'],
            'Supplier management':	['SM', 'SS', 'SRM'],
            'Supplier measurements':	['SM', 'SS'],
            'Supplier meeting':	['SS', 'SRM'],
            'Supplier optimization':	['SS', 'CM'],
            'Supplier portal':	['SM', 'SS', 'SRM'],
            'Supplier purchase terms and conditions':	['SM', 'SS', 'SRM'],
            'Supplier registration':	['SM'],
            'Supplier Relationship Management':	['SRM'],
            'Supplier requirement':	['SM', 'SS', 'CM', 'SRM'],
            'Supplier risk management':	['SS', 'CM'],
            'Supplier scorecard':	['SM', 'SS', 'CM'],
            'Supplier segmentation':	['SS', 'CM'],
            'Supplier selection':	['SM', 'SS'],
            'Supplier summit':	['SS', 'SRM'],
            'Supplier terminate':	['SM'],
            'Supplier tracking':	['SM', 'SS', 'LHR', 'ES'],
            'Supplier training':	['SM', 'SS', 'LHR', 'ES'],
            'Supplier verification':	['SS'],
            'Supply base capacity':	['SS', 'CM'],
            'Supply chain management':	['SM', 'SS', 'CM', 'SRM'],
            'Supply management system':	['SM', 'SS', 'CM', 'SRM'],
            'Supply market analysis':	['CM'],
            'Supply market intelligence':	['CM'],
            'Supply risk analysis':	['SS', 'CM'],
            'Sustainability report':	['LHR', 'ES'],
            'Talent management':	['SRM'],
            'Vendor code of conduct':	['SM', 'SS', 'SRM', 'LHR', 'ES'],
            'Vendor expectation':	['SM', 'SS', 'SRM'],
            'Vendor list':	['SM', 'SRM'],
            'Vendor management':	['SM', 'SS', 'SRM'],
            'Vendor portal':	['SM', 'SS', 'CM', 'SRM'],}

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
        self.categories = []
        for keyword in self.keywords:
            self.categories += category[keyword.strip()]
        self.categories = list(set(self.categories))

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

def get_company_names(file_path):
    file = open(file_path, 'r')
    companies_names = file.read()
    file.close()
    companies_names = companies_names.split('\n')
    for i in range(len(companies_names)):
        company_splited = companies_names[i].split(' ')
        if company_splited[-1] in ["INC", 'CORP']:
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
    # tmp = list(company_all_urls)
    # sheet.append(list(urls[0].__dict__.keys()))
    flag = 1
    for company, urls in company_all_urls.items():
        if flag == 1:
            sheet.append(list(urls[0].__dict__.keys()))
            flag = 0
        for url in urls:
            url.keywords = ', '.join(url.keywords)
            url.categories = ','.join(url.categories)
            row = [value for key, value in url.__dict__.items()]
            sheet.append(row)

    wb2.save(filename)
    return filename

company_json = json_processing('/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/concinnity_600/1-53.json',
                               '/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/concinnity_600/1-53')
company_querys = query_processing(company_json)

company_all_urls = remove_irrelevant_urls(company_querys)


# def URLbyCategory(company_all_urls):




write_to_xlsx(company_all_urls, "1-53.xlsx")
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
