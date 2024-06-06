from urllib.parse import urlencode, quote

def custom_urlencode(params):
    # safe characters: +, Ñ, ñ, á, é, í, ó, ú, ü, Á, É, Í, Ó, Ú, Ü
    return urlencode({key: value for key, value in params.items()}, quote_via=quote, safe='')