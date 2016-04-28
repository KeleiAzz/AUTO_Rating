from selenium.webdriver.support.wait import WebDriverWait

from URLExtraction.GoogleSearch import create_opener, get_search_url, get_html, parse_google
import urllib.request as urllib2
from threading import Lock, Thread
from queue import Queue
import random
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.common.exceptions import ElementNotVisibleException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC


class ScraperSelenium(object):
    '''
    Scraping by using selenium with web browser like Chrome or Phantomjs.
    '''
    def __init__(self, proxy_list=None, page=1, per_page=10):
        self.proxy_list = proxy_list
        # if proxy_list:
        #     for ip, port in proxy_list:
        #         self.openers.append(create_opener(ip, int(port)))
        # else:
        #     self.openers = [urllib2.build_opener(urllib2.BaseHandler)]
        self.lock = Lock()
        self.q_query = Queue()
        self.q_ans = Queue()
        self.running = 0
        self.page = page
        self.per_page = per_page
        self.working_thread = 0
        for i in range(len(self.proxy_list)):
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

    def thread_get(self, proxy_idx):
        error = 0
        count = 0
        ip, port = self.proxy_list[proxy_idx]
        # service_args = [
        #             '--proxy={}:{}'.format(ip, port),
        #             '--proxy-type={}'.format("socks5"),
        #         ]
        # driver = webdriver.PhantomJS(service_args=service_args)
        chrome_ops = webdriver.ChromeOptions()
        chrome_ops.add_argument(
            '--proxy-server={}://{}:{}'.format("socks5", ip, port))
        driver = webdriver.Chrome(chrome_options=chrome_ops, executable_path="/usr/local/bin/chromedriver")
        driver.set_window_size(500, 400)
        # driver.set_window_position()
        driver.get("http://www.google.com")
        max_wait = 20
        while True:
            # print("-----------------------------------")
            query, page, per_page = self.q_query.get()
            with self.lock:
                self.running += 1
            # input_field = driver.find_element(By.NAME, 'q')
            def find_visible_search_input(driver):
                input_field = driver.find_element(By.NAME, 'q')
                return input_field
            try:
                search_input = WebDriverWait(driver, max_wait).until(find_visible_search_input)
            except (TimeoutException, NoSuchElementException) as e:
                print('Proxy #{}: TimeoutException waiting for search input field: {}'.format(proxy_idx, e))
                error += 1
                with self.lock:
                    self.running -= 1
                self.q_query.put((query, page, self.per_page))
                if error >= 3:
                    with self.lock:
                        self.proxy_list[proxy_idx] = False
                    break
                else:
                    continue
            if search_input:
                search_input.clear()
                try:
                    search_input.send_keys(query + Keys.ENTER)
                except ElementNotVisibleException:
                    time.sleep(2)
                    search_input.send_keys(query + Keys.ENTER)
                try:
                    WebDriverWait(driver, 15).\
                        until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#navcnt td.cur'), str(1)))
                except TimeoutException as e:
                    print("Proxy #{} TimeoutException, can't load the results page, {}.".format(proxy_idx, e))
                    with self.lock:
                        self.running -= 1
                        self.proxy_list[proxy_idx] = False
                    break
                try:
                    html = driver.execute_script('return document.body.innerHTML;')
                except WebDriverException as e:
                    html = driver.page_source
                if html and len(html) > 20:
                    # print(len(html))
                    self.q_ans.put((query, page, parse_google(html, query)))
            # elif "Captcha" in html:
            #     error = 3
            #     self.q_query.put((query, page, self.per_page))
                else:
                    error += 1
                    self.q_query.put((query, page, self.per_page))
            with self.lock:
                self.running -= 1
            self.q_query.task_done()
            if error == 3:
                with self.lock:
                    # self.working_thread -= 1
                    self.proxy_list[proxy_idx] = False
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
                  " sleep for {} seconds".format(proxy_idx+1, query, count, sleep_time))
            time.sleep(sleep_time+random.random())
        print("Thread %s terminated due to proxy not working properly." % (proxy_idx+1,))
        driver.quit()
        with self.lock:
            self.working_thread -= 1
        if self.working_thread == 0:
            print("All threads terminated, please use new proxy and rerun")
