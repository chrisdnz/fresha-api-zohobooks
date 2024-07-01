from prisma.models import Invoice
from typing import List
from backend.database.prisma.connection import prisma

async def get_all_invoices(payment_ids=None):
    return await prisma.invoice.find_many(
        where={'payment_id': {'in': payment_ids}} if payment_ids else None
    )


async def add_invoices(invoices: list[Invoice]):
    added_invoices = []
    updated_invoices = []

    try:
        for invoice in invoices:
            # Assuming 'transaction_id' is the unique identifier for invoices
            result = await prisma.invoice.upsert(
                where={
                    'payment_ref': invoice['payment_ref']
                },
                data={
                    'create': invoice,
                    'update': invoice
                }
            )
            
            if result.created:
                added_invoices.append(invoice['transaction_id'])
            else:
                updated_invoices.append(invoice['transaction_id'])

        await prisma.disconnect()

        return {
            'added': added_invoices,
            'updated': updated_invoices
        }
    except Exception as e:
        print(f"Error adding/updating invoices: {str(e)}")
        await prisma.disconnect()
        raise