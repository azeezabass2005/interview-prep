from datetime import date, datetime, timedelta


def week_start(at: datetime) -> date:
    """The Monday that starts the competition week containing `at` (UTC)."""
    d = at.date()
    return d - timedelta(days=(d.weekday() + 1) % 7)
