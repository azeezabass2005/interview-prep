from datetime import date
from decimal import Decimal

from ..config import BOOK_GRACE_DAYS, DAILY_FINE, MAX_FINE
from ..models import Branch, Loan
from .calendar import open_days_after


def fine_for(loan: Loan, branch: Branch, returned_on: date) -> Decimal:
    days = open_days_after(branch, loan.due_on, returned_on)
    if loan.kind == "BOOK":
        days = max(0, days - BOOK_GRACE_DAYS)
    return min(days * DAILY_FINE[loan.kind], MAX_FINE[loan.kind])
