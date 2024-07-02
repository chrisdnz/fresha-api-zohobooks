from bs4 import BeautifulSoup
import re

def extract_data_reports_table(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Get table headers
    headers = [th.text.strip() for th in soup.find('thead').find_all('th')]

    # Get table data rows
    data_rows = soup.find('tbody').find_all('tr')
    data = []
    for row in data_rows:
        cells = [cell.text.strip() for cell in row.find_all('td')]
        
        row_dict = {}
        for header, cell in zip(headers, cells):
            if cell == "":
                continue
            if header == "Payment no." or header == "Sale no.":
                # Convert to integer
                row_dict[header] = int(re.sub(r'\D', '', cell))
            elif header == "Payment amount" or header == "Gross sales" or header == "Net sales" or header == "Total sales" or header == "Item discounts" or header == "Cart discounts" or header == "Total discounts" or header == "Refunds" or header == "Taxes on net sales":
                # Convert to float
                row_dict[header] = float(re.sub(r'[^\d.]', '', cell))
            else:
                # Keep as string
                row_dict[header] = cell

        data.append(row_dict)

    return data
