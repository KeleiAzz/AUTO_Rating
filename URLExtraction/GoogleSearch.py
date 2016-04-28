try:
    import urllib2
except:
    import urllib.request as urllib2
import socks
from sockshandler import SocksiPyHandler
from urllib.parse import urlencode, urlparse, urljoin
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from queue import Queue
from threading import Thread, Lock
import time
from re import match
import json
from collections import OrderedDict
import random
import os


def create_opener(ip, port):
    opener = urllib2.build_opener(SocksiPyHandler(socks.SOCKS5, ip, port))
    return opener


def get_html(url, opener):
    # header = "Mozilla/5.001 (windows; U; NT4.0; en-US; rv:1.0) Gecko/25250101"
    header = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/537.13 (KHTML, like Gecko) " \
             "Chrome/24.0.1290.1 Safari/537.13"
    try:
        request = urllib2.Request(url)
        request.add_header("User-Agent", header)
        html = opener.open(request, None, 10).read()
        return html
    except (HTTPError, urllib2.HTTPError) as e:
        print("Error accessing:", url)
        if e.code == 503:
            print("Google is requiring a Captcha. "
                  "For more information see: 'https://support.google.com/websearch/answer/86640'")
        return "Captcha"
    except Exception as e:
        print("Error accessing:", url)
        print(e)
        return None


def get_search_url(query, page=1, per_page=10, lang='en'):
    # note: num per page might not be supported by google anymore (because of
    # google instant)
    page = page - 1 if page > 0 else 0
    params = {'nl': lang, 'q': query.encode(
            'utf8'), 'start': page * per_page, 'num': per_page}
    params = urlencode(params)
    url = u"http://www.google.com/search?" + params
    # return u"http://www.google.com/search?hl=%s&q=%s&start=%i&num=%i" %
    # (lang, normalize_query(query), page * per_page, per_page)
    return url


class QueryResult(object):
    def __init__(self, query, num_results_for_query, page_number=1):
        self.query = query
        self.num_results_for_query = num_results_for_query
        self.page_number = 1
        self.results = []

    def __repr__(self):
        results_str = [r.__repr__() for r in self.results]
        res = "Search query: {}, {}\n".format(self.query, self.num_results_for_query)
        return res + '\n'.join(results_str)

    def to_dict(self):
        d = OrderedDict({"query": self.query, 'num_results_for_query': self.num_results_for_query,
                         "page_number": self.page_number})
        d['results'] = [r.__dict__ for r in self.results]
        return d

    def to_rows(self):
        res = []
        for r in self.results:
            row = r.__dict__.values()
            row.insert(0, self.query)
            row.insert(0, self.num_results_for_query)
            row.insert(0, self.page_number)
            res.append(row)
        return res

class GoogleResult:
    """Represents a google search result."""

    def __init__(self):
        self.title = None  # The title of the link
        self.link = None  # The external link
        self.domain = None
        # self.google_link = None  # The google link
        self.link_type = "results"
        self.snippet = None  # The description of the link
        # self.cached = None  # Cached version link of page
        # self.page_num = None  # Results page this one was on
        self.rank = None  # What index on this page it was on

    def __repr__(self):
        title = self.limit_str_size(self.title, 55)
        snippet = self.limit_str_size(self.snippet, 49)
        link = self.limit_str_size(self.link, 55)
        list_google = ["GoogleResult(",
                       "title={}".format(title), "\n", " " * 13,
                       "snippet={}".format(snippet), "\n", " " * 13,
                       "link={}".format(link)]
        # return str(self.__dict__)
        return "".join(list_google)

    @staticmethod
    def limit_str_size(str_element, size_limit):
        """Limit the characters of the string, adding .. at the end."""
        if not str_element:
            return None

        elif len(str_element) > size_limit:
            return str_element[:size_limit] + ".."

        else:
            return str_element


