__author__ = 'keleigong'
from docx import Document
from openpyxl import Workbook

from docx.text.paragraph import Paragraph



def is_section(paragraph):
    if any(run.underline for run in paragraph.runs):
        return True
    else:
        return False

def is_category(paragraph):
    # print(p.text)
    if len(paragraph.text.strip()) > 2 and paragraph.text.strip()[-1] == ':' and any(run.bold for run in paragraph.runs):
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

def generate_rows(doc_file):
    doc = Document(doc_file)
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
                elif p.text[0:4] == 'http' or p.text[0:3] == 'www':
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
    return rows
            # print('\t\t\t' + str(p.text.encode('utf8')), file=f)
    # if len(p.runs) > 1:
    #     print(idx)
    #     for run in p.runs:
    #         print(run.text + '---')
    #     print('----------')

# f.close()
def output_to_excel(rows, output_file):
    wb = Workbook()
    sheet = wb.create_sheet(0, 'output')
    # sheet.append(['link', 'frequency', 'company', 'rank', 'year', 'query',
    #                   'link_type', 'title', 'domain', 'snippet', 'year'])
    for row in rows:
        sheet.append(row.to_list())
    wb.save(output_file)
    print('done')

def get_urls(rows):
    res = {}
    for row in rows:
        if row.company in res.keys():
            if len(row.link) > 5:
                res[row.company].append(row.link)
        else:
            res[row.company] = []
            if len(row.link) > 5:
                res[row.company].append(row.link)
    for key, value in res.items():
        res[key] = list(set(value))
    return res


if __name__ == "__main__":
    doc_file = '/Users/keleigong/Dropbox/Python/AUTO_Rating/TextExtraction/secondary data/2015 secondary data.docx'
    output_file = '2015_secondary_data.xlsx'
    rows = generate_rows(doc_file)
    output_to_excel(rows, output_file)
    company_all_urls = get_urls(rows)
    for key, value in company_all_urls.items():
        print("{0} has\t {1} unique URLs".format(key, len(value)))



# document = dx.opendocx('/Users/keleigong/Dropbox/Python/AUTO_Rating/TextExtraction/(final)2014 SCRC Secondary Data without split.docx')

# print(dx.getdocumenttext(document))

# for p in dx.getdocumenttext(document):
    # print(p)

