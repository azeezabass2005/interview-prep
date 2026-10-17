from datetime import date, timedelta

from ..config import BLOCK_AT, LOAN_DAYS, MAX_ITEMS, MAX_RENEWALS
from ..errors import LibraryError, NotFound, Refused
from ..models import Branch, Item, Loan, Patron
from ..store import InMemoryStore
from .calendar import next_open
from .fines import fine_for


class CirculationService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def add_branch(self, code: str, holidays=()) -> Branch:
        b = Branch(code, set(holidays))
        self._store.branches[code] = b
        return b

    def add_item(self, barcode: str, kind: str, branch: str) -> Item:
        if kind not in LOAN_DAYS or branch not in self._store.branches:
            raise LibraryError("unknown item type or branch")
        item = Item(barcode, kind, branch)
        self._store.items[barcode] = item
        return item

    def add_patron(self, patron_id: str) -> Patron:
        p = Patron(patron_id)
        self._store.patrons[patron_id] = p
        return p

    def _patron(self, patron_id: str) -> Patron:
        p = self._store.patrons.get(patron_id)
        if p is None:
            raise NotFound(patron_id)
        return p

    def _item(self, barcode: str) -> Item:
        item = self._store.items.get(barcode)
        if item is None:
            raise NotFound(barcode)
        return item

    def checkout(self, patron_id: str, barcode: str, on: date) -> Loan:
        patron, item = self._patron(patron_id), self._item(barcode)
        if self._store.open_loan(barcode):
            raise Refused("item is already checked out")
        if item.on_hold_for not in (None, patron_id):
            raise Refused("item is on the hold shelf for another patron")
        if patron.balance > BLOCK_AT:
            raise Refused("outstanding fines")
        if len(self._store.loans_for(patron_id)) >= MAX_ITEMS:
            raise Refused("item limit reached")
        branch = self._store.branches[item.branch]
        loan = Loan(barcode, patron_id, item.branch, item.kind, on, next_open(branch, on + timedelta(days=LOAN_DAYS[item.kind])))
        item.on_hold_for = None
        self._store.loans.append(loan)
        return loan

    def place_hold(self, patron_id: str, barcode: str) -> int:
        self._patron(patron_id)
        item = self._item(barcode)
        if self._store.open_loan(barcode) is None:
            raise Refused("item is on the shelf; just borrow it")
        if patron_id in item.holds:
            raise Refused("already on the hold list")
        item.holds.append(patron_id)
        return len(item.holds)

    def renew(self, barcode: str, today: date) -> Loan:
        loan = self._store.open_loan(barcode)
        if loan is None:
            raise NotFound(barcode)
        if loan.kind != "BOOK":
            raise Refused("only books can be renewed")
        if loan.renewals >= MAX_RENEWALS:
            raise Refused("renewal limit reached")
        if today > loan.due_on:
            raise Refused("overdue items cannot be renewed")
        branch = self._store.branches[loan.branch]
        loan.due_on = next_open(branch, today + timedelta(days=LOAN_DAYS[loan.kind]))
        loan.renewals += 1
        return loan

    def check_in(self, barcode: str, on: date) -> Loan:
        loan = self._store.open_loan(barcode)
        if loan is None:
            raise NotFound(barcode)
        loan.returned_on = on
        loan.fine = fine_for(loan, self._store.branches[loan.branch], on)
        self._patron(loan.patron).balance += loan.fine
        item = self._item(barcode)
        if item.holds:
            item.on_hold_for = item.holds.popleft()
        return loan
