from typing import Union
from fastapi import FastAPI, Response, Request
from playwright.sync_api import sync_playwright
import json

from authentication.session import validate_session
from scrapping.fresha import FreshaScrapper
from api.zohobooks import get_contacts, get_items, create_invoice
from utils.date import format_date, sort_by_date
from utils.invoices import get_invoice_number

app = FastAPI()

@app.middleware("http")
async def verify_authorization(request: Request, call_next):
    access_token = request.headers.get("Authorization")
    if not access_token:
        return Response(status_code=401, content="Authorization header is required")
    response = await call_next(request)
    return response


@app.exception_handler(Exception)
async def error_handler(request: Request, exc: Union[Exception, str]):
    if isinstance(exc, Exception):
        return Response(status_code=500, content=str(exc))
    else:
        return Response(status_code=400, content=exc)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/access_token")
def get_access_token(request: Request):
    code = request.headers.get("Authorization-Code")
    access_token = validate_session(code)

    return access_token


@app.get("/zoho/contacts")
def list_contacts(request: Request):
    dummy = json.load(open('./dummy/invoices_temp.json'))
    access_token = request.headers.get("Authorization")

    # iterate dummy contacts and find the contact from zoho api
    for contact in dummy:
        zoho_contact = get_contacts(access_token, contact['Client'])
        contact['zoho'] = zoho_contact

    return dummy


@app.get("/zoho/invoices")
def create_invoices_from_dummy(request: Request):
    dummy = json.load(open('./dummy/invoices_temp.json'))
    access_token = request.headers.get("Authorization")
    last_invoice_number = request.query_params.get("last_invoice_number")

    invoices_created = []
    if not last_invoice_number:
        return Response(status_code=400, content="last_invoice_number is required")
    
    # dummy sort by date
    dummy = sort_by_date(dummy)

    for invoice in dummy:
        contact_id = get_contacts(access_token, invoice['Client'])['contacts'][0]['contact_id']
        date = format_date(invoice['Date'], "%Y-%m-%d")
        due_date = format_date(invoice['Date'], "%Y-%m-%d")
        invoice_number = get_invoice_number(last_invoice_number)
        items, total_adjustment = get_items(access_token, invoice['Items'])

        print(f"Creating invoice for {invoice['Client']} with invoice number {invoice_number}")

        new_invoice = create_invoice(
            access_token,
            {
                'customer_id': contact_id,
                'date': date,
                'due_date': due_date,
                'invoice_number': invoice_number,
                'adjustment': total_adjustment,
                'adjustment_description': 'Descuento' if total_adjustment > 0 else 'Ajuste',
                'line_items': [
                    {
                        'item_id': item['item_id'],
                        'rate': item['rate'],
                        'quantity': 1,
                        'discount': item['discount']
                    } for item in items
                ]
            }
        )

        last_invoice_number = new_invoice['invoice_number']
        invoices_created.append(new_invoice)

    return invoices_created


@app.get("/fresha/sales")
def list_sales():
    with sync_playwright() as p:
        fresha = FreshaScrapper(p)
        fresha.social_login()
        return {"sales": "list"}
