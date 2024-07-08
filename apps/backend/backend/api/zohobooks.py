import requests
import difflib

from typing import List
from prisma.models import Item

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


def create_contact(access_token, contact_data):
    response = requests.post(f'{zoho_api}/contacts', headers={
        'Authorization': f'Bearer {access_token}'
    }, json=contact_data)

    return response.json()

def get_inovoices(access_token):
    invoices = requests.get(f'{zoho_api}/invoices', params=custom_urlencode({
        'organization_id': Config.ZOHO_ORGANIZATION_ID
    }), headers={
        'Authorization': f'Bearer {access_token}'
    })

    return invoices.json()


def get_items(access_token, items: List[Item], discount_applied_on_tax = True):
    items_return = []
    total_adjustment = 0
    for local_item in items:
        query = local_item.serviceName
        params = {
            'name_contains': query,
            'organization_id': Config.ZOHO_ORGANIZATION_ID,
        }

        response = requests.get(f'{zoho_api}/items', params=custom_urlencode(params), headers={
            'Authorization': f'Bearer {access_token}'
        })

        zoho_items = response.json()['items']
        filtered_active_items = [item for item in zoho_items if item['status'] == 'active']

        if not filtered_active_items:
            amount = local_item.price + local_item.manual_discount + local_item.package_discount
            print(f"Item {query} with rate {hn_tax(amount)} not found in Zoho")
            response = requests.post(f'{zoho_api}/items', headers={
                'Authorization': f'Bearer {access_token}'
            }, json={
                'name': query,
                'rate': hn_tax(amount),
                'tax_id': '3093985000000075001',
                'product_type': 'service',
                'item_type': 'sales',
            })
            
            item = response.json()['item']

            filtered_active_items = [item]

        closest_match = difflib.get_close_matches(query, [item['name'] for item in filtered_active_items], n=1, cutoff=0.6)

        if closest_match:
            zoho_item = next(item for item in filtered_active_items if item['name'] == closest_match[0])
            local_discount = local_item.manual_discount + local_item.package_discount
            local_rate = local_item.price + local_discount
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
            print(f"Item {query} not found in Zoho, Price rate not match")
            continue
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

    data = response.json()

    return data['invoice']


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
