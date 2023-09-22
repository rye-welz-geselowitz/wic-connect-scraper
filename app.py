from flask import Flask, request, render_template 
from werkzeug.security import generate_password_hash, check_password_hash
from scraper import scrape_benefits, LoginException, ScrapingException, scrape_transactions
import os 
import data_presentation

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
    except LoginException:
        return {'error': 'Failed to login on behalf of user'}, 500 
    except ScrapingException as e:
        return {'error': 'Screen scraping failed', 'details': {'error': e.error, 'html_doc': e.html_doc}}, 500
    
    return {'benefits': benefits}, 200


@app.route("/transactions", methods=['POST'])
def get_transactions():
    for field in ['username', 'password']:
        if field not in request.json:
            return {'error': f'Missing field: {field}'}, 400

    try:
        transactions = scrape_transactions(
            request.json['username'],
            request.json['password'],
        )
    except LoginException:
        return {'error': 'Failed to login on behalf of user'}, 401 
    except ScrapingException as e:
        return {'error': 'Screen scraping failed', 'details': {'error': e.error, 'html_doc': e.html_doc}}, 500
    
    return {'transactions': transactions}, 200



@app.route("/transactions-summary", methods=['POST'])
def get_transactions_summary():
    for field in ['username', 'password']:
        if field not in request.json:
            return {'error': f'Missing field: {field}'}, 400

    try:
        transactions = scrape_transactions(
            request.json['username'],
            request.json['password'],
        )
    except LoginException:
        return {'error': 'Failed to login on behalf of user'}, 401 
    except ScrapingException as e:
        return {'error': 'Screen scraping failed', 'details': {'error': e.error, 'html_doc': e.html_doc}}, 500
    
    items = data_presentation.get_transactions_summary(transactions)
        
    return {'items': items}