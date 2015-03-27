# -*- coding: utf-8 -*-
# A basic use case of GoogleScraper. It will print the urls it gets from google.


from GoogleScraper import scrape_with_config, GoogleSearchError

# See in the config.cfg file for possible values
config = {
    'SCRAPING': {
        'use_own_ip': True,
        # 'keyword': 'ps4 games discount',
        'check_proxies': False,
        'keyword_file': '/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/50_companies_test/companies_list',
        'search_engines': 'google',
        'google_sleeping_ranges': 5,
        'num_pages_for_keyword': 1,
        'scrape_method': 'selenium',
        # 'num_workers': 4,
        'verbosity': 2
        # 'output_filename': '/Users/keleigong/Dropbox/Python/AUTO_Rating/output_test.csv'
    },
    'SELENIUM': {
        'num_workers': 4,
        'sel_browser': 'phantomjs',
    },
    'GLOBAL': {
        # 'do_caching': 'False',
        'verbosity': 2,
        'sleeping_ranges': '5: 5, 10',
        'manual_captcha_solving': True,
        'proxy_file': '/Users/keleigong/Dropbox/Python/AUTO_Rating/proxy.txt',
    },
    'OUTPUT': {
        # 'output_filename': 'ea_all_keywords.csv'
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