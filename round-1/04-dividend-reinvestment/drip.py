from datetime import date
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal

WITHHOLDING = {"US": Decimal("0.00"), "CA": Decimal("0.15"), "GB": Decimal("0.00")}
DEFAULT_WITHHOLDING = Decimal("0.30")
CENT = Decimal("0.01")
SHARE_UNIT = Decimal("0.0001")


class DripError(Exception):
    pass


class DripProcessor:
    def __init__(self):
        self.countries = {}
        self.trades = []
        self.enrolments = {}
        self.payments = []

    def open_account(self, account, country):
        self.countries[account] = country.upper()

    def shares_on(self, account, symbol, on):
        return sum((qty for acc, sym, when, qty in self.trades if acc == account and sym == symbol and when <= on), Decimal("0"))

    def trade(self, account, symbol, on, shares):
        if account not in self.countries:
            raise DripError("unknown account")
        shares = Decimal(str(shares))
        if shares < 0 and self.shares_on(account, symbol, date.max) + shares < 0:
            raise DripError("cannot sell more than held")
        self.trades.append((account, symbol, on, shares))

    def enrol(self, account, symbol, on, enrolled=True):
        self.enrolments.setdefault((account, symbol), []).append((on, enrolled))

    def enrolled_on(self, account, symbol, on):
        history = self.enrolments.get((account, symbol), [])
        return history[-1][1] if history else False

    def _tax_rate(self, account):
        return WITHHOLDING.get(self.countries[account], Decimal("0"))

    def pay_dividend(self, symbol, per_share, record_date, pay_date, price):
        per_share, price = Decimal(str(per_share)), Decimal(str(price))
        results = []
        for account in sorted(self.countries):
            shares = self.shares_on(account, symbol, pay_date)
            if shares <= 0:
                continue
            gross = (shares * per_share).quantize(CENT, rounding=ROUND_DOWN)
            tax = (gross * self._tax_rate(account)).quantize(CENT, rounding=ROUND_HALF_UP)
            net = gross - tax
            if self.enrolled_on(account, symbol, record_date):
                bought = (net / price).quantize(SHARE_UNIT, rounding=ROUND_HALF_UP)
                cash = Decimal("0.00")
                if bought > 0:
                    self.trades.append((account, symbol, pay_date, bought))
            else:
                bought, cash = Decimal("0"), net
            payment = {"account": account, "symbol": symbol, "pay_date": pay_date, "gross": gross, "tax": tax, "net": net,
                       "shares_bought": bought, "cash": cash}
            self.payments.append(payment)
            results.append(payment)
        return results

    def holdings(self, account, on):
        symbols = sorted({sym for acc, sym, _, _ in self.trades if acc == account})
        held = {sym: self.shares_on(account, sym, on) for sym in symbols}
        return {sym: qty for sym, qty in held.items() if qty}

    def tax_summary(self, account, year):
        rows = [p for p in self.payments if p["account"] == account and p["pay_date"].year == year]
        return {
            "gross": sum((p["gross"] for p in rows), Decimal("0.00")),
            "withheld": sum((p["tax"] for p in rows), Decimal("0.00")),
            "reinvested_shares": sum((p["shares_bought"] for p in rows), Decimal("0")),
            "cash": sum((p["cash"] for p in rows), Decimal("0.00")),
        }

    def statement(self, account):
        return [dict(p) for p in self.payments if p["account"] == account]
