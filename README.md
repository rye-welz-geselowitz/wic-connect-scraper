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
flask run

### Sample curl request
curl -X POST http://127.0.0.1:5000/benefits  -H "Content-Type: application/json" --data-raw '{"username": "test_username", "password": "test_password"}'

curl -X POST http://127.0.0.1:5000/transactions  -H "Content-Type: application/json" --data-raw '{"username": "test_username", "password": "test_password"}'

curl -X POST http://127.0.0.1:5000/scrape  -H "Content-Type: application/json" --data-raw '{"username": "brl", "password": "bananas"}'


curl -X GET 'http://127.0.0.1:5000/scrape-attempt?token=4b14c7aa-37d0-4495-8101-d7b3b70b9a1c'


# TODO: finish notes on redis local setup:
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES