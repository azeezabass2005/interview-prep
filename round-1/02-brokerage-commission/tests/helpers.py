from datetime import datetime, timedelta
from decimal import Decimal

from fees.models import Trade

BASE = datetime(2026, 3, 2, 9, 30)


def trade(n, notional="1000", side="BUY", account="ACC1", minutes=None):
    """Trade number n executed n minutes after market open unless minutes is given."""
    offset = n if minutes is None else minutes
    return Trade(f"T{n}", account, side, Decimal(notional), BASE + timedelta(minutes=offset))
