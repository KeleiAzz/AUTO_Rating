__author__ = 'keleigong'

import MySQLdb
import re
import TextExtraction.hitchecker as Hitchecker

def executeQuery(sql):
    # Open database connection
    db = MySQLdb.connect("localhost", "root", "1423", "ml")

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Fetch all the rows in a list of lists.
        results = cursor.fetchall()
        db.close()
        return results
    except:
        print('Error: Unable to fetch data')
    # disconnect from server
    db.close()

def extract_content_from_profile(keywords, flag, num_sentence, target_path):
    res = executeQuery('SELECT CONVERT(content USING utf8) '
                              'AS content,link,company_name FROM auto_test_link_content;')

    res_size = len(res)

    current_company = res[0][2].replace(',', '')

    extracted_content = "==============\r\n"

    for row in res:
        content = row[0]
        company = row[2].replace(',', '')
        link = row[1]

        print('Current link: ' + link)

        result = Hitchecker.hit_check(content, keywords, flag, num_sentence)


