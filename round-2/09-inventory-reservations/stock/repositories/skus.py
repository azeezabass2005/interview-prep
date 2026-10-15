from typing import Dict, List, Optional

from ..db import Database
from ..models import Sku


def _to_sku(r) -> Sku:
    return Sku(r["sku"], r["name"], r["on_hand"], r["reserved"], r["reorder_point"], bool(r["is_bundle"]))


class SkuRepository:
    def __init__(self, db: Database):
        self._db = db

    def add(self, sku: str, name: str, on_hand: int, reorder_point: int = 0) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO skus (sku, name, on_hand, reorder_point) VALUES (?, ?, ?, ?)",
                         (sku, name, on_hand, reorder_point))

    def add_bundle(self, sku: str, name: str, components: Dict[str, int]) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO skus (sku, name, is_bundle) VALUES (?, ?, 1)", (sku, name))
            conn.executemany("INSERT INTO bundle_components VALUES (?, ?, ?)",
                             [(sku, c, q) for c, q in components.items()])

    def get(self, sku: str) -> Optional[Sku]:
        with self._db.transaction() as conn:
            r = conn.execute("SELECT * FROM skus WHERE sku = ?", (sku,)).fetchone()
        return _to_sku(r) if r else None

    def components(self, bundle_sku: str) -> Dict[str, int]:
        with self._db.transaction() as conn:
            rows = conn.execute("SELECT component_sku, qty FROM bundle_components WHERE bundle_sku = ?",
                                (bundle_sku,)).fetchall()
        return {r["component_sku"]: r["qty"] for r in rows}

    def set_reserved(self, sku: str, reserved: int) -> None:
        with self._db.transaction() as conn:
            conn.execute("UPDATE skus SET reserved = ? WHERE sku = ?", (reserved, sku))

    def adjust_reserved(self, sku: str, delta: int) -> None:
        with self._db.transaction() as conn:
            conn.execute("UPDATE skus SET reserved = reserved + ? WHERE sku = ?", (delta, sku))

    def record_sale(self, sku: str, qty: int) -> None:
        with self._db.transaction() as conn:
            conn.execute("UPDATE skus SET on_hand = on_hand - ?, reserved = reserved - ? WHERE sku = ?", (qty, qty, sku))

    def all_stocked(self) -> List[Sku]:
        with self._db.transaction() as conn:
            rows = conn.execute("SELECT * FROM skus WHERE is_bundle = 0 ORDER BY sku").fetchall()
        return [_to_sku(r) for r in rows]
