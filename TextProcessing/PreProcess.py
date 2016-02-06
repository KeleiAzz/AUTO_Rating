__author__ = 'keleigong'
import string
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem.porter import *
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer
from os import listdir
from os.path import isfile, join
import re
import pymysql
from threading import Thread, Lock
from queue import Queue
import time
# from .InsertIntoDB import ReadDownloadedContent



class Processor:
    def __init__(self, threads):
        self.lock = Lock() #线程锁
        self.q_req = Queue() #任务队列
        self.q_ans = Queue() #完成队列
        self.threads = threads
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
        # req = (req[0], urllib2.Request(req[1], headers=self.header), req[2])
        self.q_req.put(req)

    def pop(self):
        return self.q_ans.get()

    def threadget(self):
        while True:
            req = self.q_req.get()
            with self.lock: #要保证该操作的原子性，进入critical area
                self.running += 1
            pass # do something here
            self.q_ans.put(req)
            with self.lock:
                self.running -= 1
            self.q_req.task_done()
            time.sleep(0.5)  # don't spam


class LinkContent(object):
    def __init__(self, company, link, content, categories, year=None):
        self.company = company
        self.link = link
        self.content = content
        self.categories = categories
        self.year = year

    def preprocess(self, stem=False):
        stemmer = SnowballStemmer("english")
        sentence = self.content.lower()
        tokenizer = RegexpTokenizer(r'\w+')
        tokens = tokenizer.tokenize(sentence)
        if stem:
            filtered_words = [stemmer.stem(w) for w in tokens if w not in stopwords.words('english')]
        else:
            filtered_words = [w for w in tokens if w not in stopwords.words('english')]
        self.content =  " ".join(filtered_words)
        self.content = re.sub('\d+', ' ', self.content)
        self.content = re.sub('\s+', ' ', self.content)
        shortword = re.compile(r'\W*\b\w{1}\b')
        self.content = shortword.sub('', self.content)

    # def stemming(self):
    #     stemmer = SnowballStemmer("english")
    #     all_words = self.content.split(' ')
    #     stemmed_words = [stemmer.stem(w) for w in all_words]
    #     self.content = " ".join(stemmed_words)

def preprocess(sentence):
    # wordnet_lemmatizer = WordNetLemmatizer()
    # stemmer = PorterStemmer()
    stemmer = SnowballStemmer("english")
    sentence = sentence.lower()
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(sentence)
    # print(wordnet_lemmatizer.lemmatize("didn't"))
    filtered_words = [stemmer.stem(w) for w in tokens if not w in stopwords.words('english')]
    return " ".join(filtered_words)

def ReadDownloadedContent(path, output="DB", process=False, stem=False):
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f)) and ".txt" in f]
    all_linkcontent = []
    for file in onlyfiles:
        company = file[0:-4]
        print("Now working on " + company)
        f = open(join(path, file), 'r', encoding='ISO-8859-1')
        start_flag = 0
        link_flag = 0
        category_flag = 0
        link = ""
        content = ""
        categories = ""
        for line in f:
            if line[0:54] == "======================================================":
                if start_flag == 1:
                    all_linkcontent.append(LinkContent(company, link, content, categories))
                    if process:
                        all_linkcontent[-1].preprocess(stem)
                    # if output == "DB":
                    #     InsertToDB(all_linkcontent[-1])
                    # print(len(content))
                    # except Exception as what:
                    #     print(what)

                    link_flag = 1
                    content = ""
                else:
                    start_flag = 1
                    link_flag = 1
            elif link_flag == 1:
                link = line.rstrip('\n')
                link_flag = 0
                category_flag = 1
            elif category_flag == 1:
                categories = line.rstrip('\n')
                category_flag = 0
            else:
                content += line.rstrip('\n') + " "
        if len(content) > 100 and "sec.gov/Archives/edgar" not in link:
            all_linkcontent.append(LinkContent(company, link, content, categories))
            if process:
                all_linkcontent[-1].preprocess(stem)
            # if output == "DB":
                # InsertToDB(all_linkcontent[-1])
    return all_linkcontent

# def generate_profile_files():

# InsertToDB(all_linkcontent)
# sentence = "At eight o'clock on||]*() # Thursday morning Arthur did feel very good. French-Fries"
# print(preprocess(sentence))




