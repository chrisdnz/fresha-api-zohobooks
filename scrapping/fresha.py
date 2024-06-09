import logging
import os
import json

from playwright.sync_api import Playwright
from settings import Config

class FreshaScrapper:
    site_url = 'https://partners.fresha.com/users/sign-in'
    user_email = Config.FRESHA_ACCOUNT_EMAIL
    user_password = Config.FRESHA_ACCOUNT_PASSWORD
    session_path = None
    auth_exists = False

    def __init__(self, playwright: Playwright):
        logging.info('Initialization - start')
        self.browser = playwright.chromium.launch(headless=False)
        self.restore_session()
        self.page = self.context.new_page()
        self.page.goto(self.site_url)
        self.page.wait_for_load_state("networkidle")

        logging.info('Initialization - end')

    def authenticate(self):
        logging.info('Log in with Email - start')
        # Check if the user is already logged in
        if self.page.url.find('sign-in') != -1:
            logging.info('Logging in')
            self.page.get_by_placeholder("Enter your email address").fill(self.user_email)
            self.page.get_by_label("Continue").click()
            self.page.get_by_placeholder("Enter a password").fill(self.user_password)
            self.page.get_by_label("Log in").click()

            # self.page.wait_for_load_state("networkidle")
            logging.info('Logged in successfully')
            self.save_session()
        else:
            logging.info('Already logged in')

        self.page.wait_for_timeout(30000)
        logging.info('Log in with Email - end')

    def save_session(self):
        logging.info('Save session - start')
        self.context.storage_state(path=self.session_path)
        logging.info('Save session - end')


    def restore_session(self):
        logging.info('Restore session - start')
        absdir = os.path.dirname(os.path.abspath(__file__))
        self.session_path = os.path.join(absdir, ".auth", "session.json")
        self.auth_exists = os.path.exists(self.session_path)

        os.makedirs(os.path.dirname(self.session_path), exist_ok=True)

        if not self.auth_exists:
            logging.info('No session found')
            with open(self.session_path, "w") as f:
                json.dump({}, f)

        self.context = self.browser.new_context(
            storage_state=self.session_path,
            locale="en-US"
        )
        logging.info('Restore session - end')

    def close(self):
        logging.info('Closing browser')
        self.browser.close()