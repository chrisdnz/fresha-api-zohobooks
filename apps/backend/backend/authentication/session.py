import requests

from settings import Config

zoho_api = 'https://accounts.zoho.com/oauth/v2/token'

def validate_session(code):
    auth_response = requests.post(zoho_api, params={
        'code': code,
        'client_id': Config.ZOHO_CLIENT_ID,
        'client_secret': Config.ZOHO_CLIENT_SECRET,
        'grant_type': 'authorization_code'
    })
    if auth_response.status_code == 200:
        refresh_token = auth_response.json()
        print(refresh_token)
        access_token = requests.post(zoho_api, params={
            'refresh_token': refresh_token['refresh_token'],
            'client_id': Config.ZOHO_CLIENT_ID,
            'client_secret': Config.ZOHO_CLIENT_SECRET,
            'grant_type': 'refresh_token'
        })

        if access_token.status_code == 200:
            return access_token.json()
        else:
            return None
    else:
        return None