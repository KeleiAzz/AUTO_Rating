__author__ = 'keleigong'
from GoogleScraper import scrape_with_config, GoogleSearchError
from openpyxl import Workbook
import csv


def extract_urls(keywords_file, companies_list):
    file = open(keywords_file, 'r')
    keywords = file.read()
    file.close()
    file = open(companies_list, 'r')
    companies_list = file.read()
    file.close()
    keywords = keywords.split('\n')
    companies_list = companies_list.split('\n')
    query = []
    for company in companies_list:
        for word in keywords:
            query.append(company + ' ' + word)
    config = {
        'SCRAPING': {
            'use_own_ip': True,
            'keywords': '\n'.join(query),  # 'keywords': '\n'.join(keywords),
            'check_proxies': True,
            # 'keyword_file': '/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/final_keywords',
            'search_engines': 'google',
            'num_pages_for_keyword': 1,
            'scrape_method': 'http',
            'num_workers': 4,
            # 'output_filename': '/Users/keleigong/Dropbox/Python/AUTO_Rating/output_test.csv'
        },
        'SELENIUM': {
            'sel_browser': 'chrome',
        },
        'GLOBAL': {
            'do_caching': 'False',
            'proxy_file': '/Users/keleigong/Dropbox/Python/AUTO_Rating/proxy.txt',
        },
        'OUTPUT': {
            'output_filename': keywords_file + '.csv'
        }
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


def convert_to_excel(csvfile):
    wb = Workbook(write_only=True)
    ws = wb.create_sheet(0, 'raw_data')
    with open(csvfile, 'rt') as f:
        reader = csv.reader(f)
        for row in reader:
            ws.append(row)
            # print(row)
    wb.save(csvfile[:-3] + 'xlsx')
    return csvfile[:-3] + 'xlsx'

# See in the config.cfg file for possible values
