from collections import defaultdict
from decimal import Decimal

from .services.statements import StatementService
from .store import InMemoryStore


def revenue_by_component(store: InMemoryStore, year: int, month: int) -> dict:
    statements = StatementService(store)
    totals = defaultdict(Decimal)
    for account_id in sorted(store.accounts):
        for line in statements.build(account_id, year, month).lines:
            totals["commission"] += line.commission
            totals["discount"] += line.discount
            totals["regulatory"] += line.reg_fee
    totals["net"] = totals["commission"] - totals["discount"]
    return {k: str(v) for k, v in totals.items()}
