__author__ = 'keleigong'
'''
This file is not in use
'''
from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams

def to_txt(pdf_path):
    input_ = open(pdf_path, 'rb')
    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    process_pdf(manager, converter, input_)
    return output.getvalue()

# import PyPDF2
from PyPDF2 import PdfFileReader

def to_text2(pdf_path):
    input = open(pdf_path, 'rb')
    pdfReader = PdfFileReader(input)
    # output = StringIO()
    text = ''
    for i in range(pdfReader.getNumPages()):
        text += '\n' + pdfReader.getPage(i).extractText()
    return text
    # pdfReader.read()


