from typing import Union
from fastapi import FastAPI, Response, Request
from playwright.sync_api import sync_playwright
import json

from authentication.session import validate_session
from scrapping.fresha import FreshaScrapper
from api.zohobooks import get_contacts
from utils.date import format_date
from utils.invoices import get_invoice_number

app = FastAPI()


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


@app.post("/zoho/invoices")
def create_invoices_from_dummy(request: Request):
    dummy = json.load(open('./dummy/invoices_temp.json'))
    access_token = request.headers.get("Authorization")
    last_invoice_number = request.query_params.get("last_invoice_number")

    for invoice in dummy:
        contact_id = get_contacts(access_token, invoice['Client'])['contacts'][0]['contact_id']
        # date format should be yyyy-mm-dd
        date = format_date(invoice['Sale date'], "%Y-%m-%d")
        due_date = format_date(invoice['Sale date'], "%Y-%m-%d")
        invoice_number = get_invoice_number(last_invoice_number)

    return


@app.get("/fresha/sales")
def list_sales():
    with sync_playwright() as p:
        fresha = FreshaScrapper(p)
        fresha.social_login()
        return {"sales": "list"}