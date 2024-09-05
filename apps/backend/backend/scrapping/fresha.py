import logging
import os
import json
import re
import asyncio
from urllib.parse import urlencode

from typing import List
from playwright.async_api import async_playwright
from backend.settings import Config
from backend.utils.constants import INVOICE_STATUS
from .html.transactions_operators import extract_data_reports_table, extract_invoice_details
from .html.data_report_extractor import DataReportExtractor

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
        self.browser = await playwright.chromium.launch(headless=True)
        # TODO: This is still not working
        # self.browser = await playwright.chromium.connect_over_cdp(Config.BROWSER_PLAYWRIGHT_ENDPOINT)
        await self.restore_session()
        self.page = await self.context.new_page()
        await self.page.goto(f"{self.site_url}/users/sign-in")
        try:
            await self.page.wait_for_selector("[data-qa='header-avatar']", state="visible")
            
            # click cookies button, data-qa="cookie-accept-btn"
            cookies_button = self.page.locator("[data-qa='cookie-accept-btn']")
            if await cookies_button.count() > 0:
                await cookies_button.click()
            logging.info('Already authenticated')
        except:
            await self.authenticate()
        logging.info('Initialization - end')

    async def authenticate(self):
        logging.info('Log in with Email - start')
        # Wait for any redirects to complete
        await self.page.wait_for_load_state("networkidle")

        # Check the current URL
        current_url = self.page.url
        
        if 'sign-in' in current_url:
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

    async def load_all_data(self):
        while True:
            # Look for the specific span that shows the current number of results
            results_span = self.page.locator("span[data-qa='table-footer-text']")
            if await results_span.count() == 0:
                break  # No more results to load

            results_text = await results_span.inner_text()
            match = re.search(r"Showing (\d+) of (\d+) results", results_text)
            if not match:
                break  # Unexpected format, stop loading

            showing, total = map(int, match.groups())
            if showing == total:
                break  # All results are already loaded

            # Look for the "Load more" link
            load_more_link = self.page.locator("a:has-text('Load') span:has-text('more')")
            if await load_more_link.count() == 0:
                break  # No "Load more" link found

            # Click the "Load more" link
            await load_more_link.click()
            await self.page.wait_for_load_state("networkidle")
            await asyncio.sleep(2)

    async def get_payment_transactions(self, time_filter: str):
        logging.info('Get payment transactions - start')
        await self.page.goto(f"{self.site_url}/reports/table/payment-transactions{'?shortcut=' + time_filter if time_filter else ''}")
        await self.page.wait_for_load_state("networkidle")

        await self.load_all_data()

        page_content = await self.page.content()

        extractor = DataReportExtractor(["Payment date", "Sale date"], ["Payment no.", "Sale no.", "Payment amount"])
        transactions = extractor.extract_data(page_content)
        # transactions = extract_data_reports_table(page_content)
        logging.info('Get payment transactions - end')
        return transactions
    
    async def get_sales_log_details(self, params: dict) -> List[object]:
        logging.info('Get sales log details - start')
        
        query_string = urlencode(params)
        base_url = f"{self.site_url}/reports/table/sales-list"
        full_url = f"{base_url}?{query_string}" if query_string else base_url
        
        await self.page.goto(full_url)
        await self.page.wait_for_load_state("networkidle")
    
        await self.load_all_data()

        page_content = await self.page.content()

        extractor = DataReportExtractor(["Sale date"], ["Sale no.", "Total sales", "Gift card", "Service charges", "Amount due"])
        sale_log_details = extractor.extract_data(page_content)
        filtered_sales = list(filter(lambda sale: sale.get('Sale status', '') == INVOICE_STATUS.get('COMPLETED'), sale_log_details))

        sale_details = []
        # load_morex/_element = self.page.locator("text=Load \\d+ more")
        for sale in filtered_sales:
            sale_no = sale.get('Sale no.', '')
            if not sale_no:
                continue
            matching_links = self.page.locator(f"//a[contains(@href, '/reports/table/sales-list/drawer/invoice/') and contains(text(), '{sale_no}')]")

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
        transformed_sales = []
        for sale in sale_details:
            items = {
                'create': [{
                    'serviceName': item['title'],
                    'price': item['price'],
                    'manual_discount': item['manual_discount'],
                    'package_discount': item['package_discount'],
                } for item in sale['items']]
            }
            transformed_sales.append({
                'invoiceDate': sale['Sale date'],
                'id': sale['Sale no.'],
                'items': items,
                'customer': {
                    "name": sale['Client']
                }
            })
        return transformed_sales

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
            viewport={"width": 1920, "height": 1080},
            locale="en-US"
        )
        logging.info('Restore session - end')

    async def close(self):
        logging.info('Closing browser')
        await self.browser.close()

