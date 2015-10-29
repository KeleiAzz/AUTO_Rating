__author__ = 'keleigong'

import html2text
# import urllib.request
import URLExtraction.URLsResultsProcessing as URL
import TextExtraction.SecondaryDataProcess as secondary
import codecs
import urllib.request as urllib2
from threading import Thread,Lock
from queue import Queue
import wget
import os
import time
# from .pdf2text import to_txt
from WebContentDownload.pdf2text import to_txt
# from pattern.web import URL
base_dir = '/Users/keleigong/Google Drive/SCRC 2015 work/auto-rating/'


class Fetcher:
    def __init__(self, threads):
        global base_dir
        self.header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                        'Accept-Encoding': 'none',
                        'Accept-Language': 'en-US,en;q=0.8',
                        'Connection': 'keep-alive'}
        self.path = base_dir
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

    # def is_pdf(self):

    def pop(self):
        return self.q_ans.get()

    def threadget(self):
        while True:
            req = self.q_req.get()
            with self.lock: #要保证该操作的原子性，进入critical area
                self.running += 1
            pdf_dir = base_dir + 'company_pdf/' + req[0].replace('/', ' ') + '/'
            if not os.path.exists(pdf_dir):
                os.makedirs(pdf_dir)
            try:
                ans = self.opener.open(req[1], timeout=5)
                if 'application' in ans.getheader('Content-Type') or '.pdf' in req[0]:
                    # file = open( req[0] + str(self.pdfcounter) + '.pdf', 'wb')
                    # with self.lock:
                    #     self.pdfcounter += 1
                    # file.write(ans.read())
                    # file.close()
                    downloaded_file = wget.download(req[1].get_full_url(), out=pdf_dir)
                    print('%s downloaded' % downloaded_file)
                    if '.pdf' in downloaded_file[-10:]:
                        text = to_txt(downloaded_file)
                    ans = text
                    # ans = ans.getheader('Content-Type')
                # elif 'download' in ans.getheader('Content-Type'):
                #     # wget.download(req[1].get_full_url())
                #     print('file downloaded')
                #     # ans = 'PDF content'
                #     ans = ans.getheader('Content-Type')
                else:
                    h = html2text.HTML2Text()
                    h.ignore_images = True
                    h.ignore_links = True
                    h.ignore_emphasis = True
                    # h.escape_snob = True
                    # h. = True
                    ans = h.handle(ans.read().decode('ISO-8859-1'))
                    # ans = ans.getheader('Content-Type')
                    # ans = (req[0], ans)
                    # ans = ans.read()
            except Exception as what:
                ans = 'deadlink'
                print(what)
            self.q_ans.put((req, ans))
            with self.lock:
                self.running -= 1
            self.q_req.task_done()
            time.sleep(0.1)  # don't spam

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
    company_all_urls = generate_urls_from_json('../URLExtraction/concinnity_600/1-53.json',
                                                '../URLExtraction/concinnity_600/1-53')
    urls = []
    company_files = {}
    # base_dir = '1st/'
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    pdf_dir = base_dir + 'company_pdf/'
    if not os.path.exists(pdf_dir):
        os.makedirs(base_dir + 'company_pdf/')
    text_dir = base_dir + 'company_profiles/'
    if not os.path.exists(text_dir):
        os.makedirs(text_dir)

    deadlink = codecs.open('deadlink.txt', "w", encoding="utf-8")

    for company, results in company_all_urls.items():
        company_files[company] = codecs.open(text_dir + company.replace('/', ' ')+'.txt', "w", encoding="utf-8")
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
        if content != 'deadlink':
            company_files[url[0]].write('\n\n======================================================\n')
            company_files[url[0]].write(url[1].get_full_url()+'\n')
            company_files[url[0]].write(content)
        else:
            deadlink.write(url[0] + ', ' + url[1].get_full_url() +',\n')
    for company, file in company_files.items():
        file.close()
    # print(len(h.handle(content.decode('ISO-8859-1'))))
