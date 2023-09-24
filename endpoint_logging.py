

from sqlalchemy import create_engine
from sqlalchemy import URL, text
import os 

DATABASE_URL = os.environ['DATABASE_URL']

engine = create_engine(DATABASE_URL)
conn = engine.connect()

SUCCESS_INSERT = """BEGIN;
INSERT INTO endpoint_logs (username, endpoint, status, html_doc) VALUES (:username, :endpoint, 'SUCCESS', :html_doc);
COMMIT;"""

ERROR_INSERT = """
BEGIN;
INSERT INTO endpoint_logs (username, endpoint, status, error_desc, html_doc) VALUES (:username, :endpoint, 'ERROR', :error_desc, :html_doc);
COMMIT;"""

def record_success(username, endpoint, html_doc=None):
    insert_statement =  text(SUCCESS_INSERT)
    conn.execute(insert_statement, {'endpoint': endpoint, 'html_doc': html_doc, 'username': username})

def record_error(username, endpoint, error, html_doc=None):
    insert_statement =  text(ERROR_INSERT)
    conn.execute(insert_statement, {'endpoint': endpoint, 'error_desc': error, 'html_doc': html_doc, 'username': username})




