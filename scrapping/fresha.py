import logging

from playwright.sync_api import Playwright
from settings import Config

class FreshaScrapper:
    site_url = 'https://partners.fresha.com'
    google_email = Config.GOOGLE_EMAIL
    google_password = Config.GOOGLE_PASSWORD

    def __init__(self, playwright: Playwright):
        logging.info('Initialization - start')
        self.browser = playwright.firefox.launch(headless=False)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.page.goto(self.site_url)

        logging.info('Initialization - end')

    def social_login(self):
        logging.info('Social login - start')
        with self.context.expect_page() as new_page_info:
            self.page.locator("button", has_text="Continue with Google").click()

        google_page = new_page_info.value
        google_page.wait_for_load_state()

        try:
            google_page.locator("input[type='email']").fill(self.google_email)
            google_page.locator("div[role='button']").filter(has_text="Next").click()

            google_page.locator("input[type='password']").fill(self.google_password)
            google_page.locator("div[role='button']").filter(has_text="Next").click()

            google_page.wait_for_navigation()

        except TimeoutError as e:
            logging.error(f'Error during google login: {e}')

        logging.info('Log in with Google - end')

    def close(self):
        logging.info('Closing browser')
        self.browser.close()