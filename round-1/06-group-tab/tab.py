from dataclasses import dataclass, field
from decimal import ROUND_DOWN, Decimal
from typing import Dict

CENT = Decimal("0.01")
MODES = ("EQUAL", "EXACT", "PERCENT", "SHARES")


class TabError(Exception):
    pass


@dataclass
class Expense:
    expense_id: int
    payer: str
    amount: Decimal
    shares: Dict[str, Decimal] = field(default_factory=dict)
    deleted: bool = False


@dataclass
class Payment:
    sender: str
    receiver: str
    amount: Decimal


class GroupTab:
    def __init__(self, members):
        self.members = list(members)
        self.expenses = {}
        self.payments = []

    def _check_members(self, *names):
        for name in names:
            if name not in self.members:
                raise TabError(f"{name} is not in the group")

    @staticmethod
    def _with_leftover(amount, raw, order):
        shares = {p: v.quantize(CENT, rounding=ROUND_DOWN) for p, v in raw.items()}
        leftover = int((amount - sum(shares.values())) / CENT)
        for i in range(leftover):
            shares[order[i % len(order)]] += CENT
        return shares

    def _split(self, amount, mode, participants, values):
        if mode == "EQUAL":
            each = (amount / len(participants)).quantize(CENT, rounding=ROUND_DOWN)
            return {p: each for p in participants}
        values = [Decimal(str(v)) for v in values]
        if len(values) != len(participants):
            raise TabError("one value per participant")
        if mode == "EXACT":
            return dict(zip(participants, values))
        if mode == "PERCENT":
            if sum(values) != 100:
                raise TabError("percentages must add up to 100")
            raw = {p: amount * v / 100 for p, v in zip(participants, values)}
        else:
            total = len(participants)
            raw = {p: amount * v / total for p, v in zip(participants, values)}
        return self._with_leftover(amount, raw, participants)

    def add_expense(self, payer, amount, participants, mode="EQUAL", values=()):
        amount = Decimal(str(amount))
        if amount <= 0 or mode not in MODES or not participants:
            raise TabError("bad expense")
        self._check_members(payer, *participants)
        expense = Expense(len(self.expenses) + 1, payer, amount, self._split(amount, mode, list(participants), values))
        self.expenses[expense.expense_id] = expense
        return expense

    def delete_expense(self, expense_id):
        if expense_id not in self.expenses:
            raise TabError("unknown expense")
        self.expenses[expense_id].deleted = True

    def pay(self, sender, receiver, amount):
        self._check_members(sender, receiver)
        self.payments.append(Payment(sender, receiver, Decimal(str(amount))))

    def balances(self):
        balance = {m: Decimal("0.00") for m in self.members}
        for e in self.expenses.values():
            balance[e.payer] += e.amount
            for member, share in e.shares.items():
                balance[member] -= share
        for p in self.payments:
            balance[p.sender] -= p.amount
            balance[p.receiver] += p.amount
        return balance

    def settle_up(self):
        balance = {m: v for m, v in self.balances().items() if v != 0}
        moves = []
        while balance:
            debtor = min(balance, key=lambda m: (balance[m], m))
            creditor = max(balance, key=lambda m: (balance[m], m))
            amount = min(-balance[debtor], balance[creditor])
            moves.append((debtor, creditor, amount))
            for m, delta in ((debtor, amount), (creditor, -amount)):
                balance[m] += delta
                if balance[m] == 0:
                    del balance[m]
        return moves
