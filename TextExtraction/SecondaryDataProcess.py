__author__ = 'keleigong'
from docx import Document
from openpyxl import Workbook

from docx.text.paragraph import Paragraph

doc = Document('/Users/keleigong/Dropbox/Python/AUTO_Rating/TextExtraction/2011 Secondary (Part I).docx')

def is_section(paragraph):
    if any(run.underline for run in paragraph.runs):
        return True
    else:
        return False

def is_category(paragraph):
    # print(p.text)
    if len(paragraph.text.strip()) > 2 and paragraph.text.strip()[-1] == ':':
        return True
    elif any(run.bold for run in paragraph.runs) and all(not run.underline for run in paragraph.runs):
        return True
    else:
        return False

def is_brief(paragraph):
    if not is_section(paragraph) and not is_category(paragraph) and paragraph.text[0:4] != 'http':
        return True
    return False

class row:
    def __init__(self, company, section, category, link='N/A', brief='N/A'):
        self.company = company
        self.section = section
        self.category = category
        if link == '':
            self.link = 'N/A'
        else:
            self.link = link

        if brief == '':
            self.brief = 'N/A'
        else:
            self.brief = brief

    def to_list(self):
        return [self.company, self.section, self.category, self.link, self.brief]

    def __str__(self):
        return self.company + '\n' + self.section + '\n' + self.category + '\n' + self.link + '\n' + self.brief


company_name = []
processed_data = []
rows = []
current_company = ''
current_section = ''
current_category = ''
current_link = ''
current_brief = ''
# f = open('processed.txt', 'w')

for idx, p in enumerate(doc.paragraphs):
    if len(p.text.strip()) > 1:
        if 'Heading 1' in p.style.name:
            # print(p.text)
            # company_name.append(p.text)
            previous_p = p
            current_company = p.text.replace('\n', '').strip()
            # print('=========================',file=f)
            print(current_company)
        else:
            if is_section(p):
                current_section = p.text
                previous_p = p
                # print('----------------', file=f)
                # print('\t>>>' + str(p.text), file=f)
            elif is_category(p):
                if not is_section(previous_p):
                    rows.append(row(current_company, current_section, current_category, current_link, current_brief))
                    current_link, current_brief = '', ''
                current_category = p.text.replace(':', '').replace('N/A', '').replace('NA', '').strip()
                previous_p = p
                # print('\t\t>>' + str(p.text.encode('utf8')), file=f)
            elif p.text[0:4] == 'http':
                if current_link != '' and current_brief != '':
                    rows.append(row(current_company, current_section, current_category, current_link, current_brief))
                    current_link, current_brief = '', ''
                current_link = p.text
                previous_p = p
                # print('\t\t\t>' + p.text, file=f)
            else:
                if is_brief(previous_p):
                    current_brief += p.text
                else:
                    current_brief = p.text
                previous_p = p
            # print('\t\t\t' + str(p.text.encode('utf8')), file=f)
    # if len(p.runs) > 1:
    #     print(idx)
    #     for run in p.runs:
    #         print(run.text + '---')
    #     print('----------')

# f.close()
wb = Workbook()

sheet = wb.create_sheet(0, 'output')
# sheet.append(['link', 'frequency', 'company', 'rank', 'year', 'query',
#                   'link_type', 'title', 'domain', 'snippet', 'year'])
for row in rows:
    sheet.append(row.to_list())
wb.save('2011_secondary_data_I.xlsx')
print('done')


# Using the old version docx module"
# import TextExtraction.docx_py2 as dx

# document = dx.opendocx('/Users/keleigong/Dropbox/Python/AUTO_Rating/TextExtraction/(final)2014 SCRC Secondary Data without split.docx')

# print(dx.getdocumenttext(document))

# for p in dx.getdocumenttext(document):
    # print(p)

