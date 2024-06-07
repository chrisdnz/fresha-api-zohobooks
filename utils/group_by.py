import json
import re
import os
from collections import defaultdict

def group_invoice_data(invoice_data, payment_data):
    grouped_data = {}
    payments_by_sale_no = defaultdict(list)

    # Organize payment data by Sale No.
    for payment in payment_data:
        sale_no = payment['Sale no.']
        payment_details = {
            'Payment date': payment['Payment date'],
            'Payment no.': payment['Payment no.'],
            'Payment method': payment['Payment method'],
            'Payment amount': float(payment['Payment amount'])
        }
        payments_by_sale_no[sale_no].append(payment_details)

    for entry in invoice_data:
        sale_no = entry['Sale no.']
        common_fields = {
            'Date': entry['Date'],
            'Location': entry['Location'],
            'Client': entry['Client']
        }

        # Package handling and aggregation:
        is_package_item = entry.get('Category') in ['Maquillaje', 'Cabello']
        if is_package_item:
            package_key = f"{sale_no}-{entry['Category']}"

            # Find base package name (remove specific service):
            base_package_name = re.sub(r': .+', '', entry['Item'])

            # Create or aggregate package entry:
            if package_key not in grouped_data:
                grouped_data[package_key] = {
                    **common_fields,
                    "Sale no.": sale_no,
                    "Items": [{
                        "Type": "Service",
                        "Item": base_package_name,  # Use base package name
                        "Category": entry['Category'],
                        "Team member": entry['Team member'],
                        "Channel": entry['Channel'],
                        **{
                            k: float(entry[k]) for k in entry.keys() 
                            if k.endswith('sales') or k.endswith('discounts') 
                        }
                    }],
                    "Payments": payments_by_sale_no.get(sale_no, [])
                }
            else:
                existing_package = grouped_data[package_key]["Items"][0]
                for key in ["Gross sales", "Item discounts", "Total discounts", "Net sales", "Total sales"]:
                    # Convert to float, sum, and then back to string
                    existing_package[key] = str(
                        float(existing_package[key]) +
                        float(entry[key])
                    )

        else:  # Non-package item
            item_data = {k: v for k, v in entry.items() if k not in common_fields and k != 'Sale no.'}
            if sale_no not in grouped_data:
                grouped_data[sale_no] = {
                    **common_fields,
                    "Sale no.": sale_no,
                    "Items": [item_data],
                    "Payments": payments_by_sale_no.get(sale_no, [])
                }
            else:
                # Check for consistency in common fields
                for field in common_fields:
                    if grouped_data[sale_no][field] != common_fields[field]:
                        raise ValueError(f"Inconsistent '{field}' for Sale no. {sale_no}")
                grouped_data[sale_no]["Items"].append(item_data)
    
    return list(grouped_data.values())

# Determine the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the paths to the invoice and payment data files
invoice_file_path = os.path.join(script_dir, "../dummy", "invoices_temp.json")
payment_file_path = os.path.join(script_dir, "../dummy", "payments_temp.json")

# Load the data
with open(invoice_file_path, "r") as invoice_file:
    invoice_data = json.load(invoice_file)
with open(payment_file_path, "r") as payment_file:
    payment_data = json.load(payment_file)

result = group_invoice_data(invoice_data, payment_data)

# Define the path to the new output file
output_file_path = os.path.join(script_dir, "../dummy", "grouped_invoices-copy.json")

# Ensure the directory exists
os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

# Write the grouped data to the new output file
with open(output_file_path, "w") as f:
    json.dump(result, f, indent=4)