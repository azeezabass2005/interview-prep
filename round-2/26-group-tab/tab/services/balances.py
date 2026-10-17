from collections import defaultdict
from typing import Dict

from ..errors import ValidationError
from ..store import InMemoryStore
from .groups import GroupService


class BalanceService:
    def __init__(self, store: InMemoryStore, groups: GroupService):
        self._store = store
        self._groups = groups

    def balances(self, group_id: str) -> Dict[str, int]:
        group = self._groups.get(group_id)
        balance = defaultdict(int)
        for member in group.members:
            balance[member] = 0
        for expense in self._store.group_expenses(group_id):
            balance[expense.payer] += expense.amount_cents
            for member, share in expense.shares.items():
                balance[member] -= share
        for payment in self._store.group_payments(group_id):
            balance[payment.sender] -= payment.amount_cents
            balance[payment.receiver] += payment.amount_cents
        return dict(balance)

    def record_payment(self, group_id: str, sender: str, receiver: str, amount_cents: int):
        group = self._groups.get(group_id)
        sender, receiver = sender.lower(), receiver.lower()
        self._groups.require_members(group, sender, receiver)
        if sender == receiver or amount_cents <= 0:
            raise ValidationError("payment must be positive and between two different members")
        return self._store.add_payment(group_id, sender, receiver, amount_cents)
