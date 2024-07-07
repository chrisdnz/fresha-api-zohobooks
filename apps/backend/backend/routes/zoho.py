import json

from fastapi import APIRouter, Response, Request

from backend.api.zohobooks import (
    get_contacts,
    get_items,
    create_invoice,
    create_contact,
    get_bank_accounts,
    create_payment,
    get_inovoices as get_zoho_invoices
)
from backend.utils.date import format_date, sort_by_date, to_datetime
from backend.utils.invoices import get_invoice_number
from backend.utils.banks import process_bank_charges
from backend.dao.invoices import get_all_invoices
from backend.settings import Config
from backend.database.prisma.connection import prisma

zoho_router = APIRouter()

@zoho_router.get("/zoho/invoices/pay")
async def pay_invoices(request: Request):
    dummy = json.load(open('./dummy/grouped_data.json'))
    created_invoices = await prisma.invoice.find_many(where={'status': 'CREATED'}, order={'createdAt': 'asc'})
    access_token = request.headers.get("Authorization")

    payments_created = []

    for invoice in created_invoices:
        dummy_payment = next((payment for payment in dummy if payment['Sale no.'] == invoice.fresha_sale_id), None)
        payment_amount = round(float(dummy_payment['Payments'][0]['Payment amount'] if dummy_payment else 0))
        payment_method = dummy_payment['Payments'][0]['Payment method'] if dummy_payment else ''
        dummy_payment_date = dummy_payment['Payments'][0]['Payment date'] if dummy_payment else ''
        payment_date = format_date(dummy_payment_date, "%Y-%m-%d")
        fresha_payment_id = next((payment['Payments'][0]['Payment no.'] for payment in dummy if payment['Sale no.'] == invoice.fresha_sale_id), None)
        invoice_id = invoice.zoho_invoice_id
        customer_id = invoice.zoho_customer_id
        bank_charges = process_bank_charges(payment_amount) if payment_method == 'Credit Card' else 0

        # TODO: Implement payment methods to not be hardcoded
        if payment_method == 'Bank Transfer':
            payment_account = await prisma.bankaccount.find_first(
                where={
                    'fresha_account_id': Config.FRESHA_CLIENT_ID,
                    'bank_name': 'Bac Credomatic',
                    'account_type': 'Bank Transfer'
                }
            )
        elif payment_method == 'Bank Transfer - Bac Credomatic':
            payment_account = await prisma.bankaccount.find_first(
                where={
                    'fresha_account_id': Config.FRESHA_CLIENT_ID,
                    'bank_name': 'Bac Credomatic',
                    'account_type': 'Bank Transfer'
                }
            )
        elif payment_method == 'Bank Transfer - Banco Promerica':
            payment_account = await prisma.bankaccount.find_first(
                where={
                    'fresha_account_id': Config.FRESHA_CLIENT_ID,
                    'bank_name': 'Banco Promerica',
                    'account_type': 'Bank Transfer'
                }
            )

        if payment_method == 'Cash':
            payment_account = await prisma.bankaccount.find_first(
                where={
                    'fresha_account_id': Config.FRESHA_CLIENT_ID,
                    'account_type': 'Cash'
                }
            )
        if payment_method == 'Credit Card':
            payment_account = await prisma.bankaccount.find_first(
                where={
                    'fresha_account_id': Config.FRESHA_CLIENT_ID,
                    'bank_name': 'Banco Promerica',
                    'account_type': 'Bank Transfer'
                }
            )
        
        if not dummy_payment:
            continue

        if not payment_account:
            print(f"Payment account not found for {payment_method}")
            continue

        payment_mode = payment_account.account_type
        account_id = payment_account.zoho_account_id
        print(f"Creating payment for Invoice #{invoice.invoice_number} with amount {dummy_payment['Payments'][0]['Payment amount']}")

        print(f"""
            Payment details:
              - Payment Account ID: {account_id}
              - Payment amount: {payment_amount}
              - Payment method: {payment_method}
              - Payment date: {payment_date}
              - Payment mode: {payment_mode}
              - Account ID: {account_id}
              - Bank charges: {bank_charges}
              - Invoice ID: {invoice_id}
              - Customer ID: {customer_id}
        """)

        # Create payment
        new_payment = create_payment(
            access_token,
            {
                'customer_id': customer_id,
                'payment_mode': payment_mode,
                'amount': payment_amount,
                'date': payment_date,
                'invoices': [
                    {
                        'invoice_id': invoice_id,
                        'amount_applied': payment_amount,
                    }
                ],
                'invoice_id': invoice_id,
                'amount_applied': payment_amount,
                'bank_charges': bank_charges,
                'account_id': account_id
            }
        )

        await prisma.payment.create(
            data={
                'zoho_payment_id': new_payment['payment_id'],
                'fresha_payment_id': fresha_payment_id,
                'amount': payment_amount,
                'amount_applied': payment_amount,
                'payment_mode': payment_method,
                'date': to_datetime(dummy_payment_date),
                'bank_charges': bank_charges,
                'invoiceId': invoice.id
            }
        )

        await prisma.invoice.update(
            where={'invoice_number': invoice.invoice_number},
            data={'status': 'PAID'}
        )

        payments_created.append(new_payment)
    return payments_created


