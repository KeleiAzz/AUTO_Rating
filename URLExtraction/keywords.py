scrape_jobs = [
    {
        'query': 'DEERE & CO',
        'search_engine': 'google', # on which search engines this keyword should be searched.
        'proxy': 'socks5 104.131.0.78 1080', # which proxy to use for this keyword
        'num_pages': 3, # how many pages to scrape this keyword
        'scrape_method': 'http'
    },

    {
        'query': 'HILTON WORLDWIDE HOLDINGS',
        'search_engine': 'google',
        'another option': 'some fancy value', # you can specify other (even senseless) options
        'scrape_method': 'selenium'
    },

    {
        'query': 'TELUS CORP',
        'search_engine': 'google',
        'scrape_method': 'http'
    },

]