__author__ = 'keleigong'

import MySQLdb


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
