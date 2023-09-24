import pdfplumber
from datetime import datetime


def pdf_to_txt(file_path):
    with pdfplumber.PDF(open(file=file_path, mode='rb')) as pdf:
        pages = [page.extract_text() for page in pdf.pages]
    text = ''.join(pages)

    return text


def get_now():
    now = datetime.now()
    return now.strftime("%d-%m-%Y_%H-%M-%S.%f")


def save_file(path, data):
    with open(path, "w") as file:
        file.write(data)