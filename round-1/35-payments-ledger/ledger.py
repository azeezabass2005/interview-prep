import itertools
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

FEE_THRESHOLD = Decimal("1000")
FEE_RATE = Decimal("0.0005")
MIN_FEE = Decimal("1.00")
CENT = Decimal("0.01")
SYSTEM = ("WORLD", "FEES")


class LedgerError(Exception):
    pass


@dataclass
class Transfer:
    transfer_id: int
    sender: str
    receiver: str
    amount: Decimal
    fee: Decimal
    reversed: bool = False


class Ledger:
    def __init__(self):
        self.currencies = {"WORLD": None, "FEES": None}
        self.entries = []
        self.transfers = {}
        self.by_key = {}
        self.holds = {}
        self._ids = itertools.count(1)

    def open(self, account, currency):
        self.currencies[account] = currency

    def balance(self, account):
        return sum((amount for acc, amount, _ in self.entries if acc == account), Decimal("0"))

    def available(self, account):
        return self.balance(account) - sum(h["amount"] for h in self.holds.values() if h["account"] == account)

    def _post(self, ref, *legs):
        if sum(amount for _, amount in legs) != 0:
            raise LedgerError("entries must balance")
        for account, amount in legs:
            self.entries.append((account, amount, ref))

    def deposit(self, account, amount):
        self._post("deposit", ("WORLD", -Decimal(str(amount))), (account, Decimal(str(amount))))

    @staticmethod
    def fee_for(amount):
        if amount < FEE_THRESHOLD:
            return Decimal("0.00")
        return (amount * FEE_RATE).quantize(CENT, rounding=ROUND_HALF_UP)

    def transfer(self, key, sender, receiver, amount):
        amount = Decimal(str(amount))
        if amount <= 0 or sender in SYSTEM or receiver in SYSTEM or sender == receiver:
            raise LedgerError("bad transfer")
        if self.currencies.get(sender) != self.currencies.get(receiver) or self.currencies.get(sender) is None:
            raise LedgerError("currency mismatch")
        fee = self.fee_for(amount)
        if self.balance(sender) < amount + fee:
            raise LedgerError("insufficient funds")
        t = Transfer(next(self._ids), sender, receiver, amount, fee)
        self._post(t.transfer_id, (sender, -(amount + fee)), (receiver, amount), ("FEES", fee))
        self.transfers[t.transfer_id] = t
        self.by_key[key] = t.transfer_id
        return t

    def reverse(self, transfer_id):
        t = self.transfers.get(transfer_id)
        if t is None or t.reversed:
            raise LedgerError("cannot reverse")
        t.reversed = True
        self._post(f"rev-{transfer_id}", (t.receiver, -t.amount), (t.sender, t.amount))
        return t

    def hold(self, hold_id, account, amount):
        amount = Decimal(str(amount))
        if self.available(account) < amount:
            raise LedgerError("insufficient funds")
        self.holds[hold_id] = {"account": account, "amount": amount}

    def release(self, hold_id):
        self.holds.pop(hold_id)

    def capture(self, hold_id, key, receiver):
        h = self.holds.pop(hold_id)
        return self.transfer(key, h["account"], receiver, h["amount"])