def parse_google(html, query, page=1):
    '''
    parse the html from google search page, return an QueryResult object, it has a list of GoogleResult objects.
    :param html:
    :param query:
    :param page:
    :return:
    '''
    # TODO lot to do here
    soup = BeautifulSoup(html, 'html.parser')
    resultStats = soup.find("div", attrs={"id": "resultStats"})
    if resultStats:
        num_results_for_query = resultStats.text
    else:
        num_results_for_query = "NA"
    divs = soup.findAll("div", attrs={"class": "g"})

    j = 1
    query_result = QueryResult(query, num_results_for_query, page_number=page)
    for li in divs:
        # print(li.find('a').text)
        res = GoogleResult()
        # res.page = i
        res.rank = j
        res.title = _get_title(li)
        res.link = _get_link(li)
        res.domain = _get_domain(res.link)
        # res.google_link = _get_google_link(li)
        res.snippet = _get_snippet(li)
        # res.page_num = page
        # res.cached = _get_cached(li)
        # if void is True:
        #     if res.description is None:
        #         continue
        # if res.link and res.link.startswith('http'):
        query_result.results.append(res)
        j += 1

    # print('----------------')
    return query_result


def _get_title(li):
    """Return the name of a google search."""
    a = li.find("a")
    # return a.text.encode("utf-8").strip()
    if a is not None:
        return a.text.strip()
    return None


def _get_link(li):
    """Return external link from a search."""
    try:
        a = li.find("a")
        link = a["href"]
    except:
        return None

    if link.startswith("/url?"):
        m = match('/url\?(url|q)=(.+?)&', link)
        if m and len(m.groups()) == 2:
            return urllib2.unquote(m.group(2))

    return link


def _get_domain(link):
    try:
        parsed_uri = urlparse(link)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        return domain
    except:
        return ''


def _get_google_link(li):
    """Return google link from a search."""
    try:
        a = li.find("a")
        link = a["href"]
    except:
        return None

    if link.startswith("/url?") or link.startswith("/search?"):
        return urljoin("http://www.google.com", link)

    else:
        return None


def _get_snippet(li):
    """Return the description of a google search.
    TODO: There are some text encoding problems to resolve.
    :rtype: object"""

    sdiv = li.find("div", attrs={"class": "s"})
    if sdiv:
        stspan = sdiv.find("span", attrs={"class": "st"})
        if stspan is not None:
            # return stspan.text.encode("utf-8").strip()
            return stspan.text.strip()
    else:
        return None


class ExtractWorker(Thread):
    def __init__(self, name, queue, ans, opener):
        Thread.__init__(self)
        self.opener = opener
        self.queue = queue
        self.ans = ans
        self.name = name

    def run(self):
        while True:
            url = self.queue.get()
            url = get_search_url(url)
            html = get_html(url, self.opener)
            if not html:
                break
            self.ans.put(parse_google(html))
            self.queue.task_done()
            time.sleep(1)
        print(self.name, "terminated")


