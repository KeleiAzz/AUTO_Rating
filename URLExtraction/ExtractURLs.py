__author__ = 'keleigong'
from GoogleScraper import scrape_with_config, GoogleSearchError
from openpyxl import Workbook
import csv


def extract_urls(keywords_file, companies_list):
    file = open(keywords_file, 'r')
    keywords = file.read()
    file.close()
    file = open(companies_list, 'r')
    companies_names = file.read()
    file.close()
    keywords = keywords.split('\n')
    companies_names = companies_names.split('\n')
    query = []
    for company in companies_names:
        for word in keywords:
            query.append(company + ' ' + word)
    config = {
        'SCRAPING': {
            'use_own_ip': True,
            'keywords': '\n'.join(query),  # 'keywords': '\n'.join(keywords),
            'check_proxies': False,
            # 'keyword_file': '/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/final_keywords',
            'search_engines': 'google',
            'num_pages_for_keyword': 1,
            'scrape_method': 'selenium',
            # 'num_workers': 7,
            # 'output_filename': '/Users/keleigong/Dropbox/Python/AUTO_Rating/output_test.csv'
        },
        'SELENIUM': {
            'num_workers': 2,
            'sel_browser': 'phantomjs',
        },
        'GLOBAL': {
            # 'num_workers': 7,
            'google_sleeping_ranges': '5: 5, 10',
            'verbosity': 2,
            'manual_captcha_solving': True,
            # 'do_caching': 'False',
            'proxy_file': '/Users/keleigong/Dropbox/Python/AUTO_Rating/proxy.txt',
        },
        'OUTPUT': {
            'output_filename': companies_list + '.csv'
        },
    }

    try:
        search = scrape_with_config(config)
    except GoogleSearchError as e:
        print(e)

    if companies_list.count('.') > 0:
        return companies_list[:companies_list.index('.')] + ',csv'
    else:
        return companies_list + '.csv'

    # let's inspect what we got

    # for serp in search.serps:
    #     print(serp)
    #     print(serp.search_engine_name)
    #     print(serp.scrape_method)
    #     print(serp.page_number)
    #     print(serp.requested_at)
    #     print(serp.num_results)
    #     ... more attributes ...
        # for link in serp.links:
        #     print(link)


def convert_to_excel(csvfile, companies_list):
    file = open(companies_list, 'r')
    companies_list = file.read()
    companies_list = companies_list.split('\n')
    file.close()
    wb = Workbook(write_only=True)
    ws = wb.create_sheet(0, 'raw_data')
    row_num = 0
    company_name = 'xxxxx'
    with open(csvfile, 'rt') as f:
        reader = csv.reader(f)
        for row in reader:
            if row_num == 0:
                query = row.index('query')
                row.insert(0, 'company')
                row_num += 1
            else:
                if company_name in row[query]:
                    row.insert(0, company_name)
                else:
                    company_name = [c for c in companies_list if c in row[query]][0]
                    row.insert(0, company_name)
            ws.append(row)
            # print(row)
    wb.save(csvfile[:-3] + 'xlsx')
    return csvfile[:-3] + 'xlsx'

# See in the config.cfg file for possible values
