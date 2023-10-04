import os
from bs4 import BeautifulSoup
from bs4.element import Tag
from datetime import datetime 
import logging
from scrape_records import (
    create_scrape_attempt, record_scrape_success,
    record_scrape_failure
)
from time import sleep 
from typing import Dict, Any, List, Optional
from decimal import Decimal as D
from scrape_navigators import ScrapeNavigator, DummyScrapeNavigator, LoginException, NavigationException

DUMMY_CREDS = ('brl', 'bananas')

class ParsingException(Exception):
    def __init__(self, error: Exception, html_doc: str) -> None:
        self.error = str(error)
        self.html_doc = html_doc


def _get_benefits_from_html(html_doc: str) -> List[Dict[Any, Any]]:
    logging.warning('Parsing benefits')
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
            'issued': D(tds[-2].text),
            'remaining': D(tds[-1].text)
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
            'quantity': D(tds[1].text.strip()),
            'unit': tds[2].text.strip(),
            'item': tds[3].text.strip(),
            'transaction': tds[4].text.strip(),
            'location': tds[5].text.strip()
        }
        transactions.append(transaction)
    
    return transactions


def _get_benefits_expiration_from_html(html_doc: str) -> datetime:
    soup = BeautifulSoup(html_doc, 'html.parser')
    tables = soup.find_all('table')
    table = tables[8]
    tds = table.find_all('td')
    return datetime.strptime(tds[2].text, '%m/%d/%Y')

def _get_navigator(username: str, password: str, use_headless_driver: bool) -> ScrapeNavigator:
    if (username, password) == DUMMY_CREDS:
        return DummyScrapeNavigator(
            login_sleep_seconds=2,
            transactions_sleep_seconds=2,
            benefits_sleep_seconds=2
        )
    return ScrapeNavigator(use_headless_driver)

def scrape_benefits(username: str, password: str, use_headless_driver: bool=True) -> List[Dict[Any, Any]]:
    logging.warning('Scraping benefits')
    navigator = _get_navigator(username, password, use_headless_driver)
    logging.warning('Logging in')
    navigator.login(username, password)
    logging.warning('Fetching benefits HTML doc')
    html_doc = navigator.get_benefits_html_doc()
    logging.warning('Quitting navigator')
    navigator.quit() 

    try:
        benefits = _get_benefits_from_html(html_doc)
    except Exception as e:
        raise ParsingException(error=e, html_doc=html_doc)

    return benefits

def _flatten(l: List[List[Any]]) -> List[Any]:
    return [item for sublist in l for item in sublist]

def scrape_transactions(username: str, password: str, use_headless_driver: bool=True) -> List[Dict[Any, Any]]:
    navigator = _get_navigator(username, password, use_headless_driver)
    navigator.login(username, password)

    max_workers = int(os.environ.get('PROCESS_POOL_EXECUTORS_MAX_WORKERS', 2)) 
    html_docs = navigator.get_transaction_html_docs(max_workers)

    navigator.quit() 

    try:
        tx_lists = [_get_transactions_from_html(html_doc) for html_doc in html_docs]
    except Exception as e:
        raise ParsingException(error=e, html_doc=str(html_docs))
    return _flatten(tx_lists)


def scrape_all(username: str, password: str, token: str) -> None:
    # TODO: could save time by not logging in twice
    benefits = None
    transactions = None
    try:
        benefits = scrape_benefits(username, password)
        transactions = scrape_transactions(username, password)
    except LoginException as e:
        record_scrape_failure(token, 'LOGIN', e.error, e.html_doc, benefits, transactions)
    except (NavigationException, ParsingException) as e:
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

    




