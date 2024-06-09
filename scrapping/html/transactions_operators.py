from bs4 import BeautifulSoup
import json

def extract_payment_transactions(html):
    # Parse the HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Get table headers
    headers = [th.text.strip() for th in soup.find('thead').find_all('th')]

    # Get table data rows
    data_rows = soup.find('tbody').find_all('tr')
    data = []
    for row in data_rows:
        cells = [cell.text.strip() for cell in row.find_all('td')]
        # Extract amount, remove "HNL" and spaces/newlines
        cells[-1] = cells[-1].replace("HNL", "").replace("\xa0", "").strip()  
        data.append(dict(zip(headers, cells)))

    # Convert to JSON
    json_data = json.dumps(data, indent=4)  
    return json_data
