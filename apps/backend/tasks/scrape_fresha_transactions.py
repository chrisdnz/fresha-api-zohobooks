# TODO: This is just an idea of what a task should look like

from typing import List

from rq import get_current_job
from backend.scrapping.fresha import FreshaScrapper
from backend.dao.invoices import add_invoices

from prisma.models import Invoice

def parse_transactions_to_invoices(transactions: List[dict]) -> List[Invoice]:
    invoices = []
    for transaction in transactions:
        invoice = Invoice(
            payment_ref=transaction['payment_ref'],
            # Add all other fields from your Invoice model
            # For example:
            # date=transaction['date'],
            # total_amount=transaction['total_amount'],
            # customer_name=transaction['customer_name'],
            # status=transaction['status'],
            # ... other fields ...
        )
        invoices.append(invoice)
    return invoices

async def scrape_transactions():
    job = get_current_job()
    
    scraper = FreshaScrapper()
    await scraper.initialize()
    await scraper.authenticate()
    transactions = await scraper.get_payment_transactions()
    await scraper.close()
    
    invoices = parse_transactions_to_invoices(transactions)
    add_invoices(invoices)
    
    job.meta['num_invoices'] = len(transactions)
    job.save_meta()
    
    return f"Scraped {len(transactions)} invoices"