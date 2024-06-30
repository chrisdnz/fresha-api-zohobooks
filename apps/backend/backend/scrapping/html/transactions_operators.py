from bs4 import BeautifulSoup
import re

def extract_payment_transactions(html):
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
            if header == "Payment no." or header == "Sale no.":
                # Convert to integer
                row_dict[header] = int(re.sub(r'\D', '', cell))
            elif header == "Payment amount":
                # Convert to float
                row_dict[header] = float(re.sub(r'[^\d.]', '', cell))
            else:
                # Keep as string
                row_dict[header] = cell

        data.append(row_dict)

    return data
