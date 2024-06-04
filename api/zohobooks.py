import requests

from settings import Config

zoho_api = 'https://www.zohoapis.com/books/v3'

def get_contacts(access_token, contact_name_contains: str = None):
    contact = requests.get(f'{zoho_api}/contacts', params={
        'contact_name_contains': contact_name_contains,
        'organization_id': Config.ZOHO_ORGANIZATION_ID
    }, headers={
        'Authorization': f'Bearer {access_token}'
    })

    return contact.json()