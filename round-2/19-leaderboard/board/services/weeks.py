from datetime import date, datetime, timedelta


def week_start(at: datetime) -> date:
    d = at.date()
    return d - timedelta(days=(d.weekday() + 1) % 7)
