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
from backend.utils.date import fromisoformat
from backend.utils.invoices import get_invoice_number
from backend.utils.banks import process_bank_charges
from backend.dao.invoices import get_all_invoices, update_invoice, create_zoho_invoice, get_unpaid_invoices, get_invoice_by_id
from backend.dao.payments import get_payments_by_invoice_ids
from backend.dao.customers import update_customer
from backend.settings import Config
from backend.database.prisma.connection import prisma

zoho_router = APIRouter()

@zoho_router.get("/zoho/invoices/pay")
async def pay_invoices(request: Request):
    unpaid_invoices = await get_unpaid_invoices()
    payments = await get_payments_by_invoice_ids(
        [invoice.id for invoice in unpaid_invoices]
    )
    access_token = request.headers.get("Authorization")
    payments_created = []

    for payment in payments:
        payment_amount = round(payment.payment_amount, 2)
        payment_method = payment.payment_method
        payment_date = payment.payment_date.strftime("%Y-%m-%d")
        invoice_id = payment.invoice.id
        invoice = await get_invoice_by_id(invoice_id)
        invoice_number = invoice.zohoInvoice.invoice_number
        customer_id = invoice.customer.zohoCustomerId
        bank_charges = process_bank_charges(payment_amount) if payment_method == 'Credit Card' else 0

        # TODO: Implement payment methods to not be hardcoded
        if payment_method == 'Bank Transfer':
            payment_account = await prisma.bankaccount.find_first(
                where={
                    'fresha_account_id': Config.FRESHA_CLIENT_ID,
                    'bank_name': 'Bac Credomatic',
                    'account_type': 'bank'
                }
            )
        elif payment_method == 'Bank Transfer - Bac Credomatic':
            payment_account = await prisma.bankaccount.find_first(
                where={
                    'fresha_account_id': Config.FRESHA_CLIENT_ID,
                    'bank_name': 'Bac Credomatic',
                    'account_type': 'bank'
                }
            )
        elif payment_method == 'Bank Transfer - Banco Promerica':
            payment_account = await prisma.bankaccount.find_first(
                where={
                    'fresha_account_id': Config.FRESHA_CLIENT_ID,
                    'bank_name': 'Banco Promerica',
                    'account_type': 'bank'
                }
            )

        if payment_method == 'Cash':
            payment_account = await prisma.bankaccount.find_first(
                where={
                    'fresha_account_id': Config.FRESHA_CLIENT_ID,
                    'account_type': 'cash'
                }
            )
        if payment_method == 'Credit Card':
            payment_account = await prisma.bankaccount.find_first(
                where={
                    'fresha_account_id': Config.FRESHA_CLIENT_ID,
                    'bank_name': 'Banco Promerica',
                    'account_type': 'bank'
                }
            )

        if not payment_account:
            print(f"Payment account not found for {payment_method}")
            continue

        payment_mode = payment_account.account_type
        account_id = payment_account.id
        print(f"Creating payment for Invoice #{invoice_number} with amount {payment_amount}")

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
                        'invoice_id': invoice.zohoInvoice.id,
                        'amount_applied': payment_amount,
                    }
                ],
                'invoice_id': invoice.zohoInvoice.id,
                'amount_applied': payment_amount,
                'bank_charges': bank_charges,
                'account_id': account_id
            }
        )

        await prisma.invoice.update(
            where={'id': payment.invoice.id},
            data={'status': 'PAID'}
        )

        payments_created.append(new_payment)
    return payments_created


@zoho_router.get("/zoho/invoices")
async def create_invoices_from_dummy(request: Request):
    invoices = await get_all_invoices({
        'where': {'zohoInvoiceId': None},
        'order': {'id': 'asc'}
    })
    access_token = request.headers.get("Authorization")
    zoho_invoices = get_zoho_invoices(access_token, 'draft')['invoices']
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

        await update_customer(invoice.customer.id, {'zohoCustomerId': contact_id})
        invoice_number = get_invoice_number(last_invoice_number)
        items, total_adjustment = get_items(access_token, invoice.items)

        print(f"Creating invoice for {invoice.customer.name} with invoice number {invoice_number}")
        
        new_invoice = create_invoice(
            access_token,
            {
                'customer_id': contact_id,
                'date': invoice.invoiceDate.strftime("%Y-%m-%d"),
                'due_date': invoice.invoiceDate.strftime("%Y-%m-%d"),
                'invoice_number': invoice_number,
                'adjustment': total_adjustment,
                'adjustment_description': 'Descuento' if total_adjustment > 0 else 'Ajuste',
                'line_items': [
                    {
                        'item_id': item['item_id'],
                        'quantity': 1,
                        'discount': item['discount']
                    } for item in items
                ]
            }
        )

        zoho_invoice_data = await create_zoho_invoice(
            {
                'id': new_invoice['invoice_id'],
                'invoice_number': new_invoice['invoice_number'],
                'invoice_url': new_invoice['invoice_url'],
                'status': new_invoice['status'],
                'customer_name': new_invoice['customer_name'],
                'total': new_invoice['total'],
                'tax_total': new_invoice['tax_total'],
                'sub_total': new_invoice['sub_total'],
                'discount': new_invoice['discount'],
                'balance': new_invoice['balance'],
                'date': fromisoformat(new_invoice['date'])
            }
        )

        await update_invoice(
            {
                'id': invoice.id,
                'zohoInvoiceId': zoho_invoice_data.id,
                'status': 'UNPAID'
            }
        )

        last_invoice_number = new_invoice['invoice_number']
        invoices_created.append(new_invoice)

    return invoices_created


@zoho_router.get("/zoho/banks/accounts/sync")
async def sync_bank_accounts(request: Request):
    access_token = request.headers.get("Authorization")

    zoho_bankaccounts = get_bank_accounts(access_token)
    accounts = []
    for account in zoho_bankaccounts:
        try:
            account_synced = await prisma.bankaccount.create(
                data={
                    'id': account['account_id'],
                    'fresha_account_id': Config.FRESHA_CLIENT_ID,
                    'bank_name': account['bank_name'],
                    'account_name': account['account_name'],
                    'account_type': account['account_type'],
                }
            )
            accounts.append(account_synced)
        except Exception as e:
            print(e)
            continue
    
    return accounts