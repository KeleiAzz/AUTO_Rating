# -*- coding: utf-8 -*-
# A basic use case of GoogleScraper. It will print the urls it gets from google.


from GoogleScraper import scrape_with_config, GoogleSearchError

# See in the config.cfg file for possible values

QUERY = "nike"
SITE = "forbes.com"
START_DATE = ('1', '1', '2015')
END_DATE = ('6', '1', '2015')
BASE_URL = "https://www.google.com/search?q={query}+site:{site}&newwindow=1&hl=en&gl=us&authuser=0&tbs=\
            sbd:1,cdr:1,cd_min:{start_date},cd_max:{end_date}&tbm=nws&start=0"

config = {
    'use_own_ip': True,
    'keyword': '{} site:{}'.format(QUERY, SITE),
    'check_proxies': False,
    # 'keyword_file': 'countrykeywords/country_en2',
    'search_engines': 'google',
    # 'google_sleeping_ranges': 5,
    'num_pages_for_keyword': 10,
    'scrape_method': 'selenium',  # http or selenium
    'sel_browser': 'Firefox',
    'num_workers': 1,
    'verbosity': 2,
    'do_caching': False,
    # 'sleeping_ranges': '5: 5, 10',
    'google_search_url': BASE_URL.format(query=QUERY, site=SITE, start_date="/".join(START_DATE), end_date="/".join(END_DATE)),
    # 'proxy_file': '/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/ProxyProvider/proxy.txt',  # path to the proxy file
    'output_filename': '{}_{}_{}_{}.json'.format(QUERY, SITE, "-".join(START_DATE), "-".join(END_DATE)),
    'database_name': 'basic'
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