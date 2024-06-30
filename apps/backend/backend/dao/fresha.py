from scrapping.fresha import FreshaScrapper

async def get_payments():
    scraper = FreshaScrapper()
    await scraper.initialize()
    await scraper.authenticate()
    transactions = await scraper.get_payment_transactions()
    await scraper.close()

    return transactions