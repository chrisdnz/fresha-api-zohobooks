### Fresha + Zoho Books Integration

- **Invoices Creation:** Automatically fetches invoices from Fresha and creates them in Zoho Books.
Storing the invoices internal database to avoid duplicates. GET `/api/invoices`
- **Payments Creation:** Automatically fetches payments from Fresha and creates them in Zoho Books. Storing the payments internal database to avoid duplicates. GET `/api/invoices/pay`


### Roadmap
- [] **Payments Bank Accounts Selection:** Allow the user to select the bank account where the payments will be deposited.
- [] **Frontend:** Create a frontend to allow the user to login and interactively manage the integration.
- [] **Cron Jobs:** Create cron jobs to automatically fetch invoices and payments from Fresha.
