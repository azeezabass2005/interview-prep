from datetime import date

from ..config import MIN_TRANSFER
from ..errors import LoyaltyError, NotFound
from ..models import TRANSFER
from ..store import InMemoryStore
from .ledger import Ledger


class TransferService:
    def __init__(self, store: InMemoryStore, ledger: Ledger):
        self._store = store
        self._ledger = ledger

    def transfer(self, sender: str, receiver: str, miles: int, on: date) -> None:
        for member_id in (sender, receiver):
            if self._store.member(member_id) is None:
                raise NotFound(f"member {member_id}")
        if sender == receiver:
            raise LoyaltyError("cannot transfer to yourself")
        if miles < MIN_TRANSFER:
            raise LoyaltyError(f"minimum transfer is {MIN_TRANSFER} miles")
        self._ledger.spend(sender, miles, on)
        self._store.add_lot(receiver, on, miles, TRANSFER)
        self._store.add_qualifying(receiver, on.year, miles)
