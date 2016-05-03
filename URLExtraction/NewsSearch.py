from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from URLExtraction.GoogleSearch import parse_google, QueryResult, GoogleResult, create_opener, get_html
from openpyxl import Workbook
import os
from bs4 import BeautifulSoup
import urllib.request as urllib2



# url = base_url.format(start_date="1/1/2015", end_date="2/1/2015")
# print(url)
#
# driver = webdriver.Chrome()
# driver.get(url)
#
# time.sleep(5)
#
# driver.quit()


class NewsSearch(object):
    def __init__(self, query, site=None, start_date=None, end_date=None, pages=20, news=True, proxy=None):
        '''
        Selenium with chromedriver to do google search
        :param query:
        :param site: format: nytimes.com
        :param start_date: format: 12/31/2015
        :param end_date: format: 12/31/2015
        :param pages: number of pages to get
        :param news: whether to search in google news, or in normal search
        :param proxy: format: [ip, port]
        :return:
        '''
        self.next_page_selector = "#pnnext"
        if proxy:
            ip, port = proxy
            chrome_ops = webdriver.ChromeOptions()
            chrome_ops.add_argument(
                    '--proxy-server={}://{}:{}'.format("socks5", ip, port))
            self.webdriver = webdriver.Chrome(chrome_options=chrome_ops, executable_path="/usr/local/bin/chromedriver")
        else:
            self.webdriver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver")

        # self.base_url = "https://www.google.com/search?q={query}+site:{site}&newwindow=1&hl=en&gl=us&authuser=0&tbs=sbd:1,cdr:1,cd_min:{start_date},cd_max:{end_date}&tbm=nws&start=0"
        self.query = query
        self.site = site
        self.news = news
        if start_date and end_date:
            self.start_date = start_date
            self.end_date = end_date
        else:
            self.start_date = None
            self.end_date = None

        if start_date and end_date and site:
            self.base_url = "https://www.google.com/search?q={query}+site:{site}&hl=en&gl=us&authuser=0&" \
                            "tbs=sbd:1,cdr:1,cd_min:{start_date},cd_max:{end_date}&tbm=nws&start=0"
            self.url = self.base_url.format(query=self.query, site=self.site,
                                            start_date=self.start_date, end_date=self.end_date)
            self.output = "{}_{}_{}_{}_news.xlsx".format(self.query, self.site, self.start_date.replace('/', '-'),
                                                    self.end_date.replace('/', '-'))
        elif start_date and end_date and site is None:
            self.base_url = "https://www.google.com/search?q={query}&hl=en&gl=us&authuser=0&" \
                            "tbs=sbd:1,cdr:1,cd_min:{start_date},cd_max:{end_date}&tbm=nws&start=0"
            self.url = self.base_url.format(query=self.query, start_date=self.start_date, end_date=self.end_date)
            self.output = "{}_{}_{}_news.xlsx".format(query, start_date.replace('/', '-'), end_date.replace('/', '-'))
        elif (start_date is None or end_date is None) and site:
            self.base_url = "https://www.google.com/search?q={query}+site:{site}&tbm=nws"
            self.url = self.base_url.format(query=self.query, site=self.site)
            self.output = "{}_{}_news.xlsx".format(query, site)
        else:
            self.base_url = "https://www.google.com/search?q={query}&tbm=nws"
            self.url = self.base_url.format(query=self.query)
            self.output = "{}_news.xlsx".format(query)
        if not self.news:
            self.url = self.url.replace('&tbm=nws', '')
            self.output = self.output.replace('_news', '')
        self.page_number = 1
        self.pages_per_keyword = pages
        self.pages = []

    # def __del__(self):
    #
    #     self.webdriver.quit()

    def _find_next_page_element(self):
        """
        Finds the element that locates the next page for any search engine.
        Returns:
        The element that needs to be clicked to get to the next page or a boolean value to
        indicate an error condition.
        """

        selector = self.next_page_selector
        try:
            # wait until the next page link is clickable
            WebDriverWait(self.webdriver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        except (WebDriverException, TimeoutException) as e:
            # self._save_debug_screenshot()
            print("Timeout, no next page available")
            return None
        # raise Exception('{}: Cannot locate next page element: {}'.format(self.name, str(e)))

        return self.webdriver.find_element_by_css_selector(selector)

    def _goto_next_page(self):
        """
        Click the next page element,
        Returns:
        The url of the next page or False if there is no such url
        (end of available pages for instance).
        """

        next_url = ''
        element = self._find_next_page_element()

        if hasattr(element, 'click'):
            next_url = element.get_attribute('href')
            try:
                element.click()
            except WebDriverException:
                # See http://stackoverflow.com/questions/11908249/debugging-element-is-not-clickable-at-point-error
                # first move mouse to the next element, some times the element is not visibility, like blekko.com
                selector = self.next_page_selector
                if selector:
                    try:
                        next_element = WebDriverWait(self.webdriver, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                        webdriver.ActionChains(self.webdriver).move_to_element(next_element).perform()
                        # wait until the next page link emerges
                        WebDriverWait(self.webdriver, 8).until(
                                EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                        element = self.webdriver.find_element_by_css_selector(selector)
                        next_url = element.get_attribute('href')
                        element.click()
                    except WebDriverException:
                        pass
        if not next_url:
            return False
        else:
            return next_url

    def wait_until_serp_loaded(self):
        """
        This method tries to wait until the page requested is loaded.
        We know that the correct page is loaded when self.page_number appears
        in the navigation of the page.
        """

        # if self.search_type == 'normal':

        # if self.search_engine_name == 'google':
        selector = '#navcnt td.cur'

        try:
            WebDriverWait(self.webdriver, 5). \
                until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, selector), str(self.page_number)))
        except TimeoutException as e:
            # self._save_debug_screenshot()
            content = self.webdriver.find_element_by_css_selector(selector).text
            raise Exception('Pagenumber={} did not appear in navigation. Got "{}" instead'.format(self.page_number),
                            content)
        self.wait_until_title_contains_keyword()

    def wait_until_title_contains_keyword(self):
        try:
            WebDriverWait(self.webdriver, 5).until(EC.title_contains(self.query))
        except TimeoutException:
            pass
            # logger.debug(SeleniumSearchError(
            #         '{}: Keyword "{}" not found in title: {}'.format(self.name, self.query, self.webdriver.title)))

    def search(self):
        """Search with webdriver.
        Fills out the search form of the search engine for each keyword.
        Clicks the next link while pages_per_keyword is not reached.
        """
        url = self.url
        # if self.site:
        #     url = self.base_url.format(query=self.query, site=self.site,
        #                                start_date=self.start_date, end_date=self.end_date)
        # else:
        #     url = self.base_url.format(query=self.query, start_date=self.start_date, end_date=self.end_date)
        self.webdriver.get(url)
        for page_number in range(1, self.pages_per_keyword + 1):
            self.page_number = page_number
            self.wait_until_serp_loaded()
            print("Now in page %s" % page_number)
            html = None
            try:
                html = self.webdriver.execute_script('return document.body.innerHTML;')
                # print(len(html))
            except WebDriverException as e:
                html = self.webdriver.page_source

            if html:
                page = parse_google(html, self.query, page=page_number, news=self.news)
                print(page)
                self.pages.append(page)
                # super().after_search()

                # Click the next page link not when leaving the loop
                # in the next iteration.
            # if self.page_number in self.pages_per_keyword:
            time.sleep(3)
            next_url = self._goto_next_page()
            # self.requested_at = datetime.datetime.utcnow()

            if not next_url:
                break
        self.webdriver.quit()

    def save_results(self, path=None):
        rows = []
        for page in self.pages:
            for r in page.results:
                row = [self.query, page.page_number, r.date, r.title, r.link, r.rank, r.snippet, r.domain,
                       page.num_results_for_query]
                rows.append(row)
        for row in rows:
            print(row)
        # filename = "{}_{}_{}_{}.xlsx".format(self.query, self.site, self.start_date.replace('/', '-'),
        #                                      self.end_date.replace('/', '-'))
        filename = self.output
        if path:
            file = os.path.join(path, filename)
        else:
            file = filename
        wb = Workbook(file)
        sheet = wb.create_sheet('output', 0)
        sheet.append(["query", "page_num", "date", "title", "link", "rank", "snippet", "domain", "num_results"])
        for row in rows:
            sheet.append(row)
        wb.save(file)


def scrape_news(url, parser, proxy=None):
    if proxy:
        ip, port = proxy
        opener = create_opener(ip, port)
    else:
        opener = urllib2.build_opener(urllib2.BaseHandler)
    html = get_html(url, opener)
    text = parser(html)
    return text





if __name__ == "__main__":
    # url = 'http://www.nytimes.com/2015/07/25/fashion/converse-chuck-taylor-all-star-ii.html'
    # text = scrape_news(url, parse_nytimes)
    # print(text)
    ns = NewsSearch("nike", "nytimes.com", pages=5)
    ns.search()
    ns.save_results()
# for result in ns.results:
#     print(result)
