from datetime import datetime

from ..config import (DAILY_MAX_CENTS, EARLY_BIRD_CENTS, EARLY_BIRD_EXIT_BEFORE_HOUR, EARLY_BIRD_FROM_HOUR,
                      EARLY_BIRD_UNTIL_HOUR, GRACE_MINUTES, HOURLY_CENTS, LOST_TICKET_CENTS, VALIDATION_MINUTES)


def minutes_between(start: datetime, end: datetime) -> int:
    return int((end - start).total_seconds() // 60)


def started_hours(minutes: int) -> int:
    return -(-minutes // 60)


def hourly_charge(minutes: int) -> int:
    return min(started_hours(minutes) * HOURLY_CENTS, DAILY_MAX_CENTS)


def is_early_bird(entry: datetime, exit: datetime) -> bool:
    return (EARLY_BIRD_FROM_HOUR <= entry.hour <= EARLY_BIRD_UNTIL_HOUR
            and exit.date() == entry.date()
            and exit.hour < EARLY_BIRD_EXIT_BEFORE_HOUR)


def charge(entry: datetime, exit: datetime, *, lost: bool = False, validated: bool = False) -> int:
    if exit < entry:
        raise ValueError("exit before entry")
    if lost:
        return LOST_TICKET_CENTS
    minutes = minutes_between(entry, exit)
    if minutes < GRACE_MINUTES:
        return 0
    billable = max(0, minutes - VALIDATION_MINUTES) if validated else minutes
    amount = hourly_charge(billable)
    if is_early_bird(entry, exit):
        amount = min(amount, EARLY_BIRD_CENTS)
    return amount
