from selenium.webdriver.chrome.options import Options
import os
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait # type: ignore
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from bs4.element import Tag
import concurrent.futures
from datetime import datetime 
import logging
from scrape_records import (
    create_scrape_attempt, record_scrape_success,
    record_scrape_failure
)
from time import sleep 
from typing import Dict, Any, List
from selenium.webdriver.remote.webelement import WebElement

SLEEP_ON_TEST_DATA = bool(int(os.environ.get('SLEEP_ON_TEST_DATA', 1))) 
LOGIN_PAGE_URL = 'https://www.wicconnect.com/wicconnectclient/siteLogonClient.recip?state=NEW%20YORK%20WIC&stateAgencyId=1'

DUMMY_CREDS = ('brl', 'bananas')
TEST_BENEFITS = [
    {
        'name': 'MILK',
        'unit': 'GALLON',
        'issued': 2,
        'remaining': 1
    },
    {
        'name': 'CEREAL',
        'unit': 'OUNCE',
        'issued': 36,
        'remaining': 18
    },
    {
        'name': 'EGGS',
        'unit': 'DOZEN',
        'issued': 1,
        'remaining': 1
    }
]

TEST_TRANSACTIONS = [
    {
            'date': '01/03/2023',
            'quantity': 2,
            'unit': 'CONTAINER',
            'item': 'GERBER 2FOODS BANANA BLACKBERRY BLUEBERRY 2PK*4OZ',
            'transaction': 'WIC PURCHASE',
            'location': 'CTOWN'
    },
    {
            'date': '01/04/2023',
            'quantity': 1,
            'unit': 'CONTAINER',
            'item': 'GERBER 2FOODS BANANA BLACKBERRY BLUEBERRY 2PK*4OZ',
            'transaction': 'WIC PURCHASE',
            'location': 'CTOWN'
    },
    {
            'date': '02/04/2023',
            'quantity': 1.5,
            'unit': 'GALLON',
            'item': 'GALLON	LACTAID LACTOSE FREE WHOLE MILK 96OZ',
            'transaction': 'WIC PURCHASE',
            'location': 'CTOWN'
    },
    {
            'date': '02/04/2023',
            'quantity': 2.01,
            'unit': 'CASH VALUE BENEFIT(CVB)',
            'item': 'BANANAS; YELLOW',
            'transaction': 'WIC PURCHASE',
            'location': 'CTOWN'
    },
]



class ScrapingException(Exception):
    def __init__(self, error: Exception, html_doc: str) -> None:
        self.error = str(error)
        self.html_doc = html_doc
    
class LoginException(ScrapingException):
     pass


def _get_driver(headless: bool=True) -> webdriver.Chrome:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN", "")
    if headless:
        chrome_options.add_argument("--headless") # type: ignore
    chrome_options.add_argument("--disable-dev-shm-usage") # type: ignore
    chrome_options.add_argument("--no-sandbox") # type: ignore
    service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))
    return webdriver.Chrome(service=service, options=chrome_options)


def _login(driver: webdriver.Chrome, username: str, password: str) -> None:
    logging.warning('Logging in')
    driver.get(LOGIN_PAGE_URL)
    username_input = driver.find_element(By.NAME, "login")
    password_input = driver.find_element(By.NAME, "password")
    username_input.send_keys(username)
    password_input.send_keys(password)
    login_button = driver.find_element(By.NAME, "login_but")
    login_button.click()
    logging.warning('Clicked the login button')
    message_element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "printTable"))
    )

def _get_benefits_from_html(html_doc: str) -> List[Dict[Any, Any]]:
    soup = BeautifulSoup(html_doc, 'html.parser')
    tables = soup.find_all('table')
    table = tables[9]

    benefits = []

    trs = table.find_all('tr', attrs={'class': ['RowEven', 'RowOdd']})
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

def _get_transactions_from_html(html_doc: str) -> List[Dict[Any, Any]]:
    soup = BeautifulSoup(html_doc, 'html.parser')
    table = soup.find('table', class_='sort-table')
    if table is None:
        return []

    transactions = []

    assert isinstance(table, Tag)

    trs = table.find_all('tr', attrs={'class': ['RowEven', 'RowOdd']})
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


