import codecs

__author__ = 'keleigong'
import re
import pymysql
from TextProcessing.PreProcess import LinkContent, ReadDownloadedContent
from TextProcessing.Keywords import SM_step2, SS_step2, CM_step2, SRM_step2, LHR_step2, ES_step2
from TextProcessing.Keywords import SM_original, SS_original, CM_original, SRM_original, LHR_original, ES_original
import os
step1_0 = [
    "Ariba",
    "EDI",
    "EICC",
    "Electronic data interchange",
    "Electronic Industry Citizenship Coalition",
    "Enterprise Resource Planning",
    "ERP",
    "green supply",
    "ILO",
    "International labor association",
    "Oracle",
    "procurement",
    "procurements",
    "purchasing",
    "SAP",
    "social",
    "sourcing",
    "spend management",
    "supply chain",
    "Sustainable supply"
]

step1_1 = [
    "second tier",
    "source",
    "sources",
    "sub tier",
    "subtier",
    "supplier",
    "suppliers",
    "vendor",
    "vendors"
]

step1_2 = [
    "contractor",
    "contractors",
    "partner",
    "partners",
    "provider",
    "providers",
    "sub contractor",
    "sub contractors",
    "subcontractor",
    "subcontractors"
]

def get_company_names():
    conn = pymysql.connect(host='localhost',
                           user='root',
                           password='1423',
                           db='ml_2015',
                           cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()
    sql = "SELECT DISTINCT `company` FROM `link_content_13_15`"
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
    sql = "SELECT `link`, `content`, `categories`, `year` FROM `link_content_13_15` WHERE `company`=%s AND `link` not like \"%%sec.gov/Archives%%\" "
    cur.execute(sql, (company,))
    res = []
    for row in cur:
        res.append(LinkContent(company, row['link'], row['content'], row['categories'], row['year']))
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
        # words = sentences[i].split(' ')
        if any(keyword.lower() in sentences[i] for keyword in keywords):
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

def extract_sentences_from_DB(keywords_0, keywords_1=None, keywords_2=None, path=None, num_sen=1, category="ALL"):
    res = {}
    companies = get_company_names()
    if path is not None:
        if category != "ALL":
            path = path + category + '/'
        try:
            os.makedirs(path + '2015/')
        except:
            pass
        try:
            os.makedirs(path + '2013/')
        except:
            pass
        try:
            os.makedirs(path + '2014/')
        except:
            pass

    for company in companies:
        contents = read_content_from_db(company)
        if len(contents) == 0:
            continue
        if path is not None and len(contents) > 0:
            f = codecs.open(path + str(contents[0].year) + '/' + company.replace('/', ' ')+'.txt', "w", encoding="utf-8")
        print('Working on ' + company)
        res[company] = []

        for row in contents:
            if category == 'ALL':
                original_sentences = split_content_to_sentences(row.content)
                if keywords_0 is not None:
                    sentences = extract_sentences(original_sentences, keywords_0, num_sen)
                else:
                    sentences = original_sentences
                sentences_2 = []
                if keywords_1 is not None:
                    sentences_2 = extract_sentences(original_sentences, keywords_1, num_sen)
                if keywords_2 is not None and len(sentences_2) == 0:
                    # print("NO hit in keywords 0")
                    sentences_2 = extract_sentences(original_sentences, keywords_2, num_sen)
                sentences += sentences_2
                sentences = list(set(sentences))
                if len(sentences) > 0:
                    new_content = '.\n'.join(sentences)
                    res[company].append(LinkContent(company, row.link, new_content, row.categories))
                    if path is not None:
                        f.write('\n\n======================================================\n')
                        f.write(res[company][-1].link + '\n')
                        f.write(res[company][-1].categories + '\n')
                        f.write(res[company][-1].content + '\n')
            elif category in row.categories:
                original_sentences = split_content_to_sentences(row.content)
                if keywords_0 is not None:
                    sentences = extract_sentences(original_sentences, keywords_0, num_sen)
                else:
                    sentences = original_sentences
                sentences_2 = []
                if keywords_1 is not None:
                    sentences_2 = extract_sentences(original_sentences, keywords_1, num_sen)
                if keywords_2 is not None and len(sentences_2) == 0:
                    # print("NO hit in keywords 0")
                    sentences_2 = extract_sentences(original_sentences, keywords_2, num_sen)
                sentences += sentences_2
                sentences = list(set(sentences))
                if len(sentences) > 0:
                    new_content = '.\n'.join(sentences)
                    res[company].append(LinkContent(company, row.link, new_content, row.categories))
                    if path is not None:
                        f.write('\n\n======================================================\n')
                        f.write(res[company][-1].link + '\n')
                        f.write(res[company][-1].categories + '\n')
                        f.write(res[company][-1].content + '\n')

    return res

def extract_sentences_from_dir(keywords_0, keywords_1=None, keywords_2=None, category="ALL", in_path=None, out_path=None, num_sen=1):
    res = {}
    all_link_content = ReadDownloadedContent(in_path, output=None)
    companies = {}
    for link_content in all_link_content:
        if link_content.company in companies.keys():
            companies[link_content.company].append(link_content)
        else:
            companies[link_content.company] = [link_content]
    if out_path is not None:
        try:
            os.makedirs(out_path)
        except:
            print("dir already there")
    for company, contents in companies.items():
        if out_path is not None:
            f = codecs.open(out_path + company.replace('/', ' ')+'.txt', "w", encoding="utf-8")
        print('Working on ' + company)
        res[company] = []
        # contents = read_content_from_db(company)
        for row in contents:
            if category == "ALL":
                original_sentences = split_content_to_sentences(row.content)
                if keywords_0 is None:
                    sentences = original_sentences
                else:
                    sentences = extract_sentences(original_sentences, keywords_0, num_sen)
                if len(sentences) == 0 and keywords_1 is not None:
                    # print("NO hit in keywords 0")
                    sentences = extract_sentences(original_sentences, keywords_1, num_sen)
                if len(sentences) == 0 and keywords_2 is not None:
                    # print("NO hit in keywords 1")
                    sentences = extract_sentences(original_sentences, keywords_2, num_sen)
                if len(sentences) > 0:
                    new_content = '.\n'.join(sentences)
                    res[company].append(LinkContent(company, row.link, new_content, row.categories))
                    if out_path is not None:
                        f.write('\n\n======================================================\n')
                        f.write(res[company][-1].link + '\n')
                        f.write(res[company][-1].categories + '\n')
                        f.write(res[company][-1].content + '\n')
            elif category in row.categories:
                original_sentences = split_content_to_sentences(row.content)
                if keywords_0 is None:
                    sentences = original_sentences
                else:
                    sentences = extract_sentences(original_sentences, keywords_0, num_sen)
                if len(sentences) == 0 and keywords_1 is not None:
                    # print("NO hit in keywords 0")
                    sentences = extract_sentences(original_sentences, keywords_1, num_sen)
                if len(sentences) == 0 and keywords_2 is not None:
                    # print("NO hit in keywords 1")
                    sentences = extract_sentences(original_sentences, keywords_2, num_sen)
                if len(sentences) > 0:
                    new_content = '.\n'.join(sentences)
                    res[company].append(LinkContent(company, row.link, new_content, row.categories))
                    if out_path is not None:
                        f.write('\n\n======================================================\n')
                        f.write(res[company][-1].link + '\n')
                        f.write(res[company][-1].categories + '\n')
                        f.write(res[company][-1].content + '\n')
    return res

def two_step(text_files_path, step1_save_path, step2_save_path):
    extract_sentences_from_dir(step1_0, step1_1, step1_2,
                               in_path=text_files_path,
                               out_path=step1_save_path,
                               num_sen=3)

    keywords = {"SS": SS_step2, "CM": CM_step2, "SRM": SRM_step2, "LHR": LHR_step2, "ES": ES_step2,
                "SM": SM_step2}
    for category, keyword in keywords.items():
        tmp = extract_sentences_from_dir(
            keyword,
            category=category,
            in_path=step1_save_path,
            out_path=step2_save_path + "{}/".format(category),
            num_sen=0,
        )


def sentence(text_files_path, output_path):
    keywords = {"SS": SS_original, "CM": CM_original, "SRM": SRM_original, "LHR": LHR_original, "ES": ES_original,
                "SM": SM_original}
    for category, keyword in keywords.items():
        tmp = extract_sentences_from_dir(
            keyword,
            category=category,
            in_path=text_files_path,
            out_path=output_path + "{}/".format(category),
            num_sen=0,
        )

def full_text(text_files_path, output_path):
    categories = ["CM", "SS", "SM", "LHR", "ES", "SRM"]
    for category in categories:
        extract_sentences_from_dir(None,
                                   category=category,
                                   in_path=text_files_path,
                                   out_path=output_path + "{}/".format(category),)


# contents = read_content_from_db()
# companies = get_company_names()
if __name__ == "__main__":
    # two_step("/home/scrc/Documents/WebContent/company_profiles/",
    #          "/home/scrc/Documents/WebContent/step1/",
    #          "/home/scrc/Documents/WebContent/step2/",)

    # sentence("/home/scrc/Documents/WebContent/company_profiles/",
    #          "/home/scrc/Documents/WebContent/sentence/")

    full_text("/home/scrc/Documents/WebContent/company_profiles/",
              "/home/scrc/Documents/WebContent/full_text/")