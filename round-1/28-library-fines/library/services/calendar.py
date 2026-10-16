from datetime import date, timedelta

from ..models import Branch


def is_open(branch: Branch, d: date) -> bool:
    return d not in branch.holidays


def next_open(branch: Branch, d: date) -> date:
    while not is_open(branch, d):
        d += timedelta(days=1)
    return d


def open_days_after(branch: Branch, start: date, end: date) -> int:
    count, d = 0, start + timedelta(days=1)
    while d <= end:
        if is_open(branch, d):
            count += 1
        d += timedelta(days=1)
    return count
