from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

LOAN_DAYS = {"BOOK": 21, "DVD": 3}
DAILY_FINE = {"BOOK": Decimal("0.25"), "DVD": Decimal("1.00")}
MAX_FINE = {"BOOK": Decimal("10.00"), "DVD": Decimal("15.00")}
MAX_ITEMS = 5
BLOCK_AT = Decimal("5.00")
MAX_RENEWALS = 2
SUNDAY = 6


class LibraryError(Exception):
    pass


@dataclass
class Loan:
    item: str
    patron: str
    due: date
    renewals: int = 0
    returned: Optional[date] = None


class Library:
    def __init__(self):
        self.items = {}
        self.balances = {}
        self.loans = []
        self.holds = {}
        self.hold_shelf = {}

    def add_item(self, item, kind):
        if kind not in LOAN_DAYS:
            raise LibraryError("unknown item type")
        self.items[item] = kind
        self.holds[item] = []

    def add_patron(self, patron):
        self.balances[patron] = Decimal("0.00")

    def _due(self, start, kind):
        return start + timedelta(days=LOAN_DAYS[kind])

    def _open_loan(self, item):
        return next((l for l in self.loans if l.item == item and l.returned is None), None)

    def checkout(self, patron, item, on):
        if patron not in self.balances or item not in self.items:
            raise LibraryError("unknown patron or item")
        if self._open_loan(item):
            raise LibraryError("item is out")
        if self.hold_shelf.get(item) not in (None, patron):
            raise LibraryError("item is on hold for someone else")
        if self.balances[patron] >= BLOCK_AT:
            raise LibraryError("patron owes fines")
        if sum(1 for l in self.loans if l.patron == patron) >= MAX_ITEMS:
            raise LibraryError("too many items")
        loan = Loan(item, patron, self._due(on, self.items[item]))
        self.hold_shelf.pop(item, None)
        self.loans.append(loan)
        return loan

    def place_hold(self, patron, item):
        if self._open_loan(item) is None:
            raise LibraryError("item is available")
        if patron in self.holds[item]:
            raise LibraryError("already on hold")
        self.holds[item].append(patron)

    def renew(self, item, on):
        loan = self._open_loan(item)
        if loan is None or self.items[item] != "BOOK":
            raise LibraryError("cannot renew")
        if loan.renewals >= MAX_RENEWALS or on > loan.due or self.holds[item]:
            raise LibraryError("renewal not allowed")
        loan.due = self._due(on, "BOOK")
        loan.renewals += 1
        return loan

    def check_in(self, item, on):
        loan = self._open_loan(item)
        if loan is None:
            raise LibraryError("item is not out")
        loan.returned = on
        kind = self.items[item]
        days_late = max(0, (on - loan.due).days)
        fine = days_late * DAILY_FINE[kind]
        self.balances[loan.patron] += fine
        if self.holds[item]:
            self.hold_shelf[item] = self.holds[item].pop()
        return fine
