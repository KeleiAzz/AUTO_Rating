from os import listdir
from os.path import isfile, join
from openpyxl import Workbook
import string

mypath = '/Users/keleigong/Google Drive/SCRC 2015 work/extract_sentenses_for_NLP'

file_names= [f for f in listdir(mypath) if isfile(join(mypath, f)) and 'DS_Store' not in f]

# keywords_path = '/Users/keleigong/Google Drive/SCRC 2015 work/2014_data/fourth run/d.sentences/CM/'

keywords = [
        'Ariba spend management',
        'Sourcing contract management system',
        'EDI',
        'EICC',
        'Electronic Industry Citizenship Coalition',
        'Enterprise Resource Planning',
        'e-procurement system',
        'ERP',
        'Supplier terminate',
        'Oracle',
        'Procurement',
        'Procurement team',
        'Procure-to-Pay system',
        'SAP',
        'Service Level Agreement',
        'Source approved vendor list',
        'Sourcing Process',
        'Spend management',
        'Spend analytics',
        'Supplier allocation',
        'Supplier assessment',
        'Supplier audit',
        'Supplier award',
        'Supplier code of conduct',
        'Supplier database',
        'Supplier diversity program',
        'Supplier evaluation',
        'Supplier expectation',
        'Supplier guideline',
        'Supplier list',
        'Supplier measurements',
        'Supplier portal',
        'Supplier purchase terms and conditions',
        'Supplier registration',
        'Supplier requirement',
        'Supplier scorecard',
        'Supplier selection',
        'Supplier tracking',
        'Supplier training',
        'Supply chain management',
        'Supply management system',
        'Vendor code of conduct',
        'Vendor expectation',
        'Vendor list',
        'Vendor management',
]

links = {}
sentenses = {}
rows = []

for f in file_names:
    company_name = f.replace('.txt', '')
    links[company_name] = []
    sentenses[company_name] = []
    file_path = join(mypath, f)
    # print(f)
    file = open(file_path, 'r', encoding='ascii', errors='ignore')

    # content = [line.decode('utf-8').strip().replace(u'0xe2', '') for line in file.readlines()]
    lines = file.readlines()
    file.close()
    for line in lines:
        if line[0:4] == 'http':
            links[company_name].append(line)
        elif line[0:4] != '====' and line[0:4] != 'http':
            sentenses[company_name].append(line)

    for sentense_single_line in sentenses[company_name]:
        sentense_list = sentense_single_line.split('!@#$%^')
        sentense_list = [s for s in sentense_list if len(s)>5]
        for sentense in sentense_list:
            contain_keywords = []
            for keyword in keywords:
                if keyword.lower() in sentense.lower():
                    contain_keywords.append(keyword)
            # sentense = str(sentense.encode('utf-8'))[2:-1]
            # sentense = filter(lambda x: x in string.printable, sentense)
            if len(contain_keywords) == 0:
                row = [company_name, 'N/A', str(sentense)]
            else:
                row = [company_name, '#$#'.join(contain_keywords), str(sentense)]
            rows.append(row)

f = open('NLP.txt', 'w')

for row in rows:
    print('!@#$%^'.join(row), file=f)

f.close()

# wb = Workbook()
# previous = rows[0][0]
# sheet = wb.create_sheet(0, previous)
# sheet_no = 1
#
# for row in rows:
#     if row[0] == previous:
#         try:
#             sheet.append(row)
#         except Exception as e:
#             print(e)
#             print(row)
#         previous = row[0]
#     else:
#         sheet = wb.create_sheet(sheet_no, row[0])
#         try:
#             sheet.append(row)
#         except Exception as e:
#             print(e)
#             print(row)
#         sheet_no += 1
#         previous = row[0]
#
# wb.save('NLP.xlsx')

print('done')

# f = open('/Users/keleigong/Google Drive/SCRC 2015 work/extract_sentenses_for_NLP/adt corp.txt', 'r', encoding='utf-8', errors='ignore')
#
# c = f.readlines()




