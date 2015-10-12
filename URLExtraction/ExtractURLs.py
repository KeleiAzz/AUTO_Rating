# -*- coding: utf-8 -*-
__author__ = 'keleigong'
from GoogleScraper import scrape_with_config, GoogleSearchError
from openpyxl import Workbook
import csv


def create_query(keywords_file, companies_list):
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
        company_splited = company.split(' ')
        if company_splited[-1] in ["INC", "COPR"]:
            company = ' '.join(company_splited[0:-1])
        for word in keywords:
            query.append(company + ' ' + word)
    return query

def extract_urls(keywords_file, companies_list):
    '''Use GoogleScraper to extract URLs based on the combination of company name
    and keywords, it will store the result in a .csv file and return the path
    and name of the file.

    Input: the path of the keywords file and company list. Should be txt file
    or file without format.

    Output: it will automatically create a csv file to store all the query result
    and return the path of that file
    '''

    query = create_query(keywords_file, companies_list)
    config = {
        'SCRAPING': {
            'use_own_ip': False,
            'keywords': '\n'.join(query),  # 'keywords': '\n'.join(keywords),
            'check_proxies': False,
            # 'keyword_file': '/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/final_keywords',
            'search_engines': 'google',
            'num_pages_for_keyword': 1,
            'scrape_method': 'selenium',
            'num_workers': 5,
            # 'output_filename': '/Users/keleigong/Dropbox/Python/AUTO_Rating/output_test.csv'
        },
        'SELENIUM': {
            # 'num_workers': 10,
            'sel_browser': 'Phantomjs',
            # 'sel_browser': 'Chrome',
        },
        'GLOBAL': {
            # 'num_workers': 10,
            # 'google_sleeping_ranges': '5: 10, 20',
            'verbosity': 2,
            'manual_captcha_solving': True,
            'do_caching': 'True',
            'proxy_file': '/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/ProxyProvider/proxy.txt',
        },
        'OUTPUT': {
            'database_name': companies_list,
            'output_filename': companies_list + '.json'
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
    '''Convert the csv file created by extract_urls to excel file,
    and add the company's name to each row.
    :param path of csvfile:
    :param path of companies_list:
    :return: path of the excel file.
    '''
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
