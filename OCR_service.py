'''
Starting virtual env: pipenv shell
'''

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import re
import wget
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

### pytesseract OCR service
def ocr_core(url):
    filename = url[len(url)-6:]
    file_dir = "/files/" + filename
    wget.download(url, file_dir)
    text = pytesseract.image_to_string(Image.open(file_dir))
    return text

### data extraction out of string
def get_invoice_no(text):
    keyword_start = "#"
    start = text.find(keyword_start)
    invoice_no = text[start + len(keyword_start):start + len(keyword_start)+ 10]
    match = re.search(r'(\d+)', invoice_no)
    if match:
        invoice_no = invoice_no[match.start():match.end()]
        return invoice_no
    else:
        raise Exception("OCR error")


def get_invoice_date(text):
    regex_1 = r'(\d{2,4})[.-](\d{2})[.-](\d{2,4})'
    regex_2 = r'[A-Z][a-z]{2}(\s)(\d{1,2})[,](\s)(\d{4})'
    invoice_date = text
    match_1 = re.search(regex_1, invoice_date)
    match_2 = re.search(regex_2, invoice_date)
    if match_1:
        invoice_date = invoice_date[match_1.start():match_1.end()]
        invoice_date = formatting_invoice_date(invoice_date)
        return invoice_date
    elif match_2:
        invoice_date = invoice_date[match_2.start():match_2.end()]
        invoice_date = formatting_invoice_date(invoice_date)
        return invoice_date
    else:
        raise Exception("OCR error")


def get_company_name(text):
    regex_1 = r'Aenean LLC'
    regex_2 = r'Sit Amet Corp.'
    company_name = text
    match_1 = re.search(regex_1, company_name)
    match_2 = re.search(regex_2, company_name)
    if match_1:
        company_name = company_name[match_1.start():match_1.end()]
        return company_name
    elif match_2:
        company_name = company_name[match_2.start():match_2.end()]
        return company_name
    else:
        raise Exception("OCR error")


def get_total(text):
    keyword_start = "Total"
    start = text.rfind(keyword_start)
    total = text[start + len(keyword_start):]
    match = re.search(r'(\d+)[.,]?(\d+)[.,](\d+)', total)
    if match:
        total = total[match.start():match.end()]
        total = formattin_total(total)
        return total
    else:
        raise Exception("OCR error")


### data formatting
def formatting_invoice_date(invoice_date):
    regex_1 = r'(\d{2,4})[.-](\d{2})[.-](\d{2,4})'
    regex_2 = r'[A-Z][a-z]{2}(\s)(\d{2})[,](\s)(\d{4})'
    regex_3 = r'[A-Z][a-z]{2}(\s)(\d{1})[,](\s)(\d{4})'
    match_1 = re.search(regex_1, invoice_date)
    match_2 = re.search(regex_2, invoice_date)
    match_3 = re.search(regex_3, invoice_date)
    if match_1:
        f_invoice_date = invoice_date[8:] + '-'
        f_invoice_date += invoice_date[5:7] + '-'
        f_invoice_date += invoice_date[0:4]
        return f_invoice_date
    elif match_2:
        f_invoice_date = invoice_date[4:6] + '-'
        month_switcher = {
                "Jan": "01",
                "Feb": "02",
                "Mar": "03",
                "Apr": "04",
                "May": "05",
                "Jun": "06",
                "Jul": "07",
                "Aug": "08",
                "Sep": "09",
                "Oct": "10",
                "Nov": "11",
                "Dec": "12",
            }
        f_invoice_date += month_switcher.get(invoice_date[0:3], "NA") + '-'
        f_invoice_date += invoice_date[8:]
        return f_invoice_date
    elif match_3:
        f_invoice_date = '0' + invoice_date[4:5] + '-'
        month_switcher = {
                "Jan": "01",
                "Feb": "02",
                "Mar": "03",
                "Apr": "04",
                "May": "05",
                "Jun": "06",
                "Jul": "07",
                "Aug": "08",
                "Sep": "09",
                "Oct": "10",
                "Nov": "11",
                "Dec": "12",
            }
        f_invoice_date += month_switcher.get(invoice_date[0:3], "NA") + '-'
        f_invoice_date += invoice_date[7:]
        return f_invoice_date
    else:
        raise Exception("formatting error")


def formattin_total(total):
    f_total = ''
    for c in total:
        if re.search(r'\d', c):
            f_total += c
    tmp = f_total[len(f_total)-2:]
    f_total = f_total[:len(f_total)-2]
    f_total += "." + tmp
    return f_total
