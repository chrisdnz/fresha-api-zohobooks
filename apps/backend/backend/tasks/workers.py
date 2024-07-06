# TODO: This is just an idea of what a task should look like
import asyncio

from typing import List
# from prisma import Prisma

from rq import get_current_job
from backend.dao.customers import create_customer
from backend.scrapping.fresha import FreshaScrapper
from backend.dao.invoices import add_invoices
from backend.utils.date import to_datetime
from backend.database.prisma.connection import connect_db, disconnect_db
from backend.settings import Config

from prisma.models import Invoice, Payment, Customer, Item

def scrape_transactions():
    async def async_task():
        job = get_current_job()
        
        scraper = FreshaScrapper()
        await scraper.initialize()
        await scraper.authenticate()
        transactions = await scraper.get_payment_transactions()
        print(transactions)
        await scraper.close()
        
        payments = []
        for transaction in transactions:
            payment = Payment()
            print(payment)
    
    return asyncio.run(async_task())


async def async_task_sales_logs(params: dict):
    try:
        time_filter = params.get('time_filter', '')
        db_connection = params.get('db_connection', False)
        if db_connection:
            await connect_db()
            print("Connected to database")
        scraper = FreshaScrapper()
        await scraper.initialize()
        await scraper.authenticate()
        sales_log_details = await scraper.get_sales_log_details(time_filter)
        await scraper.close()
        await add_invoices(sales_log_details)
    except Exception as e:
        print(e)
        return f"Error scraping sales: {str(e)}"
    finally:
        if db_connection:
            await disconnect_db()


def scrape_sales():
    return asyncio.run(async_task_sales_logs())