from datetime import date
from decimal import Decimal

from drip.ledger import Ledger
from drip.models import Account, DividendEvent
from drip.processor import DripProcessor

Q1 = DividendEvent("BBG", date(2026, 3, 10), date(2026, 3, 31), Decimal("0.82"), Decimal("40.00"))
Q2 = DividendEvent("BBG", date(2026, 6, 10), date(2026, 6, 30), Decimal("0.82"), Decimal("40.00"))


def setup(*accounts_and_shares, opened=date(2026, 1, 5)):
    """accounts_and_shares: (Account, shares) pairs, all bought on `opened`."""
    ledger = Ledger()
    accounts = {}
    for account, shares in accounts_and_shares:
        accounts[account.account_id] = account
        ledger.record(opened, account.account_id, shares)
    return ledger, DripProcessor(ledger, accounts)


def by_account(payments):
    return {p.account_id: p for p in payments}
