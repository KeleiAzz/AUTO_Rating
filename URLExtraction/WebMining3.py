from URLExtraction.GoogleSearch import read_proxy_list, create_query
from URLExtraction.GoogleSearchSelenium import ScraperSelenium
from URLExtraction.URLsResultsProcessing import SearchQuery, SearchResult, write_to_xlsx
from URLExtraction.WebMining2 import get_query_results_from_json, query_processing, remove_irrelevant_urls
import json
import os
import random
import time


if __name__ == "__main__":
    # test()
    base_path = "606"
    keywords_file = 'keywords.txt'
    company_name_file = 'xxx-xxx'
    keywords_file_path = os.path.join(base_path, keywords_file)
    company_name_file_path = os.path.join(base_path, company_name_file)

    proxy = read_proxy_list("ProxyProvider/proxy.txt")
    s = ScraperSelenium(proxy)
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
        print("About {} queries for each proxy".format(len(queries) / len(proxy)))
    random.shuffle(queries)
    for q in queries:
        s.push(q)
    result_file_path = company_name_file_path + '.json'
    result_file = open(result_file_path, 'a')
    # scraped_query = open("xxx-xxx_scraped", 'w')
    finished = 1
    while s.taskleft():
        query, page, result = s.pop()
        result_file.write(json.dumps(result.to_dict()))
        result_file.write('\n')
        if s.working_thread == 0:
            time.sleep(3)
            result_file.close()
            finished = 0
            break
    if finished:
        result_file.close()
        print("****Collecting URLs complete****")
        company_json = get_query_results_from_json(result_file_path, company_name_file_path)
        company_querys = query_processing(company_json)
        company_all_urls = remove_irrelevant_urls(company_querys)
        write_to_xlsx(company_all_urls, company_name_file_path+'.xlsx')
        print("***********END***********")
