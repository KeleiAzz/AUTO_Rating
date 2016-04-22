try:
    import urllib2
except:
    import urllib.request as urllib2
import socks
from sockshandler import SocksiPyHandler
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from queue import Queue
from threading import Thread, Lock
import time

def create_opener(ip, port):
    opener = urllib2.build_opener(SocksiPyHandler(socks.SOCKS5, ip, port))
    return opener


def get_html(url, opener):
    header = "Mozilla/5.001 (windows; U; NT4.0; en-US; rv:1.0) Gecko/25250101"
    try:
        request = urllib2.Request(url)
        request.add_header("User-Agent", header)
        html = opener.open(request, None, 10).read()
        return html
    except urllib2.HTTPError as e:
        print("Error accessing:", url)
        if e.code == 503 and 'CaptchaRedirect' in e.read():
            print("Google is requiring a Captcha. "
                  "For more information see: 'https://support.google.com/websearch/answer/86640'")
        return None
    except Exception as e:
        print("Error accessing:", url)
        print(e)
        return None


def get_search_url(query, page=0, per_page=10, lang='en'):
    # note: num per page might not be supported by google anymore (because of
    # google instant)

    params = {'nl': lang, 'q': query.encode(
        'utf8'), 'start': page * per_page, 'num': per_page}
    params = urlencode(params)
    url = u"http://www.google.com/search?" + params
    # return u"http://www.google.com/search?hl=%s&q=%s&start=%i&num=%i" %
    # (lang, normalize_query(query), page * per_page, per_page)
    return url


def parse_google(html):
    soup = BeautifulSoup(html, 'html.parser')
    divs = soup.findAll("div", attrs={"class": "g"})
    for li in divs:
        print(li.find('a').text)
    print('----------------')
    return len(html)

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
    def __init__(self, proxy_list, page=1, per_page=10):
        self.openers = []
        for ip, port in proxy_list:
            self.openers.append(create_opener(ip, port))
        self.lock = Lock()
        self.q_query = Queue()
        self.q_ans = Queue()
        self.running = 0
        self.page = page
        self.per_page = per_page
        for i in range(len(self.openers)):
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
        q = (query, self.page, self.per_page)
        self.q_query.put(query)

    # def is_pdf(self):

    def pop(self):
        return self.q_ans.get()

    def thread_get(self, opener_idx):
        while True:
            query = self.q_query.get()
            with self.lock:
                self.running += 1
            url = get_search_url(query, page=self.page, per_page=self.per_page)
            html = get_html(url, self.openers[opener_idx])
            self.q_ans.put((query, parse_google(html)))
            with self.lock:
                self.running -= 1
            self.q_query.task_done()
            time.sleep(1)

proxy = [("52.23.176.220", 10080), ("52.87.214.59", 10080)]

s = Scraper(proxy)

queries = ['nike', 'apple', 'facebook', 'google', 'ibm']
for q in queries:
    s.push(q)

while s.taskleft():
    q, l = s.pop()
    print(q, l)