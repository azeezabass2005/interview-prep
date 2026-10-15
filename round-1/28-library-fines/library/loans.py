from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from .calendar import LibraryCalendar

LOAN_DAYS = {"BOOK": 21, "DVD": 7, "NEW_RELEASE": 3}
DAILY_FINE = {"BOOK": Decimal("0.25"), "DVD": Decimal("1.00"), "NEW_RELEASE": Decimal("2.00")}
REPLACEMENT_COST = {"BOOK": Decimal("20.00"), "DVD": Decimal("25.00"), "NEW_RELEASE": Decimal("30.00")}
BOOK_GRACE_DAYS = 1
MAX_RENEWALS = 2


class LoanError(Exception):
    pass


@dataclass
class Loan:
    item_type: str
    borrowed_on: date
    due_on: date
    renewals: int = 0


def checkout(item_type: str, on: date, cal: LibraryCalendar) -> Loan:
    if item_type not in LOAN_DAYS:
        raise LoanError(f"unknown item type {item_type}")
    return Loan(item_type, on, on + timedelta(days=LOAN_DAYS[item_type]))


def renew(loan: Loan, today: date, cal: LibraryCalendar) -> None:
    if loan.item_type != "BOOK":
        raise LoanError("only books can be renewed")
    if loan.renewals >= MAX_RENEWALS:
        raise LoanError("renewal limit reached")
    if today > loan.due_on:
        raise LoanError("overdue items cannot be renewed")
    loan.due_on = cal.next_open(today + timedelta(days=LOAN_DAYS[loan.item_type]))
    loan.renewals += 1


def fine_for(loan: Loan, returned_on: date, cal: LibraryCalendar) -> Decimal:
    days_late = cal.open_days_after(loan.due_on, returned_on)
    if loan.item_type == "BOOK":
        days_late = max(0, days_late - BOOK_GRACE_DAYS)
    return days_late * DAILY_FINE[loan.item_type]
