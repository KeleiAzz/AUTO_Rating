__author__ = 'keleigong'
from openpyxl import load_workbook
from openpyxl import Workbook


def seperate_companies(filename):
    wb = load_workbook(filename)
    ws = wb.get_active_sheet()
    # company_names = list(set(map(lambda x: x.value, ws.column[0])))
    # for company_name in company_names:
    #     out = Workbook(write_only=True)
    #     url_sheet = out.create_sheet(0, 'links')
    urls = {}
    for row in ws.rows:
        if row[0].value in urls.keys():
            urls[row[0].value].append(row[2].value)
        else:
            urls[row[0].value] = []
    print(urls.keys())
    for company in urls.keys():
        out = Workbook(write_only=True)
        url_sheet = out.create_sheet(0, 'links')
        for url in urls[company]:
            url_sheet.append([url])
        out.save(company + '.xlsx')