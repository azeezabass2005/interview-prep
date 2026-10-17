from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

TIER_KWH = 500
TIER_DAYS = 30
LOW_RATE = Decimal("0.15")
HIGH_RATE = Decimal("0.20")
FIXED = Decimal("10.00")
TRUE_UP_RATE = Decimal("0.05")
ROLLOVER = 100_000
CENT = Decimal("0.01")


class MeterError(Exception):
    pass


@dataclass
class Account:
    customer: str
    last_date: Optional[date] = None
    last_import: int = 0
    last_export: int = 0
    bank: int = 0


def _usage(previous, current):
    return current - previous


class NetMetering:
    def __init__(self):
        self.accounts = {}
        self.bills = []

    def _account(self, customer):
        return self.accounts.setdefault(customer, Account(customer))

    def read(self, customer, on, import_reading, export_reading):
        account = self._account(customer)
        if not (0 <= import_reading < ROLLOVER and 0 <= export_reading < ROLLOVER):
            raise MeterError("bad register value")
        if account.last_date is None:
            account.last_date, account.last_import, account.last_export = on, import_reading, export_reading
            return None
        if on <= account.last_date:
            raise MeterError("readings must move forward in time")
        days = (on - account.last_date).days
        imported = _usage(account.last_import, import_reading)
        exported = _usage(account.last_export, export_reading)
        bill = self._bill(account, days, imported, exported)
        account.last_date, account.last_import, account.last_export = on, import_reading, export_reading
        self.bills.append(bill)
        return bill

    def _bill(self, account, days, imported, exported):
        net = imported - exported
        banked_used = 0
        if net < 0:
            account.bank += exported
            charged = 0
        else:
            banked_used = min(account.bank, net)
            charged = net - banked_used
        threshold = TIER_KWH
        energy = min(charged, threshold) * LOW_RATE + max(charged - threshold, 0) * HIGH_RATE
        energy = energy.quantize(CENT, rounding=ROUND_HALF_UP)
        return {"customer": account.customer, "days": days, "imported": imported, "exported": exported,
                "banked_used": banked_used, "energy": energy, "total": energy + FIXED, "bank": account.bank}

    def true_up(self, customer):
        account = self._account(customer)
        return (account.bank * TRUE_UP_RATE).quantize(CENT, rounding=ROUND_HALF_UP)

    def history(self, customer):
        return [b for b in self.bills if b["customer"] == customer]

    def summary(self, customer):
        bills = self.history(customer)
        return {
            "bills": len(bills),
            "imported": sum(b["imported"] for b in bills),
            "exported": sum(b["exported"] for b in bills),
            "charged": sum((b["total"] for b in bills), Decimal("0.00")),
            "bank": self._account(customer).bank,
        }

    def estimate(self, customer, days):
        bills = self.history(customer)[-3:]
        if not bills:
            raise MeterError("no history to estimate from")
        per_day = sum(b["imported"] - b["exported"] for b in bills) / sum(b["days"] for b in bills)
        return max(0, round(per_day * days))
