from openpyxl import load_workbook
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
import os
import html2text

def read_urls(file, domain=None):
    wb = load_workbook(file, read_only=True)
    ws = wb.get_sheet_by_name("output")
    flag = 1
    res = []
    for row in ws.rows:
        if flag:
            col_names = [x.value for x in row]
            link_idx = col_names.index("link")
            domain_idx = col_names.index("domain")
            flag = 0
        else:
            if domain and domain in row[domain_idx].value:
                res.append(row[link_idx].value)
            elif domain is None:
                res.append(row[link_idx].value)
    return res


def get_html(urls, save_path=None, proxy=None):
    if proxy:
        ip, port = proxy
        chrome_ops = webdriver.ChromeOptions()
        chrome_ops.add_argument(
                '--proxy-server={}://{}:{}'.format("socks5", ip, port))
        driver = webdriver.Chrome(chrome_options=chrome_ops, executable_path="/usr/local/bin/chromedriver")
    else:
        driver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver")
    res = []
    for url in urls:
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        if soup.find('a', attrs={'class': 'continue-button'}):
            time.sleep(10)
            driver.get(url)
            html = driver.page_source
        print(len(html))
        res.append(html)
        if save_path:
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            file = os.path.join(save_path, driver.title.replace("/", " ") + ".html")
            with open(file, 'w', encoding="utf-8") as f:
                f.write(html)
        time.sleep(3)
    driver.quit()
    return res


def parse_html(file, parser):
    # html = ''
    with open(file, 'r') as f:
        html = f.read()
    return parser(html)


def extract_text(path, parser):
    text = []
    for file in os.listdir(path):
        if not file.startswith('.'):
            file = os.path.join(path, file)
            with open(file, 'r', encoding="utf-8") as f:
                html = f.read()
                content = parser(html)
            text.append(content)
            with open(file.replace('.html', '.txt'), 'w', encoding='utf-8') as f:
                f.write(content)
    return text


def parse_forbes(html):
    soup = BeautifulSoup(html, 'html.parser')
    res = ""
    for row in soup.find_all('div', attrs={"class": "article-injected-body ng-scope"}):
        print(row.text)
        res += row.text
    return res


def parse_nytimes(html):
    soup = BeautifulSoup(html, 'html.parser')
    res = ""
    for row in soup.find_all('div', attrs={"class": "story-body"}):
        # print(row.text)
        res += row.text
    return res


def parse_general(html):
    h = html2text.HTML2Text()
    h.ignore_images = True
    h.ignore_links = True
    h.ignore_emphasis = True
    # h.escape_snob = True
    # h. = True
    return h.handle(html)

# urls = read_urls("/Users/keleigong/Dropbox/Python/AUTO_Rating/URLExtraction/nike_nytimes.com_news.xlsx", "nytimes.com")

# for url in urls:
#     print(url)
#
# get_html(urls, "news_nytimes")

extract_text("news_nytimes", parse_general)