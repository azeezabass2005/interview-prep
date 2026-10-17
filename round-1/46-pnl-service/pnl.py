from collections import defaultdict
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


class PnlError(Exception):
    pass


@dataclass
class Lot:
    quantity: Decimal
    cost_per_share: Decimal


def money(x):
    return x.quantize(CENT, rounding=ROUND_HALF_UP)


class PnlService:
    def __init__(self):
        self.lots = defaultdict(list)
        self.realized = defaultdict(Decimal)

    def held(self, symbol):
        return sum((lot.quantity for lot in self.lots[symbol]), Decimal("0"))

    def buy(self, symbol, quantity, price, commission=0):
        quantity, price, commission = Decimal(str(quantity)), Decimal(str(price)), Decimal(str(commission))
        if quantity <= 0 or price <= 0:
            raise PnlError("bad trade")
        cost = (quantity * price + commission) / quantity
        self.lots[symbol].append(Lot(quantity, cost))

    def sell(self, symbol, quantity, price, commission=0):
        quantity, price, commission = Decimal(str(quantity)), Decimal(str(price)), Decimal(str(commission))
        if quantity <= 0 or price <= 0:
            raise PnlError("bad trade")
        remaining, cost = quantity, Decimal("0")
        lots = self.lots[symbol]
        while remaining > 0 and lots:
            lot = lots[-1]
            take = min(remaining, lot.quantity)
            cost += lot.quantity * lot.cost_per_share
            lot.quantity -= take
            remaining -= take
            if lot.quantity == 0:
                lots.remove(lot)
        pnl = money(quantity * price - cost)
        self.realized[symbol] += pnl
        return pnl

    def split(self, symbol, ratio):
        for lot in self.lots[symbol]:
            lot.quantity *= ratio

    def unrealized(self, symbol, price):
        price = Decimal(str(price))
        return money(sum((lot.quantity * (price - lot.cost_per_share) for lot in self.lots[symbol]), Decimal("0")))

    def position(self, symbol):
        quantity = self.held(symbol)
        cost = sum((lot.quantity * lot.cost_per_share for lot in self.lots[symbol]), Decimal("0"))
        average = money(cost / quantity) if quantity else None
        return {"symbol": symbol, "quantity": quantity, "cost": money(cost), "average_cost": average}

    def report(self, prices):
        rows = []
        for symbol in sorted(set(self.lots) | set(self.realized)):
            if not self.lots[symbol] and not self.realized[symbol]:
                continue
            unrealized = self.unrealized(symbol, prices[symbol]) if self.lots[symbol] else Decimal("0.00")
            realized = self.realized[symbol]
            rows.append({**self.position(symbol), "realized": realized, "unrealized": unrealized,
                         "total": realized + unrealized})
        return rows

    def totals(self, prices):
        rows = self.report(prices)
        return {
            "realized": sum((r["realized"] for r in rows), Decimal("0.00")),
            "unrealized": sum((r["unrealized"] for r in rows), Decimal("0.00")),
        }
