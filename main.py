from creds import USERNAME, PASSWORD

from selenium.webdriver.chrome.options import Options
import os
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


USE_HEADLESS_DRIVER = True 
LOGIN_PAGE_URL = 'https://www.wicconnect.com/wicconnectclient/siteLogonClient.recip?state=NEW%20YORK%20WIC&stateAgencyId=1'

def get_driver(headless=True):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN", "")
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))
    return webdriver.Chrome(service=service, options=chrome_options)


def login(driver, username, password):
    driver.get(LOGIN_PAGE_URL)
    username_input = driver.find_element(By.NAME, "login")
    password_input = driver.find_element(By.NAME, "password")
    username_input.send_keys(username)
    password_input.send_keys(password)
    login_button = driver.find_element(By.NAME, "login_but")
    login_button.click()
    message_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "printTable"))
    )

def get_benefits_from_html(html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')
    tables = soup.find_all('table')
    table = tables[9]

    benefits = []

    trs = []
    for class_name in ['RowEven', 'RowOdd']:
        trs += table.find_all('tr', attrs={'class': class_name})
    for tr in trs:
        tds = tr.find_all('td')
        benefit = {
            'name': tds[-4].text.strip(),
            'unit': tds[-3].text,
            'issued': tds[-2].text,
            'remaining': tds[-1].text 
        }
        benefits.append(benefit)
    
    return benefits

    
     

def scrape(username, password):
    driver = get_driver(USE_HEADLESS_DRIVER)
    login(driver, username, password)
    benefits = get_benefits_from_html(driver.page_source)
    print('SCRIPT OUTPUT')
    for benefit in benefits:
        print(f'\n{benefit["name"]}: Issued {benefit["issued"]} {benefit["unit"]}, remaining {benefit["remaining"]} {benefit["unit"]}')


   
    

if __name__ == '__main__':
    scrape(USERNAME, PASSWORD)

