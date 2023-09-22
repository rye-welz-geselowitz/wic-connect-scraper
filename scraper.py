from selenium.webdriver.chrome.options import Options
import os
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import concurrent.futures

LOGIN_PAGE_URL = 'https://www.wicconnect.com/wicconnectclient/siteLogonClient.recip?state=NEW%20YORK%20WIC&stateAgencyId=1'

class LoginException(Exception):
    pass

class ScrapingException(Exception):
    def __init__(self, error, html_doc):
        self.error = str(error)
        self.html_doc = html_doc

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
            'issued': float(tds[-2].text),
            'remaining': float(tds[-1].text)
        }
        benefits.append(benefit)
    
    return benefits

def _get_transactions_from_html(html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')
    table = soup.find('table', class_='sort-table')
    if table is None:
        return []

    transactions = []

    trs = []
    for class_name in ['RowEven', 'RowOdd']:
        trs += table.find_all('tr', attrs={'class': class_name})
    for tr in trs:
        tds = tr.find_all('td')
        transaction = {
            'date': tds[0].text.strip(),
            'quantity': float(tds[1].text.strip()),
            'unit': tds[2].text.strip(),
            'item': tds[3].text.strip(),
            'transaction': tds[4].text.strip(),
            'location': tds[5].text.strip()
        }
        transactions.append(transaction)
    
    return transactions


def _get_year_options(driver):
    year_input = driver.find_element(By.NAME, "year")
    year_input.click()
    year_options = year_input.find_elements(By.TAG_NAME, "option")  
    return year_options

def _get_month_options(driver):
    month_input = driver.find_element(By.NAME, "month")
    month_input.click()
    month_options = month_input.find_elements(By.TAG_NAME, "option")    
    return month_options

def _get_transactions(driver):
    transactions = []
    year_idx = 0 
    month_idx = 0
    while True:
        # Select year
        year_options = _get_year_options(driver)
        year_options[year_idx].click()

        # Select month
        month_options = _get_month_options(driver)
        month_options[month_idx].click()

        # Search
        search_button = driver.find_element(By.NAME, 'app_search_button')
        search_button.click()

        WebDriverWait(driver, 3).until(
            EC.url_contains(('trxhistory.recip'))
        )

        # grab transactions
        transactions += _get_transactions_from_html(driver.page_source)

        menu_links = driver.find_elements(By.CLASS_NAME, "menu_link")
        balance_link = menu_links[0]
        assert 'future balance' in balance_link.get_attribute('innerHTML').lower()
        balance_link.click()

        # Why isn't this working?!
        WebDriverWait(driver, 3).until(
            EC.url_contains(('main.recip'))
        )

        if month_idx < len(month_options) - 1:
            month_idx += 1
        elif year_idx < len(year_options) - 1:
            year_idx += 1
            month_idx = 0
        else:
            break

    return transactions


def scrape_benefits(username, password, use_headless_driver=True):
    driver = get_driver(use_headless_driver)

    # Log in 
    try:
        login(driver, username, password)
    except Exception as e:
        driver.quit()
        raise LoginException(e)
    
    # scrape_benefits 
    html_doc = driver.page_source
    try:
        benefits = get_benefits_from_html(html_doc)
    except Exception as e:
        driver.quit()
        raise ScrapingException(error=e, html_doc=html_doc)

    driver.quit()
    return benefits


def scrape_transactions(username, password, use_headless_driver=True):
    driver = get_driver(use_headless_driver)
    # Log in 
    try:
        login(driver, username, password)
    except Exception as e:
        driver.quit()
        raise LoginException(e)
    
    # Scrape transactions
    try:
        transactions = _get_transactions(driver)
    except Exception as e:
        html_doc = driver.page_source
        driver.quit()
        raise ScrapingException(error=e, html_doc=html_doc)

    driver.quit()
    return transactions

