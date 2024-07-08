from prisma.models import Invoice
from typing import List
from backend.database.prisma.connection import prisma


async def get_all_invoices(query: dict):
    return await prisma.invoice.find_many(
        include={
            'customer': True,
            'items': True,
            'zohoInvoice': True
        },
        where=query.get('where', {}),
        order=query.get('order', {'id': 'asc'})
    )


async def update_invoice(invoice: dict):
    return await prisma.invoice.update(
        where={'id': invoice['id']},
        data=invoice
    )


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


async def create_zoho_invoice(zoho_invoice):
    data = await prisma.zohoinvoice.create(
        data=zoho_invoice
    )

    return data