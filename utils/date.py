from datetime import datetime


def format_date(date, format):
    # Parse the date string into a datetime object
    date_object = datetime.strptime(date, "%d %b %Y, %I:%M%p")
    # Format the datetime object into the desired format
    return date_object.strftime(format)

