
from URLExtraction import ExtractURLs
from URLExtraction import URLsResultsProcessing
keywords_file = '/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/final_keywords'
companies_list = '/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/50_companies_test/company_15-16'

csvfile = ExtractURLs.extract_urls(keywords_file, companies_list)
filename = ExtractURLs.convert_to_excel(csvfile, companies_list)
URLsResultsProcessing.urls_processing(filename)