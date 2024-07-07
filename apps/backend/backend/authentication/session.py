from backend.api.zohobooks import get_inovoices

def validate_session(code):
    response = get_inovoices(code)
    if response['code'] == 0:
        return True
    return False