from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict

START_CASH = Decimal("100000")
MIN_TRADES = 5
PLACES = Decimal("0.01")


class CompetitionError(Exception):
    pass


@dataclass
class Participant:
    name: str
    joined_at: datetime
    cash: Decimal = START_CASH
    positions: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    trade_prices: Dict[str, Decimal] = field(default_factory=dict)
    trades: int = 0
    disqualified: bool = False


class Leaderboard:
    def __init__(self):
        self.participants = {}
        self.prices = {}

    def join(self, name, at):
        if name in self.participants:
            raise CompetitionError("already joined")
        self.participants[name] = Participant(name, at)

    def set_price(self, symbol, price):
        self.prices[symbol] = Decimal(str(price))

    def trade(self, name, symbol, side, quantity, price):
        p = self.participants[name]
        price = Decimal(str(price))
        if quantity <= 0 or side not in ("BUY", "SELL"):
            raise CompetitionError("bad trade")
        if side == "SELL" and p.positions[symbol] < quantity:
            raise CompetitionError("not enough shares")
        p.positions[symbol] += quantity if side == "BUY" else -quantity
        p.cash += -quantity * price if side == "BUY" else quantity * price
        p.trade_prices[symbol] = price
        p.trades += 1

    def disqualify(self, name):
        self.participants[name].disqualified = True

    def value(self, name):
        p = self.participants[name]
        return p.cash + sum((q * p.trade_prices[s] for s, q in p.positions.items()), Decimal("0"))

    def return_pct(self, name):
        return ((self.value(name) - START_CASH) / START_CASH * 100).quantize(PLACES, rounding=ROUND_HALF_UP)

    def standings(self):
        eligible = [p for p in self.participants.values() if p.trades > MIN_TRADES]
        ordered = sorted(eligible, key=lambda p: (-self.return_pct(p.name), -p.trades, p.joined_at))
        return [(rank, p.name, self.return_pct(p.name)) for rank, p in enumerate(ordered, start=1)]

    def page(self, n, size=10):
        rows = self.standings()
        return rows[n * size:(n + 1) * size]

    def rank_of(self, name):
        for rank, who, _ in self.standings():
            if who == name:
                return rank
        return None

    def summary(self, name):
        p = self.participants[name]
        return {
            "name": name,
            "cash": p.cash,
            "positions": {s: q for s, q in sorted(p.positions.items()) if q},
            "value": self.value(name),
            "return_pct": self.return_pct(name),
            "trades": p.trades,
            "rank": self.rank_of(name),
            "disqualified": p.disqualified,
        }

    def movers(self, previous):
        changes = {}
        for rank, name, _ in self.standings():
            if name in previous:
                changes[name] = previous[name] - rank
        return dict(sorted(changes.items(), key=lambda kv: (-kv[1], kv[0])))
