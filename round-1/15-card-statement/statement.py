from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

APR = {"purchase": Decimal("0.24"), "cash": Decimal("0.30")}
PAYMENT_ORDER = ("purchase", "cash")
CASH_FEE_PCT = Decimal("0.05")
CASH_FEE_MIN = Decimal("10.00")
MIN_PAYMENT = Decimal("25.00")
MIN_PCT = Decimal("0.01")
LATE_FEE = Decimal("30.00")
DUE_DAYS = 25
CENT = Decimal("0.01")
ZERO = Decimal("0.00")


def money(x):
    return Decimal(x).quantize(CENT, rounding=ROUND_HALF_UP)


class CardError(Exception):
    pass


class Card:
    def __init__(self):
        self.balances = {"purchase": ZERO, "cash": ZERO}
        self.events = []
        self.statements = []

    def _record(self, on, kind, amount):
        amount = Decimal(str(amount))
        if amount <= 0:
            raise CardError("amount must be positive")
        self.events.append((on, kind, amount))
        return amount

    def purchase(self, on, amount):
        self._record(on, "purchase", amount)

    def refund(self, on, amount):
        self._record(on, "refund", amount)

    def cash_advance(self, on, amount):
        amount = self._record(on, "cash", amount)
        return money(min(amount * CASH_FEE_PCT, CASH_FEE_MIN))

    def pay(self, on, amount):
        self._record(on, "payment", amount)

    def _apply(self, kind, amount):
        if kind == "purchase":
            self.balances["purchase"] += amount
        elif kind == "refund":
            self.balances["purchase"] -= amount
        elif kind == "cash":
            self.balances["cash"] += amount + money(min(amount * CASH_FEE_PCT, CASH_FEE_MIN))
        else:
            for bucket in PAYMENT_ORDER:
                take = min(amount, max(self.balances[bucket], ZERO))
                self.balances[bucket] -= take
                amount -= take
            self.balances["purchase"] -= amount

    def close(self, start, end):
        previous = self.statements[-1] if self.statements else None
        daily_sum = {"purchase": ZERO, "cash": ZERO}
        for offset in range((end - start).days):
            day = start + timedelta(days=offset)
            for on, kind, amount in self.events:
                if on == day:
                    self._apply(kind, amount)
            for bucket in daily_sum:
                daily_sum[bucket] += self.balances[bucket]
        paid_by_due = sum((a for on, k, a in self.events if k == "payment" and previous and on <= previous["due"]), ZERO)
        grace = previous is None or previous["balance"] <= 0 or paid_by_due > previous["balance"]
        interest = {}
        for bucket, total in daily_sum.items():
            if bucket == "purchase" and grace:
                interest[bucket] = ZERO
            else:
                interest[bucket] = money(max(total, ZERO) * APR[bucket] / 365)
            self.balances[bucket] += interest[bucket]
        late_fee = ZERO
        if previous and previous["minimum"] > 0 and paid_by_due < previous["minimum"]:
            late_fee = LATE_FEE
            self.balances["purchase"] += late_fee
        balance = self.balances["purchase"] + self.balances["cash"]
        charged = interest["purchase"] + interest["cash"]
        if balance <= 0:
            minimum = ZERO
        elif balance < MIN_PAYMENT:
            minimum = MIN_PAYMENT
        else:
            minimum = max(MIN_PAYMENT, money(balance * MIN_PCT + charged))
        statement = {"start": start, "end": end, "purchase_interest": interest["purchase"], "cash_interest": interest["cash"],
                     "late_fee": late_fee, "balance": balance, "minimum": minimum, "due": end + timedelta(days=DUE_DAYS)}
        self.statements.append(statement)
        return statement
