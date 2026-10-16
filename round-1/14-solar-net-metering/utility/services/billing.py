from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from ..config import DAILY_SERVICE, TAX_RATE, TRUE_UP_MONTH, TRUE_UP_RATE
from ..errors import BillingError, NotFound
from ..models import Account, Bill, Reading
from ..store import InMemoryStore
from .meters import register_delta
from .tariff import energy_charge

CENT = Decimal("0.01")


def cents(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


class BillingService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def open_account(self, account_id: str, address: str, first: Reading) -> Account:
        account = Account(account_id, address, [first])
        self._store.accounts[account_id] = account
        return account

    def _account(self, account_id: str) -> Account:
        account = self._store.account(account_id)
        if account is None:
            raise NotFound(account_id)
        return account

    def read(self, account_id: str, reading: Reading) -> Bill:
        account = self._account(account_id)
        previous = account.readings[-1]
        if reading.read_on <= previous.read_on:
            raise BillingError("readings must be in date order")
        days = (reading.read_on - previous.read_on).days
        imported = register_delta(previous.import_register, reading.import_register)
        exported = register_delta(previous.export_register, reading.export_register)
        net = imported - exported
        billable = 0
        if net < 0:
            account.bank_kwh += -net
        else:
            used = min(account.bank_kwh, net)
            billable = net - used
        energy = cents(energy_charge(billable, days))
        service = cents(DAILY_SERVICE * days)
        tax = cents((energy + service) * TAX_RATE)
        payout = Decimal("0.00")
        if previous.read_on.month == TRUE_UP_MONTH:
            payout = cents(account.bank_kwh * TRUE_UP_RATE)
            account.bank_kwh = 0
        bill = Bill(previous.read_on, reading.read_on, days, imported, exported, billable, energy, tax, service,
                    energy + tax + service, payout)
        account.readings.append(reading)
        account.bills.append(bill)
        return bill
