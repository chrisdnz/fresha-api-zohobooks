import asyncio

from backend.scrapping.fresha import FreshaScrapper
from backend.dao.invoices import add_invoices
from backend.dao.payments import add_payments
from backend.database.prisma.connection import connect_db, disconnect_db

async def scrape_transactions(params: dict):
    try:
        time_filter = params.get('time_filter', '')
        db_connection = params.get('db_connection', False)
        if db_connection:
            await connect_db()
            print("Connected to database")
        scraper = FreshaScrapper()
        await scraper.initialize()
        await scraper.authenticate()
        transactions = await scraper.get_payment_transactions(time_filter)
        await add_payments(transactions)
    except Exception as e:
        print(e)
        return f"Error scraping sales: {str(e)}"
    finally:
        if scraper:
            await scraper.close()
        if db_connection:
            await disconnect_db()


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
        await add_invoices(sales_log_details)

        await scrape_transactions(params)
    except Exception as e:
        print(e)
        raise e
    finally:
        if scraper:
            await scraper.close()
        if db_connection:
            await disconnect_db()


def scrape_sales():
    return asyncio.run(async_task_sales_logs())