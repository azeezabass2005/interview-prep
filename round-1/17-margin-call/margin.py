from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, List, Optional

HAIRCUT = {"EQUITY": Decimal("0.25"), "ETF": Decimal("0.15")}
SHORT_HAIRCUT = Decimal("0.30")
CONCENTRATION = Decimal("0.40")
STALE_AFTER = timedelta(minutes=15)
STALE_ADD = Decimal("0.10")
CALL_UNIT = Decimal("100")


class MarginError(Exception):
    pass


@dataclass
class Account:
    account_id: str
    cash: Decimal
    positions: Dict[str, int] = field(default_factory=dict)
    deposits: List[tuple] = field(default_factory=list)
    call: Optional[dict] = None


class MarginEngine:
    def __init__(self, clock):
        self.clock = clock
        self.asset_class = {}
        self.prices = {}
        self.accounts = {}

    def list_security(self, symbol, asset_class):
        if asset_class not in HAIRCUT:
            raise MarginError("unknown asset class")
        self.asset_class[symbol] = asset_class

    def set_price(self, symbol, price, as_of):
        self.prices[symbol] = (Decimal(str(price)), as_of)

    def open_account(self, account_id, cash=0):
        self.accounts[account_id] = Account(account_id, Decimal(str(cash)))

    def trade(self, account_id, symbol, quantity, price):
        account = self.accounts[account_id]
        if symbol not in self.asset_class:
            raise MarginError("unknown security")
        account.cash -= quantity * Decimal(str(price))
        account.positions[symbol] = account.positions.get(symbol, 0) + quantity

    def deposit(self, account_id, amount):
        account = self.accounts[account_id]
        account.cash += Decimal(str(amount))
        account.deposits.append((self.clock.now(), Decimal(str(amount))))

    def _price(self, symbol):
        if symbol not in self.prices:
            raise MarginError(f"no price for {symbol}")
        return self.prices[symbol]

    def evaluate(self, account_id):
        account = self.accounts[account_id]
        now = self.clock.now()
        equity, requirement = account.cash, Decimal(0)
        gross = sum(abs(q) * self._price(s)[0] for s, q in account.positions.items())
        for symbol, quantity in account.positions.items():
            price, as_of = self._price(symbol)
            value = abs(quantity) * price
            equity += value
            if quantity < 0:
                haircut = SHORT_HAIRCUT
            else:
                haircut = HAIRCUT[self.asset_class[symbol]]
                if gross and value / gross > CONCENTRATION:
                    haircut *= 2
            if now - as_of >= STALE_AFTER:
                haircut += STALE_ADD
            requirement += value * haircut
        excess = equity - requirement
        if excess < 0 and account.call is None:
            units = (-excess / CALL_UNIT).quantize(Decimal(1), rounding=ROUND_HALF_UP)
            account.call = {"amount": units * CALL_UNIT, "issued_at": now}
        return {"equity": equity, "requirement": requirement, "excess": excess, "call": account.call}

    def call_remaining(self, account_id):
        account = self.accounts[account_id]
        if account.call is None:
            return Decimal(0)
        paid = sum(amount for _, amount in account.deposits)
        remaining = max(account.call["amount"] - paid, Decimal(0))
        if remaining == 0:
            account.call = None
        return remaining