def _get_year_options(driver: webdriver.Chrome) -> List[WebElement]:
    year_input = driver.find_element(By.NAME, "year")
    year_input.click()
    year_options = year_input.find_elements(By.TAG_NAME, "option")  
    return year_options

def _get_month_options(driver: webdriver.Chrome) -> List[WebElement]:  
    month_input = driver.find_element(By.NAME, "month")
    month_input.click()
    month_options = month_input.find_elements(By.TAG_NAME, "option")    
    return month_options

def _get_benefits_expiration_from_html(html_doc: str) -> datetime:
    soup = BeautifulSoup(html_doc, 'html.parser')
    tables = soup.find_all('table')
    table = tables[8]
    tds = table.find_all('td')
    return datetime.strptime(tds[2].text, '%m/%d/%Y')

def _get_transactions(driver: webdriver.Chrome, year_idx: int) -> List[Dict[Any, Any]]:
    transactions = []
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
        assert 'future balance' in (balance_link.get_attribute('innerHTML') or '').lower()
        balance_link.click()

        WebDriverWait(driver, 3).until(
            EC.url_contains(('main.recip'))
        )

        if month_idx < len(month_options) - 1:
            month_idx += 1
        else:
            break

    return transactions


def scrape_benefits(username: str, password: str, use_headless_driver:bool=True) -> List[Dict[Any, Any]]:
    if (username, password) == DUMMY_CREDS:
        if SLEEP_ON_TEST_DATA:
            sleep(2)
        return TEST_BENEFITS

    driver = _get_driver(use_headless_driver)

    # Log in 
    try:
        _login(driver, username, password)
    except Exception as e:
        html_doc = driver.page_source
        driver.quit()
        raise LoginException(e, html_doc)
    
    # scrape_benefits 
    html_doc = driver.page_source
    try:
        benefits = _get_benefits_from_html(html_doc)
    except Exception as e:
        driver.quit()
        raise ScrapingException(error=e, html_doc=html_doc)

    driver.quit()
    return benefits


def _scrape_transactions_for_year(username: str, password: str, year_idx: int, use_headless_driver: bool=True) -> List[Dict[Any, Any]]:
    driver = _get_driver(use_headless_driver)
    # Log in 
    try:
        _login(driver, username, password)
    except Exception as e:
        page_source = driver.page_source
        driver.quit()
        raise LoginException(e, page_source)
    
    # Scrape transactions
    try:
        transactions = _get_transactions(driver, year_idx)
    except Exception as e:
        html_doc = driver.page_source
        driver.quit()
        raise ScrapingException(error=e, html_doc=html_doc)

    driver.quit()
    return transactions

def _flatten(l: List[List[Any]]) -> List[Any]:
    return [item for sublist in l for item in sublist]

def scrape_transactions(username: str, password: str, use_headless_driver: bool=True) -> List[Dict[Any, Any]]:
    if (username, password) == DUMMY_CREDS:
        if SLEEP_ON_TEST_DATA:
            sleep(10)
        return TEST_TRANSACTIONS

    year_idxs = list(range(0, datetime.now().year - 2019 + 1))
    with concurrent.futures.ProcessPoolExecutor() as executor:
        args = [(
            username,
            password,
            year_idx,
            use_headless_driver,
        ) for year_idx in year_idxs]
        mapped = executor.map(_scrape_transactions_for_year, *zip(*args))
        transactions = list(mapped)
    return _flatten(transactions)

def scrape_all(username: str, password: str, token: str) -> None:
    # TODO: could save time by not logging in twice
    benefits = None
    transactions = None
    try:
        benefits = scrape_benefits(username, password)
        transactions = scrape_transactions(username, password)
    except LoginException as e:
        record_scrape_failure(token, 'LOGIN', e.error, e.html_doc, benefits, transactions)
    except ScrapingException as e:
        failure_stage = 'BENEFITS' if benefits is None else 'TRANSACTIONS'
        record_scrape_failure(
            token, f'SCRAPING_{failure_stage}', e.error, e.html_doc,
            benefits,
            transactions
        )
    except Exception as e:
        record_scrape_failure(token, 'UNKNOWN', str(e), None, benefits, transactions)
    else:
        record_scrape_success(token, benefits, transactions)

    




