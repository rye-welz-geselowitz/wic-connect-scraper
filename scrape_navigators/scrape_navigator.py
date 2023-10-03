
from typing import List 
import logging 
from selenium.webdriver.chrome.options import Options
import os
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait # type: ignore
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from datetime import datetime 
import concurrent.futures

SLEEP_ON_TEST_DATA = bool(int(os.environ.get('SLEEP_ON_TEST_DATA', 1))) 
LOGIN_PAGE_URL = 'https://www.wicconnect.com/wicconnectclient/siteLogonClient.recip?state=NEW%20YORK%20WIC&stateAgencyId=1'



class ScrapingException(Exception):
    def __init__(self, error: Exception, html_doc: str) -> None:
        self.error = str(error)
        self.html_doc = html_doc
    
class LoginException(ScrapingException):
     pass

class NavigationException(ScrapingException):
     pass

class ScrapeNavigator:
    def __init__(self, use_headless_driver: bool=True) -> None:
        self.driver = self._get_driver(use_headless_driver)
    
    def quit(self) -> None:
        self.driver.quit()
    
    def login(self, username: str, password: str) -> None:
        try:
            self._login(username, password)
        except Exception as e:
            html_doc = self.driver.page_source
            self.driver.quit()
            raise LoginException(e, html_doc)      

    def get_benefits_html_doc(self) -> str:
       return self.driver.page_source 

    def get_transaction_html_docs(self, max_workers: int) -> List[str]:
        try:
            return self._get_transaction_html_docs(max_workers)
        except Exception as e:
            html_doc = self.driver.page_source
            self.driver.quit()
            raise NavigationException(error=e, html_doc=html_doc)

    def _get_transaction_html_docs(self, max_workers: int) -> List[str]:
        year_idxs = list(range(0, datetime.now().year - 2019 + 1))
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            args = [(
                self,
                year_idx,
            ) for year_idx in year_idxs]
            html_doc_lists = executor.map(self._get_transactions_html_docs_for_year, *zip(*args))
        return [html_doc for html_docs in html_doc_lists for html_doc in html_docs]


    def _login(self, username: str, password: str) -> None:
        logging.warning('Logging in')
        self.driver.get(LOGIN_PAGE_URL)
        username_input = self.driver.find_element(By.NAME, "login")
        password_input = self.driver.find_element(By.NAME, "password")
        username_input.send_keys(username)
        password_input.send_keys(password)
        login_button = self.driver.find_element(By.NAME, "login_but")
        login_button.click()
        logging.warning('Clicked the login button')
        message_element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.ID, "printTable"))
        )

    def _get_year_options(self) -> List[WebElement]:
        year_input = self.driver.find_element(By.NAME, "year")
        year_input.click()
        year_options = year_input.find_elements(By.TAG_NAME, "option")  
        return year_options

    def _get_month_options(self) -> List[WebElement]:  
        month_input = self.driver.find_element(By.NAME, "month")
        month_input.click()
        month_options = month_input.find_elements(By.TAG_NAME, "option")    
        return month_options

    def _get_driver(self, headless: bool=True) -> webdriver.Chrome:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN", "")
        if headless:
            chrome_options.add_argument("--headless") # type: ignore
        chrome_options.add_argument("--disable-dev-shm-usage") # type: ignore
        chrome_options.add_argument("--no-sandbox") # type: ignore
        service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))
        return webdriver.Chrome(service=service, options=chrome_options)

    def _get_transactions_html_docs_for_year(self, year_idx: int) -> List[str]:
        logging.warning(f'Fetching benefits for year_idx {year_idx}')
        html_docs: List[str] = []
        month_idx = 0
        while True:
            # Select year
            year_options = self._get_year_options()
            year_options[year_idx].click()

            # Select month
            month_options = self._get_month_options()
            month_options[month_idx].click()

            logging.warning(f'Fetching benefits for month_idx {month_idx}')
            # Search
            search_button = self.driver.find_element(By.NAME, 'app_search_button')
            search_button.click()

            WebDriverWait(self.driver, 3).until(
                EC.url_contains(('trxhistory.recip'))
            )

            # grab transactions
            html_docs += self.driver.page_source

            menu_links = self.driver.find_elements(By.CLASS_NAME, "menu_link")
            balance_link = menu_links[0]
            assert 'future balance' in (balance_link.get_attribute('innerHTML') or '').lower()
            balance_link.click()

            WebDriverWait(self.driver, 3).until(
                EC.url_contains(('main.recip'))
            )

            if month_idx < len(month_options) - 1:
                month_idx += 1
            else:
                break

        return html_docs