@zoho_router.get("/zoho/invoices")
async def create_invoices_from_dummy(request: Request):
    invoices = await get_all_invoices()
    dummy = json.load(open('./dummy/grouped_data.json'))
    access_token = request.headers.get("Authorization")
    zoho_invoices = get_zoho_invoices(access_token)['invoices']
    if zoho_invoices:
        last_invoice_number = zoho_invoices[0]['invoice_number']
    else:
        last_invoice_number = None

    invoices_created = []
    if not last_invoice_number:
        return Response(status_code=400, content="last_invoice_number is required")

    for invoice in invoices:
        contact = get_contacts(access_token, invoice.customer.name)
        contact_id = contact['contacts'][0]['contact_id'] if len(contact['contacts']) > 0 else None
        if not contact_id:
            print(f"Contact {invoice.customer.name} not found in Zoho")
            contact = create_contact(access_token, {
                'contact_name': invoice.customer.name,
            })['contact']
            contact_id = contact['contact_id']
        invoice_number = get_invoice_number(last_invoice_number)
        items, total_adjustment = get_items(access_token, invoice.items)

        print(f"Creating invoice for {invoice.customer.name} with invoice number {invoice_number}")

        # await prisma.invoice.create(
        #     data={
        #         'invoice_number': invoice_number,
        #         'zoho_customer_id': contact_id,
        #         'zoho_line_items': [item['item_id'] for item in items if item['item_id'] is not None],
        #         'fresha_sale_id': invoice['Sale no.'],
        #         'fresha_account_id': Config.FRESHA_CLIENT_ID,
        #         'createdAt': invoice.invoiceDate,
        #         'due_date': invoice.invoiceDate,
        #         'adjustment': total_adjustment,
        #         'adjustment_description': 'Descuento' if total_adjustment > 0 else 'Ajuste'
        #     }
        # )
        
        # new_invoice = create_invoice(
        #     access_token,
        #     {
        #         'customer_id': contact_id,
        #         'date': invoice.invoiceDate,
        #         'due_date': invoice.invoiceDate,
        #         'invoice_number': invoice_number,
        #         'adjustment': total_adjustment,
        #         'adjustment_description': 'Descuento' if total_adjustment > 0 else 'Ajuste',
        #         'line_items': [
        #             {
        #                 'item_id': item['item_id'],
        #                 'quantity': 1,
        #                 'discount': item['discount']
        #             } for item in items
        #         ]
        #     }
        # )

        # await prisma.invoice.update(
        #     where={'invoice_number': invoice_number},
        #     data={'zoho_invoice_id': new_invoice['invoice_id']}
        # )

        # last_invoice_number = new_invoice['invoice_number']
        # invoices_created.append(new_invoice)

    return invoices_created


@zoho_router.get("/zoho/banks/accounts/sync")
async def sync_bank_accounts(request: Request):
    access_token = request.headers.get("Authorization")

    zoho_bankaccounts = get_bank_accounts(access_token)
    accounts = []
    for account in zoho_bankaccounts:
        # trycatch for unique constraint
        try:
            account_synced = await prisma.bankaccount.create(
                data={
                    'zoho_account_id': account['account_id'],
                    'fresha_account_id': Config.FRESHA_CLIENT_ID,
                    'bank_name': account['bank_name'],
                    'account_type': account['account_type'],
                }
            )
            accounts.append(account_synced)
        except Exception as e:
            print(e)
            continue
    
    return accounts