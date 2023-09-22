def get_transactions_summary(transactions):
    tx_dict = {}
    for tx in transactions:
        key = (tx['item'], tx['unit']) 
        if key not in tx_dict:
            tx_dict[key] = {
                'item': tx['item'],
                'unit': tx['unit'],
                'quantity': 0,
            }
        tx_dict[key]['quantity'] += tx['quantity']
    
    sorted_items = sorted(
        tx_dict.values(),
        key=lambda tx: tx['quantity'],
        reverse=True
    )
    return sorted_items