class Scraper(object):
    '''
    Scraping by using urllib, sending request. This way is easier to be blocked.
    '''
    def __init__(self, proxy_list=None, page=1, per_page=10):
        self.openers = []
        if proxy_list:
            for ip, port in proxy_list:
                self.openers.append(create_opener(ip, int(port)))
        else:
            self.openers = [urllib2.build_opener(urllib2.BaseHandler)]
        self.lock = Lock()
        self.q_query = Queue()
        self.q_ans = Queue()
        self.running = 0
        self.page = page
        self.per_page = per_page
        self.working_thread = 0
        for i in range(len(self.openers)):
            self.working_thread += 1
            t = Thread(target=self.thread_get, args=(i,))
            t.setDaemon(True)
            t.start()

    def __del__(self):
        time.sleep(0.5)
        self.q_query.join()
        self.q_ans.join()

    def taskleft(self):
        return self.q_query.qsize() + self.q_ans.qsize() + self.running

    def push(self, query):
        # req = (req[0], urllib2.Request(req[1], headers=self.header), req[2])
        for i in range(1, self.page+1):
            q = (query, i, self.per_page)
            self.q_query.put(q)

    # def is_pdf(self):

    def pop(self):
        return self.q_ans.get()

    def thread_get(self, opener_idx):
        error = 0
        count = 0
        sleep_total = 1
        while True:
            print("-----------------------------------")
            query, page, per_page = self.q_query.get()
            with self.lock:
                self.running += 1
            url = get_search_url(query, page=page, per_page=per_page)
            html = get_html(url, self.openers[opener_idx])
            if html and len(html) > 20:
                self.q_ans.put((query, page, parse_google(html, query)))
            elif html == "Captcha":
                error = 3
                self.q_query.put((query, page, self.per_page))
            else:
                error += 1
                self.q_query.put((query, page, self.per_page))
            with self.lock:
                self.running -= 1
            self.q_query.task_done()
            if error == 3:
                with self.lock:
                    # self.working_thread -= 1
                    self.openers[opener_idx] = False
                break
            count += 1
            if count % 50 == 0:
                sleep_time = random.randint(60, 100)
            elif count % 40 == 0:
                sleep_time = random.randint(30, 50)
            elif count % 30 == 0:
                sleep_time = random.randint(20, 25)
            elif count % 20 == 0:
                sleep_time = random.randint(15, 22)
            elif count % 10 == 0:
                sleep_time = random.randint(11, 17)
            elif count % 5 == 0:
                sleep_time = random.randint(9, 14)
            else:
                sleep_time = random.randint(7, 12)
            print("Proxy #{}, scraping keyword: {}, {} keywords completed,"
                  " sleep for {} seconds".format(opener_idx+1, query, count, sleep_time))
            time.sleep(sleep_time+random.random())
        print("Thread %s terminated due to proxy not working properly." % (opener_idx+1,))
        with self.lock:
            self.working_thread -= 1
        if self.working_thread == 0:
            print("All threads terminated, please use new proxy and rerun")


def read_proxy_list(file):
    with open(file, 'r') as f:
        lines = f.read().strip().split('\n')
        res = [line.split()[1].split(':') for line in lines]
        print("Read proxy list done, there are {} proxies".format(len(res)))
        return res

def create_query(keywords_file, companies_list):
    '''
    combine company names and keywords to create search query.
    :param keywords_file: a file contains keywords, one keyword per line
    :param companies_list: contains company names, one company per line
    :return:
    '''
    file = open(keywords_file, 'r')
    keywords = file.read()
    file.close()
    file = open(companies_list, 'r')
    companies_names = file.read()
    file.close()
    keywords = keywords.split('\n')
    companies_names = companies_names.split('\n')
    query = []
    for company in companies_names:
        # company_splited = company.split(' ')
        # if company_splited[-1] in ["INC", "CORP"]:
        #     company = ' '.join(company_splited[0:-1])
        for word in keywords:
            query.append(company + ' ' + word)
    # print("Create query done, there are {} queries need to be scraped in total".format(len(query)))
    return query


def test():
    query = 'python regex tester'
    url = get_search_url(query, page=1)
    header = "Mozilla/5.001 (windows; U; NT4.0; en-US; rv:1.0) Gecko/25250101"
    request = urllib2.Request(url)
    request.add_header("User-Agent", header)
    html = urllib2.urlopen(request).read()
    # soup = BeautifulSoup(html, 'html.parser')
    result = parse_google(html, query)
    print(result.__dict__)
    # print(result.results[0].__dict__)
    d = result.results[0].__dict__
    print(json.dumps(d))
    print(result.results[0])
    # print(json.dumps(result.to_json()))
    with open('res.json', 'w') as f:
        # line = json.dumps(result.to_dict(), indent=2, separators=(',', ': '))
        line = json.dumps(result.to_dict())
        f.write(line)
        f.write('\n')
        f.write(line)


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
                json_obj = json.loads(line.strip())
                scraped.add(json_obj['query'])
    else:
        scraped = None
    print("{} queries in total".format(len(queries)))
    if scraped:
        queries = [q for q in queries if q not in scraped]
        print("{} queries remaining".format(len(queries)))
    random.shuffle(queries)
    for q in queries:
        s.push(q)
    result_file = open(company_name_file_path+'.json', 'a')
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
    print("***********END***********")
