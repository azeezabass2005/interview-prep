from datetime import datetime
from decimal import Decimal

from .pricing import Quote, cents
from .rates import FULL_REFUND_HOURS, PARTIAL_REFUND_HOURS, TAX_RATE


def refund(q: Quote, cancelled_at: datetime) -> Decimal:
    check_in = datetime(q.check_in.year, q.check_in.month, q.check_in.day)
    hours_before = (check_in - cancelled_at).total_seconds() / 3600
    if hours_before >= FULL_REFUND_HOURS:
        return q.total
    if hours_before >= PARTIAL_REFUND_HOURS:
        first_night = q.nightly[0]
        return q.total - first_night - cents(first_night * TAX_RATE)
    return Decimal("0.00")
