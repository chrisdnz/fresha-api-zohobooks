PROMERICA_FEE = 0.036

def process_bank_charges(amount):
    return round(amount * PROMERICA_FEE, 2)