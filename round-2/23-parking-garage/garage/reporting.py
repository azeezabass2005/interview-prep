from datetime import datetime, timedelta

from .store import InMemoryStore


def daily_revenue(store: InMemoryStore, day) -> dict:
    start = datetime(day.year, day.month, day.day)
    tickets = store.closed_between(start, start + timedelta(days=1))
    paid = [t for t in tickets if t.charge_cents]
    return {"day": day.isoformat(), "exits": len(tickets), "paid_exits": len(paid),
            "revenue_cents": sum(t.charge_cents for t in paid),
            "validated": sum(1 for t in tickets if t.validated)}
