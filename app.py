from flask import Flask, request 
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from scraper import scrape_benefits, LoginException, ScrapingException
import os 

auth = HTTPBasicAuth()

app = Flask(__name__)

USERS = {"brl_fellow": generate_password_hash(os.environ.get('PASSWORD'))}

@auth.verify_password
def verify_password(username, password):
    if username in USERS and \
            check_password_hash(USERS.get(username), password):
        return username

@app.route("/benefits", methods=['GET'])
@auth.login_required
def get_benefits():
    for field in ['username', 'password']:
        if field not in request.json:
            return {'error': f'Missing field: {field}'}, 400

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