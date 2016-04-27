__author__ = 'keleigong'

import html2text
# import urllib.request
import URLExtraction.URLsResultsProcessing as URL
import TextExtraction.SecondaryDataProcess as secondary
import codecs
# import wget
import os
# import time
from collections import defaultdict, namedtuple
from openpyxl import load_workbook
from WebContentDownload.MultipleThreadFetcher import Fetcher

# from .pdf2text import to_txt

# from pattern.web import URL

BASE_DIR = "/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/606/filtered/content"
# SECONDARY_FILE = "/Users/keleigong/Dropbox/Python/AUTO_Rating/TextExtraction/secondary data/2015 secondary data.docx"
# EXCEL_FILE = "/Users/keleigong/Dropbox/Python/AUTO_Rating/TextExtraction/secondary data/EDGAE_by_year.xlsx"
URL_FILE = "/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/606/filtered/1-30.xlsx"


def generate_urls_from_json(json_file, company_name_file):
    company_json = URL.get_company_query_from_json(json_file, company_name_file)
    company_querys = URL.query_processing(company_json)
    company_all_urls = URL.remove_irrelevant_urls(company_querys)
    return company_all_urls


# def generate_urls_from_secondary(doc_file):
#     rows = secondary.generate_rows(doc_file)
#     company_all_urls = secondary.get_urls(rows)
#     return company_all_urls

def get_processed_urls(excel_file):
    res = defaultdict(list)
    wb = load_workbook(excel_file, read_only=True)
    ws = wb.get_sheet_by_name("output")
    flag = 1
    Link = namedtuple("Link", ["company", "link", "categories"])
    for row in ws.rows:
        if flag == 1:
            names = list(map(lambda x: x.value, row))
            link_idx = names.index('link')
            company_idx = names.index('company')
            category_idx = names.index('categories')
            flag = 0
        else:
            res[row[company_idx].value].append(
                Link(row[company_idx].value, row[link_idx].value, row[category_idx].value.split(",")))
    return res


def prepare(company_all_urls):
    pass


if __name__ == "__main__":
    # company_all_urls = generate_urls_from_json('../URLExtraction/concinnity_600/54-106.json',
    #                                             '../URLExtraction/concinnity_600/54-106')

    # company_all_urls = secondary.get_urls_from_docx(SECONDARY_FILE)

    # company_all_urls = secondary.get_urls_from_excel(EXCEL_FILE)
    company_all_urls = get_processed_urls(URL_FILE)
    urls = []
    company_files = {}
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)

    pdf_dir = os.path.join(BASE_DIR, 'company_pdf')
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)
    text_dir = os.path.join(BASE_DIR, 'company_profiles')
    if not os.path.exists(text_dir):
        os.makedirs(text_dir)
    _, url_file_name = os.path.split(URL_FILE)
    url_file_name = url_file_name[0:url_file_name.rindex(".")]
    deadlink = codecs.open(os.path.join(BASE_DIR, url_file_name + '_deadlink.csv'), "a", encoding="utf-8")
    try:
        with open(url_file_name + '_processed.txt', 'r') as fp:
            processed_urls = fp.read()
            if '\n' in processed_urls:
                processed_urls = processed_urls.split('\n')
    except FileNotFoundError:
        print(url_file_name + "_processed.txt does not exist, will create a new one")
        processed_urls = []

    processed = codecs.open(os.path.join(BASE_DIR, url_file_name + '_processed.txt'), "a", encoding="utf-8")

    for company, results in company_all_urls.items():
        company_files[company] = codecs.open(os.path.join(text_dir, company.replace('/', ' ') + '.txt'), "a", encoding="utf-8")
        for result in results:
            if result.link not in processed_urls:
                urls.append((company, result.link, ','.join(result.categories)))
            else:
                print("This link has been processed " + result.link)

    f = Fetcher(threads=10, base_dir=BASE_DIR)
    h = html2text.HTML2Text()
    for url in urls:
        f.push(url)
    while f.taskleft():
        url, content = f.pop()
        print(url[0], url[1].get_full_url(), len(content))
        if content != 'deadlink':
            company_files[url[0]].write('\n\n======================================================\n')
            company_files[url[0]].write(url[1].get_full_url() + '\n')
            company_files[url[0]].write(url[2] + '\n')
            company_files[url[0]].write(content)
            processed.write(url[1].get_full_url() + '\n')
        else:
            print('Deadlink detected: ' + url[1].get_full_url())
            deadlink.write(url[0] + ', ' + url[1].get_full_url() + ',\n')
    for company, file in company_files.items():
        file.close()
    deadlink.close()
    processed.close()
