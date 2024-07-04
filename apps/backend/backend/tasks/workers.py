# TODO: This is just an idea of what a task should look like
import asyncio

from typing import List
# from prisma import Prisma

from rq import get_current_job
from backend.dao.customers import create_customer
from backend.scrapping.fresha import FreshaScrapper
from backend.dao.invoices import create_invoice
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

def scrape_sales():
    async def async_task():
        try:
            print("DB URL", Config.DATABASE_URL)
            # job = get_current_job()
            await connect_db()
            print("Connected to database")
            scraper = FreshaScrapper()
            await scraper.initialize()
            await scraper.authenticate()
            sales_log_details = await scraper.get_sales_log_details()
            await scraper.close()
            
            sales = []

            print("Scraping sales...")
            # for sale in sales_log_details:

            #     # Use .get() method with default values
            #     print(sale)
            #     customer_name = sale.get('Client', '')
            #     sale_no = sale.get('Sale no.', '')
            #     date = sale.get('Sale date')
            #     item_name = sale.get('Item', '')

            #     print("validate data: ", customer_name, sale_no, date, item_name)

            #     if not customer_name and not sale_no and not date and not item_name:
            #         continue

                # print("Creating customer")
                # customer = await create_customer(customer_name) if customer_name else None

                # invoice = None
                # if sale_no:
                #     invoice = Invoice(
                #         id=sale_no,
                #         clientName=customer_name,
                #         invoiceDate=to_datetime(date),
                #         customer=customer
                #     )
                #     await create_invoice(invoice)

                # item = None
                # if item_name and invoice:
                #     item = Item(
                #         serviceName=item_name,
                #         invoiceId=invoice.id
                #     )

            #     # Only append non-None values
            #     sale_data = {}
            #     if customer:
            #         sale_data['customer'] = customer
            #     if invoice:
            #         sale_data['invoice'] = invoice
            #     # if item:
            #     #     sale_data['item'] = item

            #     if sale_data:  # Only append if there's at least one non-None value
            #         sales.append(sale_data)
            
            # print(sales)
        except Exception as e:
            print(e)
            return f"Error scraping sales: {str(e)}"
        finally:
            await disconnect_db()
    return asyncio.run(async_task())