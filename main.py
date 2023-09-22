from creds import USERNAME, PASSWORD
from scraper import scrape_benefits, scrape_transactions
import os 
from datetime import datetime
import csv

USE_HEADLESS_DRIVER = bool(int(os.environ.get('USE_HEADLESS_DRIVER', 1))) 


def scrape(username, password):
    # benefits = scrape_benefits(username, password, USE_HEADLESS_DRIVER)
    # for benefit in benefits:
    #     print(f'\n{benefit["name"]}: Issued {benefit["issued"]} {benefit["unit"]}, remaining {benefit["remaining"]} {benefit["unit"]}')

    start_dt = datetime.now()
    transactions = scrape_transactions(username, password, USE_HEADLESS_DRIVER)

    with open('transactions.csv', 'w') as csvfile:
        fieldnames = transactions[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for transaction in transactions:
            writer.writerow(transaction)

    print(f'It took {datetime.now() - start_dt}')




if __name__ == '__main__':
    scrape(USERNAME, PASSWORD)

