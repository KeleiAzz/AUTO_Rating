__author__ = 'keleigong'
import string
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem.porter import *
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer
from os import listdir
from os.path import isfile, join
import re
import pymysql


TABLE_NAME = "link_content_2015_only"
BASE_DIR = '/Users/keleigong/Google Drive/SCRC 2015 work/auto-rating/6th/company_profiles_2015/'

class LinkContent(object):
    def __init__(self, company, link, content, categories):
        self.company = company
        self.link = link
        self.content = content
        self.categories = categories

    def preprocess(self, stem=False):
        stemmer = SnowballStemmer("english")
        sentence = self.content.lower()
        tokenizer = RegexpTokenizer(r'\w+')
        tokens = tokenizer.tokenize(sentence)
        if stem:
            filtered_words = [stemmer.stem(w) for w in tokens if not w in stopwords.words('english')]
        else:
            filtered_words = [w for w in tokens if not w in stopwords.words('english')]
        self.content =  " ".join(filtered_words)

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
                    if output == "DB":
                        InsertToDB(all_linkcontent[-1])
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
        if len(content) > 100:
            all_linkcontent.append(LinkContent(company, link, content, categories))
            if process:
                all_linkcontent[-1].preprocess(stem)
            if output == "DB":
                InsertToDB(all_linkcontent[-1])
    return all_linkcontent

def InsertToDB(linkcontent):
    # linkcontent = all_linkcontent[0]
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='1423',
                                 db='ml_2015',
                                 # charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor,
                                 autocommit=True)
    # sql = "SELECT `link` FROM `link_content_2014` WHERE `company_name`=%s"
    # for linkcontent in all_linkcontent:
    if len(linkcontent.content) > 200:
        try:
            cur = connection.cursor()
            sql = "INSERT INTO `%s` (`company`, `link`, `content`, `categories`) VALUES (%s, %s, %s, %s)"
            cur.execute(sql, (TABLE_NAME, linkcontent.company, linkcontent.link, linkcontent.content, linkcontent.categories))
            connection.close()
        except Exception as what:
            print(what, linkcontent.link, len(linkcontent.content))
            connection.close()
    # connection.commit()

if __name__ == "__main__":
    BASE_DIR = BASE_DIR
    all_linkcontent = ReadDownloadedContent(BASE_DIR)
# InsertToDB(all_linkcontent)
# sentence = "At eight o'clock on||]*() # Thursday morning Arthur did feel very good. French-Fries"
# print(preprocess(sentence))