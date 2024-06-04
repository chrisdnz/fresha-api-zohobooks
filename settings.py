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

    # Credentials
    GOOGLE_EMAIL = os.getenv('GOOGLE_EMAIL')
    GOOGLE_PASSWORD = os.getenv('GOOGLE_PASSWORD')