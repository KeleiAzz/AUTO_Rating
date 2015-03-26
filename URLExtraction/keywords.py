# scrape_jobs = [
#     {
#         'query': 'DEERE & CO',
#         'search_engine': 'google', # on which search engines this keyword should be searched.
#         'proxy': 'socks5 104.131.0.78 1080', # which proxy to use for this keyword
#         'num_pages': 3, # how many pages to scrape this keyword
#         'scrape_method': 'http'
#     },
#
#     {
#         'query': 'HILTON WORLDWIDE HOLDINGS',
#         'search_engine': 'google',
#         'another option': 'some fancy value', # you can specify other (even senseless) options
#         'scrape_method': 'selenium'
#     },
#
#     {
#         'query': 'TELUS CORP',
#         'search_engine': 'google',
#         'scrape_method': 'http'
#     },
#
# ]


# from openpyxl import load_workbook
# wb = load_workbook('/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/output_apple_all_keywords.xlsx')
#
# ws = wb.create_sheet(0, 'test')
#
#
# wb.save('output_apple_all_keywords.xlsx')


from URLExtraction import ExtractURLs
from URLExtraction import URLsResultsProcessing

csvfile = ExtractURLs.extract_urls('/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/50_companies_test/companies_list')
filename = ExtractURLs.convert_to_excel(csvfile)
URLsResultsProcessing.urls_processing(filename)