import datetime


def format_date(date_string: str) -> datetime.datetime:
    return datetime.datetime.strptime(date_string.split('-04:00')[0].split('-05:00')[0], "%Y-%m-%dT%H:%M:%S")
