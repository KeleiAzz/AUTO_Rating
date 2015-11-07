__author__ = 'keleigong'
import pymysql

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='1423',
                             db='ml',
                             # charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

cur = connection.cursor()
sql = "SELECT `link` FROM `link_content_2014` WHERE `company_name`=%s"
cur.execute(sql,('ABBOTT LABORATORIES',))
for row in cur:
    print(row)


try:
    # with connection.cursor() as cursor:
    #     # Create a new record
    #     sql = "INSERT INTO `users` (`email`, `password`) VALUES (%s, %s)"
    #     cursor.execute(sql, ('webmaster@python.org', 'very-secret'))

    # connection is not autocommit by default. So you must commit to save
    # your changes.
    # connection.commit()

    # with connection.cursor() as cursor:
    cursor = connection.cursor()
    # Read a single record
    sql = "SELECT `link` FROM `link_content_2014` WHERE `company_name`=%s"
    cursor.execute(sql, ('ABBOTT LABORATORIES',))
    # print(cursor.description)
    # result = cursor.fetchone()
    for row in cursor:
        print(row)
    # print(result)
finally:
    connection.close()