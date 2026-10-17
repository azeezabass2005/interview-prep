from collections import defaultdict
from decimal import Decimal

from .store import InMemoryStore


def annual_statement(store: InMemoryStore, account_id: str, year: int) -> dict:
    account = store.account(account_id)
    months = defaultdict(lambda: {"imported": 0, "exported": 0, "total": Decimal("0.00")})
    payout = Decimal("0.00")
    for bill in account.bills:
        if bill.period_end.year != year:
            continue
        row = months[bill.period_end.month]
        row["imported"] += bill.imported
        row["exported"] += bill.exported
        row["total"] += bill.total
        payout += bill.true_up_payout
    return {"year": year, "months": {m: {k: str(v) for k, v in row.items()} for m, row in sorted(months.items())},
            "billed": str(sum((r["total"] for r in months.values()), Decimal("0.00"))), "true_up": str(payout),
            "self_sufficiency": _ratio(sum(r["exported"] for r in months.values()), sum(r["imported"] for r in months.values()))}


def _ratio(exported: int, imported: int) -> str:
    if imported == 0:
        return "n/a"
    return f"{min(exported / imported, 1.0):.0%}"
