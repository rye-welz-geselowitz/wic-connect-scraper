from creds import USERNAME, PASSWORD
from scraper import scrape_benefits

USE_HEADLESS_DRIVER = True 


def scrape(username, password):
    benefits = scrape_benefits(username, password, USE_HEADLESS_DRIVER)
    for benefit in benefits:
        print(f'\n{benefit["name"]}: Issued {benefit["issued"]} {benefit["unit"]}, remaining {benefit["remaining"]} {benefit["unit"]}')


if __name__ == '__main__':
    scrape(USERNAME, PASSWORD)

