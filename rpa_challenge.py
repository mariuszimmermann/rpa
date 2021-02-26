from RPA.Browser import Browser
from RPA.HTTP import HTTP
import OCR_service
from RPA.Tables import Tables
import pandas as pd
import time
import datetime


browser = Browser()
term = "python"

def open_the_website(url):
    browser.open_available_browser(url)

def get_web_table(df_web_table, table_id):

    i = 2 # rows
    while i < 6:
        no = browser.get_table_cell(table_id, i, 1)
        id = browser.get_table_cell(table_id, i, 2)
        dd = browser.get_table_cell(table_id, i, 3)
        df_web_table = df_web_table.append({'#' : no, 'ID' : id, 'Due Date' : dd}, ignore_index=True)
        i += 1
    return df_web_table

def call_invoice(xp):
    browser.click_element(xp)
    handles = browser.get_window_handles()
    browser.switch_window(handles[len(handles)-1])
    url = browser.get_location()
    browser.switch_window(handles[0])
    return url

def get_invoice_information(df_invoice):
    xp_1 = 'xpath=//*[@id="tableSandbox"]/tbody/tr[1]/td[4]/a'
    xp_2 = 'xpath=//*[@id="tableSandbox"]/tbody/tr[2]/td[4]/a'
    xp_3 = 'xpath=//*[@id="tableSandbox"]/tbody/tr[3]/td[4]/a'
    xp_4 = 'xpath=//*[@id="tableSandbox"]/tbody/tr[4]/td[4]/a'
    xp_values = [xp_1, xp_2, xp_3, xp_4]
    i = 0
    for xp in xp_values:
        url = call_invoice(xp)
        text = OCR_service.ocr_core(url)
        invoice_number = OCR_service.get_invoice_no(text)
        invoice_date = OCR_service.get_invoice_date(text)
        company_name = OCR_service.get_company_name(text)
        total = OCR_service.get_total(text)
        df_invoice = df_invoice.append({'invoice_number' : invoice_number, 'invoice_date' : invoice_date, 'company_name': company_name, 'total' : total}, ignore_index=True)
    return df_invoice

def next_page():
    browser.click_element('xpath=//*[@id="tableSandbox_next"]')

def click_start():
    browser.click_element('xpath=//*[@id="start"]')

def submit():
    browser.choose_file('xpath=//*[@id="submit"]/div/div/div/form/input[1]', 'output.csv')

def create_csv(df_invoice, df_web_table):
    df_output = pd.DataFrame(columns = ['ID', 'DueDate','InvoiceNo','InvoiceDate','CompanyName','TotalDue'])
    i = 0
    while i < len(df_invoice.index):
        date_str = str(df_web_table['Due Date'].values[i])
        date = datetime.datetime.strptime(date_str, '%d-%m-%Y')
        today = datetime.datetime.today().strftime ('%d-%m-%Y')
        today = datetime.datetime.strptime(today, '%d-%m-%Y')
        dif = int((today - date).days)

        if dif >= 0:
            id = str(df_web_table['ID'].values[i])
            dd = str(df_web_table['Due Date'].values[i])
            no = str(df_invoice['invoice_number'].values[i])
            da = str(df_invoice['invoice_date'].values[i])
            cn = str(df_invoice['company_name'].values[i])
            td = str(df_invoice['total'].values[i])

            df_output = df_output.append({'ID' : id, 'DueDate' : dd, 'InvoiceNo' : no, 'InvoiceDate' : da, 'CompanyName' : cn, 'TotalDue' : td}, ignore_index=True)
        i +=1
    print("-> Merged Data:")
    print(df_output)
    print("")
    df_output.to_csv('output.csv', index=False)

def main():
    url = "https://rpachallengeocr.azurewebsites.net"
    df_invoice = pd.DataFrame(columns = ['invoice_number', 'invoice_date','company_name','total'])
    df_web_table = pd.DataFrame(columns = ['#', 'ID', 'Due Date'])
    try:
        open_the_website(url)
        click_start()
        time.sleep(0.2)
        i = 0
        while i < 3:
            print("+++ Scanning Page +++")
            df_web_table = get_web_table(df_web_table, "id:tableSandbox")
            df_invoice = get_invoice_information(df_invoice)
            next_page()
            i += 1
        print("+++ Scanning finished +++")
        print("")
        print("-> Website Information:")
        print(df_web_table)
        print("")
        print("-> Invoice Information:")
        print(df_invoice)
        print("")
        create_csv(df_invoice, df_web_table)
        submit()
        print("+++ Process finished +++")
        print("")
    finally:
        pass
        #browser.close_all_browsers()

# Call the main() function, checking that we are running as a stand-alone script:
if __name__ == "__main__":
    main()
