import codecs

__author__ = 'keleigong'
import re
import pymysql
from TextProcessing.PreProcess import LinkContent, ReadDownloadedContent

def get_company_names():
    conn = pymysql.connect(host='localhost',
                           user='root',
                           password='1423',
                           db='ml_2015',
                           cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()
    sql="SELECT DISTINCT `company` FROM `link_content_13_15`"
    cur.execute(sql)
    res = []
    for row in cur:
        res.append(row['company'])
    return res

def read_content_from_db(company):
    conn = pymysql.connect(host='localhost',
                           user='root',
                           password='1423',
                           db='ml_2015',
                           cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()
    sql="SELECT `link`, `content`, `categories` FROM `link_content_13_15` WHERE `company`=%s"
    cur.execute(sql, (company,))
    res = []
    for row in cur:
        res.append(row)
    return res


def split_content_to_sentences(content):
    if type(content) == type(b'x'):
        content = content.decode('utf8')
    # while True:
    #     # content.
    #     pass
    pattern = re.compile("[^\w.]+|_", re.UNICODE)
    content = str(pattern.sub(' ', content.lower()))
    line = re.sub(r'[^\x00-\x7F]+', ' ', content)

    # line = re.sub('[@|/-_+=~`\[\]\{\}\(\)"\'#$%*&^\r\n]', ' ', line)
    line = re.sub('\s+', ' ', line)
    line = re.sub('\.+', '.', line)
    # line = re.sub('\s\w\s', '', line)
    tmp = re.sub('\.+\s+', '<PERIOD>', line)
    return tmp.split('<PERIOD>')

def extract_sentences(sentences, keywords, n):
    res = []
    for i in range(len(sentences)):
        words = sentences[i].split(' ')
        if any( keyword in words for keyword in keywords):
            res.append(i)
    indexs = []
    for i in res:
        for j in range(i-n, i+n+1, 1):
            # if 0 <= j < len(sentences):
            indexs.append(j)
    indexs = list(filter(lambda x: 0 <= x < len(sentences), indexs))
    indexs = list(set(indexs))
    sen = []
    for i in indexs:
        sen.append(sentences[i])
    return sen

def extract_sentences_for_all(keywords, path=None):
    res = {}
    companies = get_company_names()
    for company in companies[0:5]:
        if path is not None:
            f = codecs.open(path + company.replace('/', ' ')+'.txt', "w", encoding="utf-8")
        print('Working on ' + company)
        res[company] = []
        contents = read_content_from_db(company)
        for row in contents:
            original_sentences = split_content_to_sentences(row['content'])
            sentences = extract_sentences(original_sentences, keywords, 2)
            if len(sentences) > 0:
                new_content = '.\n'.join(sentences)
                res[company].append(LinkContent(company, row['link'], new_content, row['categories']))
                if path is not None:
                    f.write('\n\n======================================================\n')
                    f.write(res[company][-1].link + '\n')
                    f.write(res[company][-1].categories + '\n')
                    f.write(res[company][-1].content + '\n')
    return res


# contents = read_content_from_db()
# companies = get_company_names()
if __name__ == "__main__":
    tmp = extract_sentences_for_all(['supplier', 'suppliers', 'vendor'], path='/Users/keleigong/Dropbox/Python/AUTO_Rating/TextProcessing/')