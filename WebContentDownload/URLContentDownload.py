__author__ = 'keleigong'

import html2text
import urllib.request
import URLExtraction.URLsResultsProcessing as URL
import TextExtraction.SecondaryDataProcess as secondary

import urllib.request as urllib2
from threading import Thread,Lock
from queue import Queue
import wget
import time
# from pattern.web import URL
class Fetcher:
    def __init__(self,threads):
        self.header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                        'Accept-Encoding': 'none',
                        'Accept-Language': 'en-US,en;q=0.8',
                        'Connection': 'keep-alive'}
        self.opener = urllib2.build_opener(urllib2.HTTPHandler)
        # self.opener.addheaders(self.header)
        # self.h = html2text.HTML2Text()
        self.lock = Lock() #线程锁
        self.q_req = Queue() #任务队列
        self.q_ans = Queue() #完成队列
        self.threads = threads
        self.pdfcounter = 0
        for i in range(threads):
            t = Thread(target=self.threadget)
            t.setDaemon(True)
            t.start()
        self.running = 0

    def __del__(self): #解构时需等待两个队列完成
        time.sleep(0.5)
        self.q_req.join()
        self.q_ans.join()

    def taskleft(self):
        return self.q_req.qsize()+self.q_ans.qsize()+self.running

    def push(self, req):
        req = (req[0], urllib2.Request(req[1], headers=self.header))
        self.q_req.put(req)

    def pop(self):
        return self.q_ans.get()

    def threadget(self):
        while True:
            req = self.q_req.get()
            with self.lock: #要保证该操作的原子性，进入critical area
                self.running += 1
            try:
                ans = self.opener.open(req[1], timeout=5)
                if 'application/pdf' in ans.getheader('Content-Type'):
                    # file = open( req[0] + str(self.pdfcounter) + '.pdf', 'wb')
                    with self.lock:
                        self.pdfcounter += 1
                    # file.write(ans.read())
                    # file.close()
                    print('PDF downloaded')
                    ans = 'PDF content'
                elif 'application/download' in ans.getheader('Content-Type'):
                    # wget.download(req[1].get_full_url())
                    print('file downloaded')
                    ans = 'PDF content'
                else:
                    h = html2text.HTML2Text()
                    ans = h.handle(ans.read().decode('ISO-8859-1'))
                    # ans = (req[0], ans)
                    # ans = ans.read()
            except Exception as what:
                ans = ''
                print(what)
            self.q_ans.put((req, ans))
            with self.lock:
                self.running -= 1
            self.q_req.task_done()
            time.sleep(0.1) # don't spam

# if __name__ == "__main__":
#     links = [ 'http://www.verycd.com/topics/%d/'%i for i in range(5420,5430) ]

def generate_urls_from_json(json_file, company_name_file):
    company_json = URL.json_processing(json_file, company_name_file)
    company_querys = URL.query_processing(company_json)

    company_all_urls = URL.remove_irrelevant_urls(company_querys)
    return company_all_urls

def generate_urls_from_secondary(doc_file):
    rows = secondary.generate_rows(doc_file)
    company_all_urls = secondary.get_urls(rows)
    return company_all_urls


if __name__ == "__main__":
    company_all_urls = generate_urls_from_json('../URLExtraction/concinnity_600/1-50.json',
                                                '../URLExtraction/concinnity_600/1-50')
    urls = []
    for company, results in company_all_urls.items():
        for result in results:
            urls.append((company, result.link))
# urls = [result.link for result in company_all_urls['BIOGEN']]
    f = Fetcher(threads=10)
    h = html2text.HTML2Text()
    for url in urls:
        f.push(url)
    while f.taskleft():
        url, content = f.pop()
        print(url[0], url[1].get_full_url(), len(content))
    # print(len(h.handle(content.decode('ISO-8859-1'))))

# a = urllib2