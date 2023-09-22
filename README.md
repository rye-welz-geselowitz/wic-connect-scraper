# Running locally
### Create virtualenv
python3 -m venv scraper-venv

### Activate virtualenv
source scraper-venv/bin/activate

### Install requirements
pip install -r requirements.txt 

### Run script
python -m main

### Run server locally
PASSSWORD=some_password flask run

### Sample curl request
curl -X GET http://127.0.0.1:5000/benefits  -H "Content-Type: application/json" --data-raw '{"username": "test_username", "password": "test_password"}' -u "brl_fellow:some_password"

curl -X GET http://127.0.0.1:5000/transactions  -H "Content-Type: application/json" --data-raw '{"username": "test_username", "password": "test_password"}' -u "brl_fellow:some_password"
