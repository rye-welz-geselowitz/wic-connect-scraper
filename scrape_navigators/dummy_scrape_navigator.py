from .scrape_navigator import ScrapeNavigator
import logging 
from time import sleep 
from typing import Optional, List

class DummyScrapeNavigator(ScrapeNavigator):
    def __init__(self,
        login_sleep_seconds: Optional[int] = None,
        transactions_sleep_seconds: Optional[int] = None,
        benefits_sleep_seconds: Optional[int] = None
    ) -> None:
        self.login_sleep_seconds = login_sleep_seconds
        self.benefits_sleep_seconds = benefits_sleep_seconds
        self.transactions_sleep_seconds = transactions_sleep_seconds

    def login(self) -> None:
        logging.info('Pretending to login!') 
        if self.login_sleep_seconds is not None:
            sleep(self.login_sleep_seconds)
        

    def get_benefits_html_doc(self) -> str:
        logging.info('Pretending to fetch benefits HTML doc!') 
        if self.benefits_sleep_seconds is not None:
            sleep(self.benefits_sleep_seconds) 

        with open('tests/data/benefits.html', 'r') as f:
            html_doc = f.read()
            
        return html_doc



    def get_transaction_html_docs(self, max_workers: int) -> List[str]:
        logging.info('Pretending to fetch transactions!') 
        if self.transactions_sleep_seconds is not None:
            sleep(self.transactions_sleep_seconds) 

        with open('tests/data/transactions.html', 'r') as f:
            html_doc = f.read()

        return [html_doc]
    
    def quit(self) -> None:
        logging.info('Pretending to quit!')