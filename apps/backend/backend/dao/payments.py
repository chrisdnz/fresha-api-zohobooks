from prisma.models import Payment

from backend.database.prisma.connection import prisma


async def get_payments_by_invoice_ids(invoice_ids: list[int]):
    return await prisma.payment.find_many(where={'invoiceId': {'in': invoice_ids}}, include={'invoice': True}, order={'payment_date': 'asc'})

async def add_payments(payments: list[Payment]):
    try:
        for payment in payments:
            invoice = await prisma.invoice.find_unique(where={'id': payment['Sale no.']}, include={'customer': True})
            if not invoice:
                print(f"Invoice not found for payment {payment['Payment no.']} with sale no. {payment['Sale no.']}")
                continue
            await prisma.payment.upsert(
                where={'id': payment['Payment no.']},
                data={
                    'create': {
                        'id': payment['Payment no.'],
                        'payment_amount': payment['Payment amount'],
                        'payment_method': payment['Payment method'],
                        'payment_date': payment['Payment date'],
                        'invoiceId': invoice.id,
                    },
                    'update': {
                        'id': payment['Payment no.'],
                    }
                }
            )
    except Exception as e:
        print(f"Error adding payments: {str(e)}")
        await prisma.disconnect()
        raise