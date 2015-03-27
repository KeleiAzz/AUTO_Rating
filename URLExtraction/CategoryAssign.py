__author__ = 'keleigong'

from openpyxl import load_workbook

def assign_category(url_file, category_file):
    wb = load_workbook(category_file)
    ws = wb.get_active_sheet()
