from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import List


class Manifest:
    def __init__(self):
        self._entries = defaultdict(list)

    def add(self, ship_on: date, carrier: str, order_id: str, packages: int, charge: Decimal) -> None:
        self._entries[(ship_on, carrier)].append((order_id, packages, charge))

    def for_pickup(self, ship_on: date, carrier: str) -> dict:
        rows = self._entries.get((ship_on, carrier), [])
        return {"date": ship_on.isoformat(), "carrier": carrier, "orders": len(rows),
                "packages": sum(r[1] for r in rows), "charged": str(sum((r[2] for r in rows), Decimal("0.00")))}

    def carriers_on(self, ship_on: date) -> List[str]:
        return sorted({c for (d, c) in self._entries if d == ship_on})
