from datetime import datetime
from decimal import Decimal
from typing import Optional

from .rates import CANCEL_FEE, CANCEL_FREE_WINDOW_SECONDS


def cancellation_fee(assigned_at: datetime, eta_seconds: int, cancelled_at: datetime,
                     arrived_at: Optional[datetime] = None) -> Decimal:
    """Fee charged to a rider who cancels after a driver has been assigned."""
    waited = (cancelled_at - assigned_at).total_seconds()
    if waited <= CANCEL_FREE_WINDOW_SECONDS:
        return Decimal("0.00")
    return CANCEL_FEE
