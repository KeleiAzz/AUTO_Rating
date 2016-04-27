import os
import time
import urllib.request as urllib2
from queue import Queue
from threading import Thread, Lock

import html2text

from WebContentDownload.pdf2text import to_text2


class Fetcher:
    def __init__(self, threads, base_dir):
        # self.base_dir = base_dir
        self.header = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
        self.path = base_dir
        self.opener = urllib2.build_opener(urllib2.HTTPHandler)
        self.lock = Lock()
        self.q_req = Queue()
        self.q_ans = Queue()
        self.threads = threads
        self.pdfcounter = 0
        for i in range(threads):
            t = Thread(target=self.threadget)
            t.setDaemon(True)
            t.start()
        self.running = 0

    def __del__(self):
        time.sleep(0.5)

        self.q_req.join()
        self.q_ans.join()

    def taskleft(self):
        return self.q_req.qsize() + self.q_ans.qsize() + self.running

    def push(self, req):
        req = (req[0], urllib2.Request(req[1], headers=self.header), req[2])
        self.q_req.put(req)

    # def is_pdf(self):

    def pop(self):
        return self.q_ans.get()

    def threadget(self):
        while True:
            req = self.q_req.get()
            with self.lock:
                self.running += 1
            pdf_dir = os.path.join(self.path, "company_pdf", req[0].replace('/', ' '))
            # pdf_dir = self.path + 'company_pdf/' + req[0].replace('/', ' ') + '/'
            if not os.path.exists(pdf_dir):
                try:
                    os.makedirs(pdf_dir)
                except FileExistsError:
                    print("dir already there")
            try:
                ans = self.opener.open(req[1], timeout=15)
                if 'pdf' in ans.getheader('Content-Type') or '.pdf' in req[0]:
                    filename = req[0].replace('/', ' ') + str(self.pdfcounter) + '.pdf'
                    file = open(os.path.join(pdf_dir, filename), 'wb')
                    with self.lock:
                        self.pdfcounter += 1
                    file.write(ans.read())
                    file.close()
                    print('pdf file %s downloaded' % filename)
                    text = to_text2(pdf_dir + filename)
                    ans = text
                elif 'application' in ans.getheader('Content-Type'):
                    ans = 'other file'
                else:
                    h = html2text.HTML2Text()
                    h.ignore_images = True
                    h.ignore_links = True
                    h.ignore_emphasis = True
                    # h.escape_snob = True
                    # h. = True
                    ans = h.handle(ans.read().decode('ISO-8859-1'))
            except Exception as what:
                ans = 'deadlink'
                print(what)
            self.q_ans.put((req, ans))
            with self.lock:
                self.running -= 1
            self.q_req.task_done()
            time.sleep(0.5)  # don't spam
