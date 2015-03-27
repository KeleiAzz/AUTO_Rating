__author__ = 'keleigong'

from openpyxl import load_workbook
from openpyxl import Workbook

def assign_category(url_file, category_file):
    keyword_category = get_keyword_category(category_file)
    wb = load_workbook(url_file, read_only=True)
    out = Workbook(write_only=True)
    url_category = out.create_sheet(0, 'url_category')
    ws = wb.get_sheet_by_name('output')

    for row in ws.rows:
        if not isinstance(row[1].value, str) and row[1].value > 1:
            queries = row[5].value.split(', ')
            queries = [query.replace(row[2].value + ' ', "") for query in queries]
            print(queries)
            categories = set()
            for query in queries:
                [categories.add(x) for x in keyword_category[query]]
            categories = '@_@'.join(list(categories))
            url_category.append([row[2].value, categories, row[0].value])
    out.save('for_database.xlsx')


def get_keyword_category(category_file):
    wb = load_workbook(category_file, read_only=True)
    ws = wb.get_active_sheet()
    keyword_category = {}
    for row in ws.rows:
        keyword_category[row[0].value.strip()] = [x.strip() for x in row[1].value.split(',')]
    keyword_category.pop('Keywords')
    return keyword_category