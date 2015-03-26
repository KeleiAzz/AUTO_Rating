__author__ = 'keleigong'
from GoogleScraper import scrape_with_config, GoogleSearchError
file = open('/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/50_companies_test/companies_list', 'r')
keywords = file.read()
file.close()
# keywords = keywords.split('\n')
# See in the config.cfg file for possible values
config = {
    'SCRAPING': {
        'use_own_ip': True,
        'keywords': keywords,  # 'keywords': '\n'.join(keywords),
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
        'output_filename': 'all_companies.csv'
    }
}

try:
    search = scrape_with_config(config)
except GoogleSearchError as e:
    print(e)

# let's inspect what we got

for serp in search.serps:
    print(serp)
    print(serp.search_engine_name)
    print(serp.scrape_method)
    print(serp.page_number)
    print(serp.requested_at)
    print(serp.num_results)
    # ... more attributes ...
    for link in serp.links:
        print(link)