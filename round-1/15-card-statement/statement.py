from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

APR = {"purchase": Decimal("0.24"), "cash": Decimal("0.30")}
PAYMENT_ORDER = ("cash", "purchase")
CASH_FEE_PCT = Decimal("0.05")
CASH_FEE_MIN = Decimal("10.00")
MIN_PAYMENT = Decimal("25.00")
MIN_PCT = Decimal("0.01")
LATE_FEE = Decimal("30.00")
DUE_DAYS = 25
CENT = Decimal("0.01")
ZERO = Decimal("0.00")


def money(x):
    """Round a value to whole cents, with halves rounded away from zero (e.g. 1.005 -> 1.01)."""
    return Decimal(x).quantize(CENT, rounding=ROUND_HALF_UP)


class CardError(Exception):
    """Raised when a card operation gets invalid input, such as a non-positive amount."""
    pass


class Card:
    """A credit card with separate purchase and cash-advance balances.

    Transactions are only recorded when they happen. They change the balances
    later, when close() replays them day by day for the billing cycle.
    """

    def __init__(self):
        """Start a card with both balances at zero, no recorded events and no statements.

        balances:   current amount owed per bucket ("purchase", "cash"); a negative
                    purchase balance is a credit.
        events:     every recorded transaction as (date, kind, amount), in the order recorded.
        statements: every statement produced by close(), oldest first.
        """
        self.balances = {"purchase": ZERO, "cash": ZERO}
        self.events = []
        self.statements = []

    def _record(self, on, kind, amount):
        """Validate an amount and add the transaction to the event log.

        The amount is converted to Decimal through str() so floats like 0.1 don't
        bring binary rounding errors with them. Raises CardError unless the amount
        is positive. Returns the converted amount.
        """
        amount = Decimal(str(amount))
        if amount <= 0:
            raise CardError("amount must be positive")
        self.events.append((on, kind, amount))
        return amount

    def purchase(self, on, amount):
        """Record a purchase on date `on`. When applied, it adds to the purchase balance."""
        self._record(on, "purchase", amount)

    def refund(self, on, amount):
        """Record a refund on date `on`. When applied, it reduces the purchase balance and may make it a credit."""
        self._record(on, "refund", amount)

    def cash_advance(self, on, amount):
        """Record a cash advance on date `on` and return the fee charged on it.

        Only the advance amount goes into the event log. The fee is calculated again
        in _apply(), where the amount plus the fee is added to the cash balance.
        """
        amount = self._record(on, "cash", amount)
        return money(min(amount * CASH_FEE_PCT, CASH_FEE_MIN))

    def pay(self, on, amount):
        """Record a payment on date `on`. When applied, it is split across the balances by _apply()."""
        self._record(on, "payment", amount)

    def _apply(self, kind, amount):
        """Change the running balances for one recorded event.

        purchase: add to the purchase balance.
        refund:   subtract from the purchase balance.
        cash:     add the advance plus its fee to the cash balance.
        payment:  pay down cash first, then purchases. Each bucket takes no more
                  than what it owes (a credit counts as owing nothing). Anything left
                  over is subtracted from purchases as a credit.
        """
        if kind == "purchase":
            self.balances["purchase"] += amount
        elif kind == "refund":
            self.balances["purchase"] -= amount
        elif kind == "cash":
            self.balances["cash"] += amount + money(max(amount * CASH_FEE_PCT, CASH_FEE_MIN))
        else:
            for bucket in PAYMENT_ORDER:
                take = min(amount, max(self.balances[bucket], ZERO))
                self.balances[bucket] -= take
                amount -= take
            self.balances["purchase"] -= amount

    def close(self, start, end):
        """Close the billing cycle from `start` to `end`, then build and save its statement.

        Steps:
          1. Go through the cycle one day at a time. Apply that day's events, then add
             each bucket's end-of-day balance to a running total. The total divided by
             the number of days is the average daily balance (ADB), so
             total x APR / 365 equals ADB x APR / 365 x days.
          2. Total the payments made on or before the previous statement's due date.
          3. Decide on the grace period: it applies on the first cycle, when the previous
             balance was zero or a credit, or when the previous balance was paid off.
             Grace removes purchase interest only.
          4. Calculate interest for each bucket (a negative total is treated as zero),
             round it to the cent, and add it to that bucket.
          5. If the payments from step 2 didn't cover the previous minimum, add the
             late fee to purchases.
          6. New balance = purchases + cash. Work out the minimum payment from the new
             balance and this cycle's interest. The due date is DUE_DAYS after `end`.

        Returns the statement dict: start, end, purchase_interest, cash_interest,
        late_fee, balance, minimum, due. The same dict is appended to self.statements.
        """
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
        grace = previous is None or previous["balance"] <= 0 or paid_by_due >= previous["balance"]
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
