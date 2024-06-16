# We have a format for invoice numbers,
# The format is FACT-000-002-01-0000000
# The last 7 digits are the invoice number and they should be unique and incremental.
def get_invoice_number(last_invoice_number):
    # Split the last invoice number into parts
    parts = last_invoice_number.split("-")
    # Get the last part and increment it by 1
    last_part = int(parts[-1]) + 1
    # Format the last part to have 7 digits
    new_last_part = str(last_part).zfill(7)
    # Join the parts back together
    new_invoice_number = "-".join(parts[:-1] + [new_last_part])
    return new_invoice_number
