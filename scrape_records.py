
from sqlalchemy import create_engine
from sqlalchemy import URL, text
import os 
import json 

DATABASE_URL = os.environ['DATABASE_URL'].replace('postgres://', 'postgresql://')

engine = create_engine(DATABASE_URL)
conn = engine.connect()


INSERT_SCRAPE_ATTEMPT = """BEGIN;
INSERT INTO scrape_attempts (username, token, status) VALUES (:username, :token, 'PENDING');
COMMIT;"""

UPDATE_SCRAPE_ATTEMPT = """BEGIN;
UPDATE scrape_attempts 
SET
    status=:status,
    error_desc=:error_desc,
    html_doc=:html_doc,
    benefits=:benefits,
    transactions=:transactions
WHERE token=:token;
COMMIT;"""

def create_scrape_attempt(username, token):
    insert_statement =  text(INSERT_SCRAPE_ATTEMPT)
    conn.execute(insert_statement, {'username': username, 'token': token})

def record_scrape_success(token, benefits, transactions):
    update_statement =  text(UPDATE_SCRAPE_ATTEMPT)
    conn.execute(update_statement, {
        'token': token, 'status': 'SUCCESS', 'error_desc': None,
        'html_doc': None, 'benefits': json.dumps(benefits),
        'transactions': json.dumps(transactions)})

def record_scrape_failure(token, error_category, error_desc, html_doc, benefits, transactions):
    update_statement = text(UPDATE_SCRAPE_ATTEMPT)
    conn.execute(update_statement, {
        'token': token, 'status': f'FAILURE_{error_category}', 'error_desc': error_desc,
        'html_doc': html_doc, 'benefits': json.dumps(benefits),
        'transactions': json.dumps(transactions)}) 

