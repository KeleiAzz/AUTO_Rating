
from URLExtraction import ExtractURLs
from URLExtraction import URLsResultsProcessing
#from URLExtraction import CategoryAssign
from URLExtraction import URLsResultsProcessing
import os
#
def web_mining(company_name_file, keywords_file):
    csvfile = ExtractURLs.extract_urls(keywords_file, company_name_file)

# filename = ExtractURLs.convert_to_excel(csvfile, companies_list)
# result = URLsResultsProcessing.urls_processing(filename)
# CategoryAssign.assign_category(result, '/Users/keleigong/Dropbox/Python/AUTO_Rating/Final_keywords.xlsx')

if __name__ == "__main__":
    # Setting the base working path, and required file names
    base_path = '/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/606/'
    keywords_file = 'keywords.txt'
    company_name_file = 'xxx-xxx'
    keywords_file_path = os.path.join(base_path, keywords_file)
    company_name_file_path = os.path.join(base_path, company_name_file)

    # Collecting URLs using Google search, it will generate a json file and a db file to store the results.
    result_file = web_mining(company_name_file_path, keywords_file_path)

    # Processing the collected results.
    company_json = URLsResultsProcessing.get_company_query_from_db(company_name_file_path)
    company_querys = URLsResultsProcessing.query_processing(company_json)
    company_all_urls = URLsResultsProcessing.remove_irrelevant_urls(company_querys)
    URLsResultsProcessing.write_to_xlsx(company_all_urls, company_name_file_path+'.xlsx')