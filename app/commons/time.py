from datetime import datetime


def now(as_str=False):
    now = datetime.utcnow()
    if as_str:
        return now.strftime("%B %d, %Y %H:%M:%S")
    return now
