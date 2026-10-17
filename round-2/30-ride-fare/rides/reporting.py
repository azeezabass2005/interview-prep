from decimal import Decimal

from .models import COMPLETED
from .store import InMemoryStore


def driver_earnings(store: InMemoryStore, driver: str) -> dict:
    trips = [t for t in store.for_driver(driver) if t.status == COMPLETED]
    return {"driver": driver, "trips": len(trips),
            "earnings": str(sum((t.driver_payout for t in trips), Decimal("0.00")))}
