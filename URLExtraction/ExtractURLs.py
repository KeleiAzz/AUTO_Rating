# -*- coding: utf-8 -*-
__author__ = 'keleigong'
from GoogleScraper import scrape_with_config, GoogleSearchError
from openpyxl import Workbook
import csv
import os

def create_query(keywords_file, companies_list):
    '''
    combine company names and keywords to create search query.
    :param keywords_file: a file contains keywords, one keyword per line
    :param companies_list: contains company names, one company per line
    :return:
    '''
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
        # company_splited = company.split(' ')
        # if company_splited[-1] in ["INC", "CORP"]:
        #     company = ' '.join(company_splited[0:-1])
        for word in keywords:
            query.append(company + ' ' + word)
    return query


def extract_urls(keywords_file, companies_list, proxy_list=None):
    '''
    Use GoogleScraper to extract URLs based on the combination of company name
    and keywords, it will store the result in a .csv file and return the path
    and name of the file.

    Input: the path of the keywords file and company list. Should be txt file
    or file without format.

    Output: it will automatically create a json file and a sqlite db file to store all the query result
    and return the path of that file
    '''
    if proxy_list:
        proxy_file = proxy_list
    else:
        full_path = os.path.realpath(__file__)
        path, filename = os.path.split(full_path)
        # print(path, filename)
        proxy_file = os.path.join(path, "ProxyProvider", "proxy.txt")

    query = create_query(keywords_file, companies_list)
    config = {
        'use_own_ip': False,
        'keywords': query,
        'check_proxies': False,
        'search_engines': 'google',
        'stop_on_detection': False,
        # 'google_sleeping_ranges': 5,
        'num_pages_for_keyword': 1,
        'scrape_method': 'selenium',  # http or selenium
        'sel_browser': 'Phantomjs',
        'num_workers': 1,
        'verbosity': 2,
        'do_caching': False,
        # 'sleeping_ranges': '5: 5, 10',
        'google_search_url': 'http://www.google.com/search?',
        'proxy_file': proxy_file,
        'output_filename': companies_list + '.json',
        'database_name': companies_list,
    }

    try:
        search = scrape_with_config(config)
    except GoogleSearchError as e:
        print(e)

    if companies_list.count('.') > 0:
        return companies_list[:companies_list.rindex('.')] + '.json'
    else:
        return companies_list + '.json'

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
    '''
    This function is not in use
    Convert the csv file created by extract_urls to excel file,
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

if __name__ == "__main__":
    print(os.getcwd())
    print(__file__)
    print(os.path.realpath(__file__))
    full_path = os.path.realpath(__file__)
    path, filename = os.path.split(full_path)
    print(path, filename)