from bs4 import BeautifulSoup
import re

from backend.utils.date import to_datetime

FLOAT_FIELDS = [
    "Total sales",
    "Gift card",
    "Service charges",
    "Amount due",
    "Gross sales",
    "Item discounts",
    "Total discounts",
    "Net sales",
    "Total sales",
    "Payment amount",
    "Cart discounts",
    "Refunds",
    "Taxes on net sales"
]

DATE_TIME_FIELDS = ["Date", "Time", "Sale date", "Payment date"]

def extract_data_reports_table(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Find the main table and the sales table
    tables = soup.find_all('table')
    table = tables[0]
    table_sales = tables[1]

    # Get table headers for the main table
    headers = [th.text.strip() for th in table.find('thead').find_all('th') if th.text.strip()]

    # Get table data rows for both tables
    data_rows = table.find('tbody').find_all('tr')
    sales_rows = table_sales.find('tbody').find_all('tr')

    data = []
    for main_row, sales_row in zip(data_rows, sales_rows):
        cells = main_row.find_all('td')
        sales_cell = sales_row.find('td')
        
        if len(cells) <= 1:  # Skip rows with only one cell (like the "Total" row)
            continue

        row_dict = {}
        for header, cell in zip(headers, cells):
            cell_text = cell.text.strip()
            
            if cell_text == "":
                continue
            
            if header in DATE_TIME_FIELDS:
                row_dict[header] = to_datetime(cell_text, "%d %b %Y, %I:%M%p")
            elif header in ["Sale no.", "Items sold"]:
                row_dict[header] = int(cell_text) if cell_text.isdigit() else None
            elif header in FLOAT_FIELDS:
                row_dict[header] = float(re.sub(r'[^\d.]', '', cell_text)) if re.sub(r'[^\d.]', '', cell_text) else None
            else:
                row_dict[header] = cell_text

        # Add the data from the sales table
        sales_text = sales_cell.text.strip() if sales_cell else ''
        if sales_text:
            # Assuming the sales data is numeric. Adjust as needed.
            cleaned_sales_text = re.sub(r'[^\d.]', '', sales_text)
            row_dict['Sale no.'] = int(cleaned_sales_text) if cleaned_sales_text else None
        else:
            row_dict['Sale no.'] = None

        data.append(row_dict)

    return data


def extract_invoice_details(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    def extract_amount(text):
        cleaned_text = re.sub(r'[^\d.]', '', text)
        cleaned_text = cleaned_text.replace(',', '.')
        return float(cleaned_text)
    
    def clean_text(text: str):
        print("cleantext", text)
        text = text.replace('・', ' ')
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
        return text.strip()

    invoice_title_element = soup.find_all('p', attrs={'data-qa': 'sale-drawer-sale-title'})
    invoice_text = next((element.text for element in invoice_title_element if 'Invoice' in element.text), None)
    payment_span = soup.find('span', attrs={'data-qa': 'invoice-payment-name'})
    change_span = soup.find('span', attrs={'data-qa': 'change-value'})
    invoice_details = {
        'invoice_number': re.findall(r'\d+', invoice_text), 
        'created_at': to_datetime(soup.find('p', attrs={'data-qa': 'pos-summary-invoice-created-at'}).text.split('・')[0].strip(), "%a %d %b %Y"),
        'items': [],
        'subtotal': extract_amount(soup.find('span', attrs={'data-qa': 'pos-summary-subtotal-price'}).text),
        'total': extract_amount(soup.find('span', attrs={'data-qa': 'pos-summary-total-price'}).text),
        'payment_method': payment_span.find_all('p')[1].text.strip(),
        'payment_date': to_datetime(payment_span.find_next_sibling('span').text.strip(), "%a %d %b %Y at %I:%M%p"),
        'payment_amount': extract_amount(soup.find('span', attrs={'data-qa': 'invoice-payment-price'}).text),
        'change': extract_amount(change_span.text) if change_span else None,
    }

    # Extract item details with price conversion
    for item_container in soup.find_all('div', attrs={'data-qa': lambda value: value and value.startswith('pos-cart-item-container-')}):
        item = {
            'title': clean_text(item_container.find('p', attrs={'data-qa': 'pos-cart-item-title'}).text),
            'description': clean_text(item_container.find('span', attrs={'data-qa': 'pos-cart-item-description'}).text),
            'price': extract_amount(item_container.find('span', attrs={'data-qa': 'pos-cart-item-price'}).text),
        }
        invoice_details['items'].append(item)

    return invoice_details
