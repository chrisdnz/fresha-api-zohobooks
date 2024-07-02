import requests

from backend.settings import Config
from backend.utils.tax import hn_tax
from backend.utils.url import custom_urlencode

zoho_api = 'https://www.zohoapis.com/books/v3'

def get_contacts(access_token, contact_name_contains: str = None):
    name = 'Walk-Inn' if contact_name_contains == 'Sin cita' else contact_name_contains
    contact = requests.get(f'{zoho_api}/contacts', params=custom_urlencode({
        'contact_name_contains': name,
        'organization_id': Config.ZOHO_ORGANIZATION_ID
    }), headers={
        'Authorization': f'Bearer {access_token}'
    })

    return contact.json()


def get_items(access_token, items, discount_applied_on_tax = True):
    items_return = []
    total_adjustment = 0
    for local_item in items:
        params = {
            'name_contains': local_item['Item'],
            'organization_id': Config.ZOHO_ORGANIZATION_ID
        }

        response = requests.get(f'{zoho_api}/items', params=custom_urlencode(params), headers={
            'Authorization': f'Bearer {access_token}'
        })

        items = response.json()

        for zoho_item in items['items']:
            local_rate = float(local_item['Gross sales'])
            local_discount = float(local_item['Total discounts'])
            item_discount = 0
            if discount_applied_on_tax:
                item_discount = hn_tax(local_discount)
            else:
                total_adjustment += local_discount
            if abs(hn_tax(local_rate) - zoho_item['rate']) < 0.1:
                items_return.append({
                    **zoho_item,
                    'discount': abs(item_discount),
                })

        if not items_return:
            raise ValueError(f"Item {local_item['Item']} not found in Zoho")
    return items_return, total_adjustment


def create_invoice(access_token, invoice_data):
    response = requests.post(f'{zoho_api}/invoices', headers={
        'Authorization': f'Bearer {access_token}'
    }, json={
        'customer_id': invoice_data['customer_id'],
        'date': invoice_data['date'],
        'due_date': invoice_data['due_date'],
        'invoice_number': invoice_data['invoice_number'],
        'line_items': invoice_data['line_items']
    })

    return response.json()['invoice']


def get_bank_accounts(access_token):
    params = {
        'organization_id': Config.ZOHO_ORGANIZATION_ID
    }
    response = requests.get(f'{zoho_api}/bankaccounts', headers={
        'Authorization': f'Bearer {access_token}'
    }, params=custom_urlencode(params))

    return response.json()['bankaccounts']


def create_payment(access_token, payment_data):
    params = {
        'organization_id': Config.ZOHO_ORGANIZATION_ID
    }
    response = requests.post(f'{zoho_api}/customerpayments', headers={
        'Authorization': f'Bearer {access_token}'
    }, json=payment_data, params=custom_urlencode(params))

    payment = response.json()

    if payment['code'] == 0:
        return response.json()['payment']
        
    raise ValueError(payment['message'])
