# currency.py


def format_currency(amount):
    """Format a number as dollars.

    Examples: 1375 -> '$1,375.00' and -40 -> '-$40.00'.
    """
    sign = "-" if amount < 0 else ""
    return f"{sign}${abs(amount):,.2f}"
