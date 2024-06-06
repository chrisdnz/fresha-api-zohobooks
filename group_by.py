import json
import re

def group_invoice_data(data):
    grouped_data = {}

    for entry in data:
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
                    }]
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
                    "Items": [item_data]
                }
            else:
                # Check for consistency in common fields
                for field in common_fields:
                    if grouped_data[sale_no][field] != common_fields[field]:
                        raise ValueError(f"Inconsistent '{field}' for Sale no. {sale_no}")
                grouped_data[sale_no]["Items"].append(item_data)
    
    return list(grouped_data.values())

# Load and group the data
data = json.load(open("./dummy/invoices_temp.json"))
result = group_invoice_data(data)

# Write back to file (optional)
with open("./dummy/invoices_temp.json", "w") as f:
    json.dump(result, f, indent=4)
