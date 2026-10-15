from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Account:
    account_id: str
    resident: bool
    drip_enrolled: bool


@dataclass(frozen=True)
class DividendEvent:
    symbol: str
    record_date: date
    pay_date: date
    per_share: Decimal
    reinvest_price: Decimal


@dataclass
class DividendPayment:
    account_id: str
    gross: Decimal
    withholding: Decimal
    fee: Decimal
    cash_paid: Decimal
    shares_bought: Decimal
    residual: Decimal
