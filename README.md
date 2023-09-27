# Running locally
### Create virtualenv
python3 -m venv scraper-venv

### Activate virtualenv
source scraper-venv/bin/activate

### Install requirements
pip install -r requirements.txt 

### Run script
python -m main

### Run locally

#### Run server
export DATABASE_URL='your-db-url'
flask run

#### Run redis server
redis-server

#### Run worker
export DATABASE_URL='your-db-url'
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
python worker.py


### Sample curl request
curl -X POST http://127.0.0.1:5000/scrape-attempt  -H "Content-Type: application/json" --data-raw '{"username": "brl", "password": "bananas"}'


curl -X GET 'http://127.0.0.1:5000/scrape-attempt?token=0c419b28-119f-49e6-87ad-9036a4ee67da&username=brl'

## Run mypy
```mypy app.py```