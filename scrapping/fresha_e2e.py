from scrapping.fresha import FreshaScrapper

from playwright.sync_api import Playwright, sync_playwright, expect


with sync_playwright() as playwright:
    fresha = FreshaScrapper(playwright)

    fresha.authenticate()

    fresha.close()
