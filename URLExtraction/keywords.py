
from URLExtraction import ExtractURLs
from URLExtraction import URLsResultsProcessing
from URLExtraction import CategoryAssign
'''

'''
keywords_file = '/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/final_keywords'
companies_list = '/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/50_companies_test/company_45-50'

csvfile = ExtractURLs.extract_urls(keywords_file, companies_list)
filename = ExtractURLs.convert_to_excel(csvfile, companies_list)
result = URLsResultsProcessing.urls_processing(filename)
CategoryAssign.assign_category(result, '/Users/keleigong/Dropbox/Python/AUTO_Rating/Final_keywords.xlsx')