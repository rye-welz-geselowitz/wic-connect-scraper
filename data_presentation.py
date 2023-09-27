from typing import List, Dict, Any

def get_transactions_summary(transactions: List[Dict[Any, Any]]) -> List[Dict[Any, Any]]:
    tx_dict = {}
    for tx in transactions:
        key = (tx['item'], tx['unit']) 
        if key not in tx_dict:
            tx_dict[key] = {
                'item': tx['item'],
                'unit': tx['unit'],
                'times_purchased': 0,
                'quantity': 0
            }
        tx_dict[key]['times_purchased'] += 1
        tx_dict[key]['quantity'] += tx['quantity']
    
    sorted_items = sorted(
        tx_dict.values(),
        key=lambda tx: tx['times_purchased'],
        reverse=True
    )
    return sorted_items

def get_cvb_total(transactions: List[Dict[Any, Any]]) -> float:
    total = 0
    for tx in transactions:
        if 'CASH VALUE BENEFIT' in tx['unit']:
            total += tx['quantity']
    return total
