from URLExtraction.GoogleSearch import create_opener, get_html, get_search_url, parse_google
from queue import Queue
from threading import Thread, Lock
import urllib.request as urllib2
import random
import time


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
