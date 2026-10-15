from datetime import datetime

from .rates import (
    DAILY_MAX_CENTS,
    EARLY_BIRD_CENTS,
    EARLY_BIRD_END_HOUR,
    EARLY_BIRD_EXIT_BEFORE_HOUR,
    EARLY_BIRD_START_HOUR,
    GRACE_MINUTES,
    HOURLY_CENTS,
    LOST_TICKET_CENTS,
)


def parking_fee(entry: datetime, exit: datetime, *, pass_holder=False, lost_ticket=False) -> int:
    """Charge in cents for one stay."""
    if exit < entry:
        raise ValueError("exit before entry")
    if lost_ticket:
        return LOST_TICKET_CENTS
    if pass_holder and entry.weekday() < 5:
        return 0

    minutes = int((exit - entry).total_seconds() // 60)
    if minutes < GRACE_MINUTES:
        return 0
    if _is_early_bird(entry, exit):
        return EARLY_BIRD_CENTS
    return _hourly_with_cap(minutes)


def _is_early_bird(entry: datetime, exit: datetime) -> bool:
    return (
        EARLY_BIRD_START_HOUR <= entry.hour <= EARLY_BIRD_END_HOUR
        and exit.date() == entry.date()
        and exit.hour <= EARLY_BIRD_EXIT_BEFORE_HOUR
    )


def _hourly_with_cap(minutes: int) -> int:
    hours = -(-minutes // 60)  # started hours
    return min(hours * HOURLY_CENTS, DAILY_MAX_CENTS)
