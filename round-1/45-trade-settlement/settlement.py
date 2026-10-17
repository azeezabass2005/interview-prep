from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal


class SettlementError(Exception):
    pass


@dataclass
class Trade:
    trade_id: str
    account: str
    symbol: str
    side: str
    quantity: int
    price: Decimal
    settles_on: date
    cancelled: bool = False


@dataclass
class Instruction:
    account: str
    symbol: str
    quantity: int
    cash: Decimal
    status: str = "PENDING"


class Settlement:
    def __init__(self, holidays=()):
        self.holidays = set(holidays)
        self.trades = {}
        self.failed = []

    def settle_date(self, trade_date):
        d = trade_date + timedelta(days=1)
        while d.weekday() >= 5:
            d += timedelta(days=1)
        return d

    def book(self, trade_id, account, symbol, side, quantity, price, trade_date):
        if trade_id in self.trades or side not in ("BUY", "SELL") or quantity <= 0:
            raise SettlementError("bad trade")
        trade = Trade(trade_id, account, symbol, side, quantity, Decimal(str(price)), self.settle_date(trade_date))
        self.trades[trade_id] = trade
        return trade

    def cancel(self, trade_id):
        self.trades[trade_id].cancelled = True

    def net(self, day):
        netted = {}
        for t in self.trades.values():
            if t.settles_on != day:
                continue
            key = (t.account, t.symbol)
            qty, cash = netted.get(key, (0, Decimal("0")))
            value = t.quantity * t.price
            netted[key] = (qty + t.quantity, cash - value if t.side == "BUY" else cash + value)
        return [Instruction(a, s, q, c) for (a, s), (q, c) in sorted(netted.items())]

    def run(self, day, holdings):
        instructions = self.net(day)
        self.failed = []
        for ins in instructions:
            if ins.quantity < 0 and holdings.get((ins.account, ins.symbol), 0) < -ins.quantity:
                ins.status = "FAILED"
            else:
                ins.status = "SETTLED"
        return instructions

    @staticmethod
    def reconcile(ours, custodian):
        breaks = {}
        for symbol, quantity in ours.items():
            theirs = custodian.get(symbol, 0)
            if quantity != theirs:
                breaks[symbol] = (quantity, theirs)
        return breaks
