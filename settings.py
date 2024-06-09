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