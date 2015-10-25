__author__ = 'keleigong'

from selenium import webdriver

import os
# profile = webdriver.FirefoxProfile()
# profile.set_preference('browser.download.folderList', 2)
# profile.set_preference('browser.download.manager.showWhenStarting', False)
# profile.set_preference('browser.download.dir', os.getcwd())
# profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/pdf')
#
#
# profile.set_preference('pdfjs.disabled', True)
#
# profile.set_preference("plugin.scan.plid.all", False)
# profile.set_preference("plugin.scan.Acrobat", "99.0")
#
# driver = webdriver.Firefox(profile)
# driver.get('http://anh.cs.luc.edu/python/hands-on/3.1/Hands-onPythonTutorial.pdf')
# html = driver.page_source

import html2text
import urllib.request
import URLExtraction.URLsResultsProcessing as URL

company_json = URL.json_processing('/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/concinnity_600/1-50.json',
                                   '/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/concinnity_600/1-50')
company_querys = URL.query_processing(company_json)

company_all_urls = URL.remove_irrelevant_urls(company_querys)

urls = [result.link for result in company_all_urls['BIOGEN']]
# urls =['https://www.bankofamerica.com/suppliers/supply-chain-management.go?request_locale=en_US',
#       'http://about.bankofamerica.com/en-us/our-story/supplier-relations.html',
#       'http://about.bankofamerica.com/en-us/our-story/supplier-diversity.html',
#       'http://www.bofaml.com/en-us/content/trade-supply-chain.html']

# with urllib.request.urlopen(url) as response:
#     html = response.read()

# response = map(urllib.request.urlopen, urls)

# h = html2text.HTML2Text()
# result = h.handle(html.decode('utf8'))
# print(result)
import urllib.request as urllib2
from threading import Thread,Lock
from queue import Queue
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

    def push(self,req):
        req = urllib2.Request(req, headers=self.header)
        self.q_req.put(req)

    def pop(self):
        return self.q_ans.get()

    def threadget(self):
        while True:
            req = self.q_req.get()
            with self.lock: #要保证该操作的原子性，进入critical area
                self.running += 1
            try:
                ans = self.opener.open(req, timeout=5)
                if ans.getheader('Content-Type') == 'application/pdf':
                    file = open(str(self.pdfcounter) + '.pdf', 'wb')
                    self.pdfcounter += 1
                    file.write(ans.read())
                    file.close()
                    print('PDF downloaded')
                    ans = 'PDF content'
                else:
                    ans = ans.read()
                # print(ans.getheader('Content-Type'))  # application/pdf
                # ans = ans.read()
            except Exception as what:
                ans = ''
                print(what)
            # if ans == '':
            #     self.q_ans.put((req,'no content fetched'))
            #     with self.lock:
            #         self.running -= 1
            # elif ans.getheader('Content-Type') == 'application/pdf':
            #     self.q_ans.put((req,'pdf content'))
            #     self.pdfcounter += 1
            #     # tmp = ans.read()
            #     file = open(str(self.pdfcounter) + '.pdf', 'wb')
            #     file.write(ans.read())
            #     file.close()
            #     print("PDF downloaded")
            #     with self.lock:
            #         self.running -= 1
            # else:
            #     ans = ans.read()
            self.q_ans.put((req, ans))
            with self.lock:
                self.running -= 1
            self.q_req.task_done()
            time.sleep(0.1) # don't spam

# if __name__ == "__main__":
#     links = [ 'http://www.verycd.com/topics/%d/'%i for i in range(5420,5430) ]
f = Fetcher(threads=10)
for url in urls:
    f.push(url)
while f.taskleft():
    url, content = f.pop()
    print(url.get_full_url(), len(content))

# a = urllib2