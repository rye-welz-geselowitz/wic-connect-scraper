from flask import Flask, request, render_template 
from werkzeug.security import generate_password_hash, check_password_hash
from scraper import scrape_benefits, LoginException, ScrapingException, scrape_transactions
import os 
import data_presentation
from endpoint_logging import record_error, record_success
import logging

app = Flask(__name__)

@app.route("/")
def get_index():
    return render_template('index.html')


@app.route("/benefits", methods=['POST'])
def get_benefits():
    for field in ['username', 'password']:
        if field not in request.json:
            return {'error': f'Missing field: {field}'}, 400
    
    username = request.json['username']
    password = request.json['password']
    try:
        benefits = scrape_benefits(
            request.json['username'],
            request.json['password'],
        )
    except LoginException as e:
        record_error(username, '/benefits', f'Login failed: {e.error}', e.html_doc)
        return {'error': 'Failed to login on behalf of user'}, 500 
    except ScrapingException as e:
        record_error(username, '/benefits', e.error, e.html_doc)
        return {'error': 'Screen scraping failed'}, 500
    except Exception as e:
        record_error(username, '/benefits', str(e))
        return {'error': str(e)}
    record_success(username, '/benefits')
    return {'benefits': benefits}, 200


@app.route("/transactions-summary", methods=['POST'])
def get_transactions_summary():
    for field in ['username', 'password']:
        if field not in request.json:
            return {'error': f'Missing field: {field}'}, 400

    username = request.json['username']
    logging.info('Scraping transactions')
    try:
        transactions = scrape_transactions(
            username,
            request.json['password'],
        )
    except LoginException as e:
        record_error(username, '/transactions-summary', f'Login failed: {e.error}', e.html_doc)
        return {'error': 'Failed to login on behalf of user'}, 401 
    except ScrapingException as e:
        record_error(username, '/transactions-summary', e.error, e.html_doc)
        return {'error': 'Screen scraping failed'}, 500
    except Exception as e:
        record_error(username, '/transactions-summary', str(e))
        return {'error': str(e)}

    items = data_presentation.get_transactions_summary(transactions)
    
    record_success(username, '/transactions-summary')
    return {'items': items}