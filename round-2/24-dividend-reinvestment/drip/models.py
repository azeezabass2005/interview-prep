from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Account:
    account_id: str
    name: str
    country: str


@dataclass(frozen=True)
class Movement:
    account_id: str
    security: str
    on: date
    shares: Decimal
    reason: str


@dataclass(frozen=True)
class Enrolment:
    account_id: str
    security: str
    effective_from: date
    enrolled: bool


@dataclass(frozen=True)
class DividendEvent:
    event_id: str
    security: str
    record_date: date
    pay_date: date
    per_share: Decimal
    reinvest_price: Decimal


@dataclass(frozen=True)
class Payment:
    event_id: str
    account_id: str
    gross: Decimal
    withholding: Decimal
    fee: Decimal
    cash_paid: Decimal
    shares_bought: Decimal
    leftover: Decimal
