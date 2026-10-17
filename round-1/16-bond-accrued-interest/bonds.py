import calendar
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

CONVENTIONS = ("30/360", "ACT/360")
FREQUENCIES = (1, 2, 4)
CENT = Decimal("0.01")


class BondError(Exception):
    pass


def add_months(d, months):
    month = d.month - 1 + months
    year, month = d.year + month // 12, month % 12 + 1
    return date(year, month, min(d.day, calendar.monthrange(year, month)[1]))


def days_30_360(start, end):
    d1, d2 = start.day, end.day
    if d2 == 31 and d1 >= 30:
        d2 = 30
    return 360 * (end.year - start.year) + 30 * (end.month - start.month) + (d2 - d1)


@dataclass(frozen=True)
class Bond:
    face: Decimal
    rate: Decimal
    frequency: int
    maturity: date
    convention: str

    def __post_init__(self):
        if self.frequency not in FREQUENCIES or self.convention not in CONVENTIONS:
            raise BondError("unsupported bond")

    def coupon_dates(self, start):
        step = 12 // self.frequency
        dates, current = [], self.maturity
        while current > start:
            dates.append(current)
            current = add_months(current, -step)
        dates.append(current)
        return sorted(dates)

    def previous_coupon(self, settle):
        if settle >= self.maturity:
            raise BondError("bond has matured")
        return max(d for d in self.coupon_dates(settle) if d < settle)

    def accrued(self, settle):
        start = self.previous_coupon(settle)
        if self.convention == "30/360":
            days = days_30_360(start, settle)
        else:
            days = (settle - start).days
        basis = 360 if self.convention == "30/360" else 365
        return self.face * self.rate * days / basis


class Desk:
    def __init__(self, holidays=()):
        self.holidays = set(holidays)
        self.trades = {}

    def _business_day(self, d):
        return d.weekday() < 5

    def settlement_date(self, trade_date):
        d, added = trade_date, 0
        while added < 2:
            d += timedelta(days=1)
            if self._business_day(d):
                added += 1
        return d

    def book(self, trade_id, bond, trade_date, quantity, clean_price):
        if trade_id in self.trades or quantity <= 0:
            raise BondError("bad trade")
        settle = self.settlement_date(trade_date)
        principal = (quantity * bond.face * Decimal(str(clean_price)) / 100).quantize(CENT, rounding=ROUND_HALF_UP)
        accrued = (quantity * bond.accrued(settle)).quantize(CENT, rounding=ROUND_HALF_UP)
        trade = {"settle": settle, "principal": principal, "accrued": accrued, "total": principal + accrued}
        self.trades[trade_id] = trade
        return trade
