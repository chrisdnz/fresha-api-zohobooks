import logging
import os
import json

from playwright.async_api import async_playwright
from backend.settings import Config
from .html.transactions_operators import extract_data_reports_table, extract_invoice_details

class FreshaScrapper:
    site_url = 'https://partners.fresha.com'
    user_email = Config.FRESHA_ACCOUNT_EMAIL
    user_password = Config.FRESHA_ACCOUNT_PASSWORD
    session_path = None
    auth_exists = False

    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None

    async def initialize(self):
        logging.info('Initialization - start')
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False)
        await self.restore_session()
        self.page = await self.context.new_page()
        await self.page.goto(f"{self.site_url}/users/sign-in")
        await self.page.wait_for_load_state("networkidle")
        logging.info('Initialization - end')

    async def authenticate(self):
        logging.info('Log in with Email - start')
        # Check if the user is already logged in
        if self.page.url.find('sign-in') != -1:
            logging.info('Logging in')
            await self.page.get_by_placeholder("Enter your email address").fill(self.user_email)
            await self.page.get_by_label("Continue").click()
            await self.page.get_by_placeholder("Enter a password").fill(self.user_password)
            await self.page.get_by_label("Log in").click()

            await self.page.wait_for_url(f"{self.site_url}/calendar")
            logging.info('Logged in successfully')
            await self.save_session()
        else:
            logging.info('Already logged in')
        logging.info('Log in with Email - end')

    async def get_payment_transactions(self):
        logging.info('Get payment transactions - start')
        await self.page.goto(f"{self.site_url}/reports/table/payment-transactions")
        await self.page.wait_for_load_state("networkidle")

        page_content = await self.page.content()

        transactions = extract_data_reports_table(page_content)
        logging.info('Get payment transactions - end')
        return transactions
    
    async def get_sales_log_details(self):
        logging.info('Get sales log details - start')
        await self.page.goto(f"{self.site_url}/reports/table/sales-list")
        await self.page.wait_for_load_state("networkidle")

        page_content = await self.page.content()

        sale_log_details = extract_data_reports_table(page_content)

        # print(sale_log_details)
        sale_details = []
        for sale in sale_log_details:
            sale_no = sale.get('Sale no.', '')
            if not sale_no:
                continue
            matching_links = self.page.locator(f"//a[contains(text(), '{sale_no}')]")

            count = await matching_links.count()
            if count == 0:
                print(f"No links found for Sale no. {sale_no}")
                continue

            for i in range(count):
                link = matching_links.nth(i)
                text_content = await link.text_content()
                if f"{sale_no}" in text_content:
                    await link.click()
                    await self.page.wait_for_selector("[data-qa='invoice-details']", state="visible")
                    invoice_page_details = await self.page.content()
                    invoice_details = extract_invoice_details(invoice_page_details)
                    invoice_details.update(sale)
                    sale_details.append(invoice_details)
        
        logging.info('Get sales log details - end')
        return sale_details

    async def save_session(self):
        logging.info('Save session - start')
        await self.context.storage_state(path=self.session_path)
        logging.info('Save session - end')

    async def restore_session(self):
        logging.info('Restore session - start')
        absdir = os.path.dirname(os.path.abspath(__file__))
        self.session_path = os.path.join(absdir, ".auth", "session.json")
        self.auth_exists = os.path.exists(self.session_path)

        os.makedirs(os.path.dirname(self.session_path), exist_ok=True)

        if not self.auth_exists:
            logging.info('No session found')
            with open(self.session_path, "w") as f:
                json.dump({}, f)

        self.context = await self.browser.new_context(
            storage_state=self.session_path,
            locale="en-US"
        )
        logging.info('Restore session - end')

    async def close(self):
        logging.info('Closing browser')
        await self.browser.close()

