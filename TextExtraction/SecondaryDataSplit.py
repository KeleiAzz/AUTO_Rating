__author__ = 'keleigong'

try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML
import zipfile



"""
Module that extract text from MS XML Word document (.docx).
(Inspired by python-docx <https://github.com/mikemaccana/python-docx>)
"""

WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
PARA = WORD_NAMESPACE + 'p'
TEXT = WORD_NAMESPACE + 't'


def get_docx_text(path):
    """
    Take the path of a docx file as argument, return the text in unicode.
    """
    document = zipfile.ZipFile(path)
    xml_content = document.read('word/document.xml')
    document.close()
    tree = XML(xml_content)

    paragraphs = []
    for paragraph in tree.getiterator(PARA):
        texts = [node.text
                 for node in paragraph.getiterator(TEXT)
                 if node.text]
        if texts:
            paragraphs.append(''.join(texts))

    return '\n'.join(paragraphs)

def secondary_data_split(path):
    text = get_docx_text(path).split('\n')

    # clean = text.split('\n')
    # cleaned_text = [x for x in clean if x != '']
    cleaned_text = text[text.index('I am a panda'):]
    company_profiles = []
    for line in cleaned_text:
        if line == 'I am a panda':
            company_profiles.append('')
        else:
            if len(company_profiles) == 0:
                company_profiles.append('')
            if line[-1] == ':':
                line = '\n' + line
            company_profiles[-1] += '\n' + line

    return company_profiles

def write_to_txt(company_profiles):
    for profile in company_profiles:
        profile = profile.strip()
        company_name = profile[0:profile.index('\n')]
        if '/THE' in company_name:
            company_name = company_name[0:-4]
        content = profile[profile.index('\n'):]
        f = open('/Users/keleigong/Dropbox/Python/AUTO_Rating/TextExtraction/splited_data/' + company_name + '.txt', 'w')
        f.write(content)
        f.close()


data = secondary_data_split('/Users/keleigong/Dropbox/Python/AUTO_Rating/TextExtraction/(final)2014 SCRC Secondary Data.docx')
# text = get_docx_text('/Users/keleigong/Dropbox/Python/AUTO_Rating/TextExtraction/(final)2014 SCRC Secondary Data.docx')
print(data)
write_to_txt(data)