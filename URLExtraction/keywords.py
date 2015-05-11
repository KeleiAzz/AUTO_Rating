
from URLExtraction import ExtractURLs
from URLExtraction import URLsResultsProcessing
#from URLExtraction import CategoryAssign
#
keywords_file = '/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/countrykeywords/keywords_en1'
companies_list = '/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/countrykeywords/country_en'

csvfile = ExtractURLs.extract_urls(keywords_file, companies_list)
filename = ExtractURLs.convert_to_excel(csvfile, companies_list)
result = URLsResultsProcessing.urls_processing(filename)
#CategoryAssign.assign_category(result, '/Users/keleigong/Dropbox/Python/AUTO_Rating/Final_keywords.xlsx')

# from selenium import webdriver
# browser = webdriver.PhantomJS()
# browser.get("http://borjarefoyo.com/2013/11/16/scraping-website-using-python-selenium-lxml-phantomjs/")
# for elem in browser.find_elements_by_xpath('.//span[@class = "gbts"]'):
#     print(elem.text)
