__author__ = 'keleigong'
import pymysql
from os import listdir
from os.path import isfile, join
from TextProcessing.PreProcess import LinkContent

TABLE_NAME = "link_content_260"
BASE_DIR = '/Users/keleigong/Google Drive/SCRC 2015 work/auto-rating/8th/company_profiles/'
DB = 'ml_2015'
YEAR = 2015

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
                                 db=DB,
                                 # charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor,
                                 autocommit=True)
    # sql = "SELECT `link` FROM `link_content_2014` WHERE `company_name`=%s"
    # for linkcontent in all_linkcontent:
    if len(linkcontent.content) > 200:
        try:
            cur = connection.cursor()
            sql = "INSERT INTO `" + TABLE_NAME + "` (`company`, `link`, `content`, `categories`, `year`) VALUES ( %s, %s, %s, %s, %s)"
            cur.execute(sql, (linkcontent.company, linkcontent.link, linkcontent.content, linkcontent.categories, YEAR,))
            connection.close()
        except Exception as what:
            print(what, linkcontent.link, len(linkcontent.content))
            connection.close()
    # connection.commit()

if __name__ == "__main__":
    # dir_path = BASE_DIR
    all_linkcontent = ReadDownloadedContent(BASE_DIR)


# Connect to the database
# connection = pymysql.connect(host='localhost',
#                              user='root',
#                              password='1423',
#                              db='ml',
#                              # charset='utf8mb4',
#                              cursorclass=pymysql.cursors.DictCursor)
#
# cur = connection.cursor()
# sql = "SELECT `link` FROM `link_content_2014` WHERE `company_name`=%s"
# cur.execute(sql,('ABBOTT LABORATORIES',))
# for row in cur:
#     print(row)

