from flask import Flask, request 
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from scraper import scrape_benefits
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

    benefits = scrape_benefits(
        request.json['username'],
        request.json['password'],
    )
    return {'benefits': benefits}, 200