from creds import USERNAME, PASSWORD
from scraper import scrape_benefits, scrape_transactions_concurrently
import os 
from datetime import datetime
import csv

USE_HEADLESS_DRIVER = bool(int(os.environ.get('USE_HEADLESS_DRIVER', 1))) 


def scrape(username, password):
    start_dt = datetime.now()
    
    benefits = scrape_benefits(username, password, USE_HEADLESS_DRIVER)
    with open('benefits.csv', 'w') as csvfile:
        fieldnames = benefits[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for benefit in benefits:
            writer.writerow(benefit)
    
    print(f'Benefits took {datetime.now() - start_dt}')

    start_dt = datetime.now()
    transactions = scrape_transactions_concurrently(username, password, USE_HEADLESS_DRIVER)

    with open('transactions.csv', 'w') as csvfile:
        fieldnames = transactions[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for transaction in transactions:
            writer.writerow(transaction)

    print(f'Transactions took {datetime.now() - start_dt}')




if __name__ == '__main__':
    scrape(USERNAME, PASSWORD)

