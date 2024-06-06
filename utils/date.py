from datetime import datetime


def format_date(date, format):
    # Parse the date string into a datetime object
    date_object = datetime.strptime(date, "%Y-%m-%d %I:%M %p")
    # Format the datetime object into the desired format
    return date_object.strftime(format)


def sort_by_date(data):
    for entry in data:
        entry["Date"] = datetime.strptime(entry["Date"], "%Y-%m-%d %I:%M %p")
    sorted_data = sorted(data, key=lambda x: x["Date"])
    for entry in sorted_data:
        entry["Date"] = entry["Date"].strftime("%Y-%m-%d %I:%M %p")
    return sorted_data