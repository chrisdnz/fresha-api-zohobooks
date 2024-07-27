# Environment Variables for the application

import os

# Load the .env file

from dotenv import load_dotenv
load_dotenv()


class Config:
    # Zoho Config
    ZOHO_CLIENT_ID = os.getenv('ZOHO_CLIENT_ID')
    ZOHO_CLIENT_SECRET = os.getenv('ZOHO_CLIENT_SECRET')
    ZOHO_ORGANIZATION_ID = os.getenv('ZOHO_ORGANIZATION_ID')

    # Fresha Config
    FRESHA_CLIENT_ID = os.getenv('FRESHA_CLIENT_ID')

    # Credentials
    FRESHA_ACCOUNT_EMAIL = os.getenv('FRESHA_ACCOUNT_EMAIL')
    FRESHA_ACCOUNT_PASSWORD = os.getenv('FRESHA_ACCOUNT_PASSWORD')

    # Redis Config
    REDIS_URL = os.getenv('REDIS_URL')
    DATABASE_URL = os.getenv('DATABASE_URL')

    # QSTASH Config
    QSTASH_TOKEN = os.getenv('QSTASH_TOKEN')
    QSTASH_CURRENT_SIGNING_KEY = os.getenv('QSTASH_CURRENT_SIGNING_KEY')
    QSTASH_NEXT_SIGNING_KEY = os.getenv('QSTASH_NEXT_SIGNING_KEY')
    SCHEDULE_URL = os.getenv('SCHEDULE_URL')

    # PW
    BROWSER_PLAYWRIGHT_ENDPOINT = os.getenv('BROWSER_PLAYWRIGHT_ENDPOINT')