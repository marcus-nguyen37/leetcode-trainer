from datetime import datetime, timedelta

# Calculate next review date.
def next_review(date_str, confidence):

    # Somewhat arbitrary values for now, just want to model exponential behaviour
    base = 2 + confidence
    days = base**2

    next_date = datetime.fromisoformat(date_str) + timedelta(days=days)
    return next_date.date()
