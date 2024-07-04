from prisma.models import Invoice
from typing import List
from backend.database.prisma.connection import prisma

async def get_all_invoices(payment_ids=None):
    return await prisma.invoice.find_many()


async def create_invoice(invoice: Invoice):
    return await prisma.invoice.create(data=invoice)

async def add_invoices(invoices: list[Invoice]):
    try:
        for invoice in invoices:
            customer = await prisma.customer.upsert(
                where={
                    'name': invoice['customer']['name']
                },
                data={
                    'create': invoice['customer'],
                    'update': invoice['customer']
                }
            )
            await prisma.invoice.upsert(
                where={
                    'id': invoice['id']
                },
                data={
                    'create': {
                        'clientName': invoice['clientName'],
                        'invoiceDate': invoice['invoiceDate'],
                        'id': invoice['id'],
                        'items': invoice['items'],
                        'customerId': customer.id
                    },
                    'update': {
                        'id': invoice['id']
                    }
                }
            )
        await prisma.disconnect()
    except Exception as e:
        print(f"Error adding/updating invoices: {str(e)}")
        await prisma.disconnect()
        raise