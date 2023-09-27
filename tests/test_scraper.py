
from scraper import _get_benefits_from_html, _get_transactions_from_html

EXPECTED_PARSED_BENEFITS =  [
    {'name': 'CHEESE', 'unit': 'OUNCE', 'issued': 16.0, 'remaining': 16.0},
    {'name': 'EGGS', 'unit': 'DOZEN', 'issued': 1.0, 'remaining': 1.0},
    {'name': 'CEREAL', 'unit': 'OUNCE', 'issued': 36.0, 'remaining': 36.0},
    {'name': 'BEANS PEAS LENTILS PEANUT BUTTER', 'unit': 'CONTAINER', 'issued': 1.0, 'remaining': 1.0},
    {'name': 'WHOLE WHEAT BREAD; TORTILLAS; RICE; PASTA', 'unit': 'OUNCE', 'issued': 32.0, 'remaining': 32.0},
    {'name': 'FRUITS AND VEGETABLES CASH VALUE BENEFIT', 'unit': 'CASH VALUE BENEFIT(CVB)', 'issued': 25.0, 'remaining': 19.53},
    {'name': 'YOGURT WHOLE MILK', 'unit': 'OUNCE', 'issued': 32.0, 'remaining': 32.0},
    {'name': 'MILK LACTOSE FREE WHOLE', 'unit': 'GALLON', 'issued': 3.0, 'remaining': 0.75},
    {'name': 'JUICE 16OZ FROZEN OR 64OZ CONTAINER', 'unit': 'CONTAINER', 'issued': 2.0, 'remaining': 0.0}
]

EXPECTED_PARSED_TRANSACTIONS = [
    {'date': '01/01/2023', 'quantity': 2.0, 'unit': 'CONTAINER', 'item': 'SOME PRODUCT 2PK*4OZ', 'transaction': 'WIC PURCHASE', 'location': 'C-TOWN'},
    {'date': '01/02/2023', 'quantity': 2.0, 'unit': 'CONTAINER', 'item': 'SOME OTHER PRODUCT 2PK*4OZ', 'transaction': 'WIC PURCHASE', 'location': 'C-TOWN'},
    {'date': '01/02/2023', 'quantity': 2.0, 'unit': 'CONTAINER', 'item': 'A THIRD PRODUCT 2PK*4OZ', 'transaction': 'WIC PURCHASE', 'location': 'C-TOWN'},
    {'date': '01/02/2023', 'quantity': 2.0, 'unit': 'CONTAINER', 'item': 'A FOURTH PRODUCT 2PK*4OZ', 'transaction': 'WIC PURCHASE', 'location': 'C-TOWN'},
    {'date': '01/02/2023', 'quantity': 1.0, 'unit': 'CONTAINER', 'item': 'A FIFTH PRODUCT 4OZ', 'transaction': 'WIC PURCHASE', 'location': 'C-TOWN'},
    {'date': '01/02/2023', 'quantity': 2.0, 'unit': 'CONTAINER', 'item': 'SOMETHING ELSE 4OZ', 'transaction': 'WIC PURCHASE', 'location': 'C-TOWN'},
    {'date': '01/02/2023', 'quantity': 2.0, 'unit': 'CONTAINER', 'item': 'YET ANOTHER PRODUCT 4OZ', 'transaction': 'WIC PURCHASE', 'location': 'C-TOWN'},
    {'date': '01/02/2023', 'quantity': 2.0, 'unit': 'CONTAINER', 'item': 'MORE PRODUCT 4OZ', 'transaction': 'WIC PURCHASE', 'location': 'C-TOWN'},
    {'date': '01/08/2023', 'quantity': 0.75, 'unit': 'GALLON', 'item': 'OTHER FOOD 96OZ', 'transaction': 'WIC PURCHASE', 'location': 'C-TOWN'},
    {'date': '01/29/2023', 'quantity': 1.05, 'unit': 'CASH VALUE BENEFIT(CVB)', 'item': 'ANOTHER FOOD', 'transaction': 'WIC PURCHASE', 'location': 'C-TOWN'},
    {'date': '01/29/2023', 'quantity': 4.29, 'unit': 'CASH VALUE BENEFIT(CVB)', 'item': 'A TASTY FOOD 6PK*3.9OZ', 'transaction': 'WIC PURCHASE', 'location': 'C-TOWN'},
    {'date': '01/29/2023', 'quantity': 32.0, 'unit': 'OUNCE', 'item': 'YOGURT 32OZ', 'transaction': 'WIC PURCHASE', 'location': 'C-TOWN'}]

class TestGetBenefitsFromHtml:
    with open('tests/data/benefits.html', 'r') as f:
        html_doc = f.read()
        benefits = _get_benefits_from_html(html_doc) 
    
    assert benefits == EXPECTED_PARSED_BENEFITS

class TestGetTransactionsFromHtml:
    with open('tests/data/transactions.html', 'r') as f:
        html_doc = f.read()
        txs = _get_transactions_from_html(html_doc) 
    
    assert txs == EXPECTED_PARSED_TRANSACTIONS