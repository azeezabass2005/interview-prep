from collections import defaultdict
from decimal import Decimal

from ..store import InMemoryStore


def tax_report(store: InMemoryStore, event_id: str) -> dict:
    by_country = defaultdict(Decimal)
    for payment in store.payments.get(event_id, []):
        by_country[store.account(payment.account_id).country.upper()] += payment.withholding
    return {country: str(amount) for country, amount in sorted(by_country.items())}


def event_totals(store: InMemoryStore, event_id: str) -> dict:
    payments = store.payments.get(event_id, [])
    return {
        "accounts": len(payments),
        "gross": str(sum((p.gross for p in payments), Decimal("0"))),
        "cash_paid": str(sum((p.cash_paid for p in payments), Decimal("0"))),
        "shares_issued": str(sum((p.shares_bought for p in payments), Decimal("0"))),
    }
