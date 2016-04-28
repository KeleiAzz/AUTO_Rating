from URLExtraction.GoogleSearch import read_proxy_list, create_query, Scraper
from URLExtraction.URLsResultsProcessing import SearchQuery, SearchResult, write_to_xlsx
import json
import os
import random
import time


def get_company_names(file_path):
    with open(file_path, 'r') as file:
        companies_names = file.read()
    companies_names = companies_names.strip().split('\n')
    return companies_names


def get_query_results_from_json(json_file, company_file):
    with open(json_file, 'r') as f:
        json_data = []
        for result in f:
            try:
                json_obj = json.loads(result)
                json_data.append(json_obj)
            except ValueError:
                pass
    company_names = get_company_names(company_file)
    company_json = {}
    for name in company_names:
        company_json[name] = []
    for query_result in json_data:
        for name in company_names:
            if name in query_result['query']:
                company_json[name].append(query_result)
                break
    print(len(company_json))
    return company_json


def query_processing(company_json):
    company_querys = {}
    # print(company_json)
    for company in company_json.keys():
        company_querys[company] = []
    for company, querys in company_json.items():
        for query in querys:
            company_querys[company].append(SearchQuery(company, query))
    return company_querys


def remove_irrelevant_urls(company_querys):
    keywords_to_delete = ['linkedin', 'linkup', 'disabledperson', 'indeed', 'simplyhired',
                          'career', 'recruit', 'glassdoor', 'jobs', 'monster.com', 'yelp', 'itunes',
                          'googleadservices', 'wiki', 'www.google.com', 'amazon.com']
    company_all_urls = {}
    for company, querys in company_querys.items():
        company_all_urls[company] = []
        for query in querys:
            for result in query.results:
                if any(k in result.domain for k in keywords_to_delete):
                    continue
                if result in company_all_urls[company]:
                    pass
                else:
                    company_all_urls[company].append(result)
    for company, urls in company_all_urls.items():
        for url in urls:
            url.update_categories()
        urls.sort(key=lambda x: x.count,reverse=True)
        company_all_urls[company] = list(filter(lambda x: x.count>2, urls))
    print(len(company_all_urls))
    return company_all_urls



if __name__ == "__main__":
    # test()
    base_path = "606"
    keywords_file = 'keywords.txt'
    company_name_file = 'xxx-xxx'
    keywords_file_path = os.path.join(base_path, keywords_file)
    company_name_file_path = os.path.join(base_path, company_name_file)

    proxy = read_proxy_list("ProxyProvider/proxy.txt")
    s = Scraper(proxy)
    queries = create_query(keywords_file_path, company_name_file_path)
    if os.path.exists(company_name_file_path+'.json'):
        with open(company_name_file_path+'.json', 'r') as f:
            scraped = set()
            for line in f:
                try:
                    json_obj = json.loads(line.strip())
                    scraped.add(json_obj['query'])
                except ValueError:
                    pass

    else:
        scraped = None
    print("{} queries in total".format(len(queries)))
    if scraped:
        queries = [q for q in queries if q not in scraped]
        print("{} queries remaining".format(len(queries)))
    random.shuffle(queries)
    for q in queries:
        s.push(q)
    result_file_path = company_name_file_path + '.json'
    result_file = open(result_file_path, 'a')
    # scraped_query = open("xxx-xxx_scraped", 'w')
    while s.taskleft():
        query, page, result = s.pop()
        result_file.write(json.dumps(result.to_dict()))
        result_file.write('\n')
        if s.working_thread == 0:
            time.sleep(3)
            result_file.close()
            exit(1)
    result_file.close()
    print("****Collecting URLs complete****")
    company_json = get_query_results_from_json(result_file_path, company_name_file_path)
    company_querys = query_processing(company_json)
    company_all_urls = remove_irrelevant_urls(company_querys)
    write_to_xlsx(company_all_urls, company_name_file_path+'.xlsx')
    print("***********END***********")
