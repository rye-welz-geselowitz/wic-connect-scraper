from flask import Flask, request, render_template 
from werkzeug.security import generate_password_hash, check_password_hash
from scraper import scrape_benefits, scrape_transactions, scrape_all
import os 
import data_presentation
import logging
from rq import Queue
from worker import conn
from scrape_records import get_scrape_attempt, create_scrape_attempt
from typing import Tuple, Dict, Any

q = Queue(connection=conn)

app = Flask(__name__)

@app.route("/")
def get_index() -> str:
    return render_template('index.html')

@app.route('/scrape-attempt', methods=['POST'])
def post_scrape_attempt() -> Tuple[Dict[Any, Any], int]:
    if request.json is None:
        return {'error': 'Request must include json'}, 400

    for field in ['username', 'password', 'email']:
        if field not in request.json:
            return {'error': f'Missing field: {field}'}, 400
    username = request.json['username']
    password = request.json['password']
    email = request.json['email']
    scrape_attempt = create_scrape_attempt(email)
    q.enqueue(scrape_all, username, password, scrape_attempt['token'])
    return scrape_attempt, 201


@app.route("/scrape-attempt", methods=['GET'])
def get_scrape_attempt_resource() -> Tuple[Dict[Any, Any], int]:
    for field in ['token']:
        if field not in request.args:
            return {'error': f'Missing field: {field}'}, 400
    
    scrape_attempt = get_scrape_attempt(request.args['token'])
    if scrape_attempt is None:
        return {'result': 'Not found'}, 404
    
    
    scrape_attempt['transactions_summary'] = None
    scrape_attempt['cvb_total'] = None

    transactions = scrape_attempt.get('transactions')
    if transactions:
        scrape_attempt['transactions_summary'] = data_presentation.get_transactions_summary(transactions)
        scrape_attempt['cvb_total'] = data_presentation.get_cvb_total(transactions)
    
    return scrape_attempt, 200