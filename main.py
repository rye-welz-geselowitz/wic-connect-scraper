from creds import USERNAME, PASSWORD
from scraper import scrape_benefits, scrape_transactions
import os 
from datetime import datetime
import csv
from data_presentation import get_transactions_summary

USE_HEADLESS_DRIVER = bool(int(os.environ.get('USE_HEADLESS_DRIVER', 1))) 
WRITE_CSVS = bool(int(os.environ.get('WRITE_CSVS', 1))) 

def scrape(username, password):
    start_dt = datetime.now()
    benefits = scrape_benefits(username, password, USE_HEADLESS_DRIVER)
    print(f'Benefits took {datetime.now() - start_dt}')

    start_dt = datetime.now()
    transactions = scrape_transactions(username, password, USE_HEADLESS_DRIVER)
    print(f'Transactions took {datetime.now() - start_dt}')

    summary_lines = get_transactions_summary(transactions)

    if WRITE_CSVS:
        with open('benefits.csv', 'w') as csvfile:
            fieldnames = benefits[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for benefit in benefits:
                writer.writerow(benefit)
        with open('transactions.csv', 'w') as csvfile:
            fieldnames = transactions[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for transaction in transactions:
                writer.writerow(transaction)
                
        with open('summary.csv', 'w') as csvfile:
            fieldnames = summary_lines[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for line in summary_lines:
                writer.writerow(line)  

    
    

    print('summary', summary)




if __name__ == '__main__':
    scrape(USERNAME, PASSWORD)

