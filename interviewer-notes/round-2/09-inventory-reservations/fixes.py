FIXES = [
    ("stock/services/availability.py",
     "        return min(self._skus.get(component).available for component in components)",
     "        return min(self._skus.get(component).available // per for component, per in components.items())"),
    ("stock/services/reports.py", "if s.on_hand < s.reorder_point]", "if s.on_hand <= s.reorder_point]"),
    ("stock/repositories/reservations.py",
     "    def set_status(self, reservation_id: int, status: str) -> None:",
     """    def reserve_units(self, cart_id: str, units, expires_at: datetime) -> bool:
        \"\"\"Reserve every component or none.\"\"\"
        with self._db.transaction() as conn:
            conn.execute("BEGIN IMMEDIATE")
            for sku, qty in units.items():
                cur = conn.execute("UPDATE skus SET reserved = reserved + ? WHERE sku = ? AND on_hand - reserved >= ?",
                                   (qty, sku, qty))
                if cur.rowcount != 1:
                    conn.rollback()
                    return False
                conn.execute("INSERT INTO reservations (cart_id, sku, qty, expires_at) VALUES (?, ?, ?, ?)",
                             (cart_id, sku, qty, expires_at.isoformat()))
        return True

    def release_if_active(self, reservation_id: int) -> bool:
        with self._db.transaction() as conn:
            row = conn.execute("SELECT sku, qty FROM reservations WHERE reservation_id = ?", (reservation_id,)).fetchone()
            cur = conn.execute("UPDATE reservations SET status = 'RELEASED' WHERE reservation_id = ? AND status = 'ACTIVE'",
                               (reservation_id,))
            if cur.rowcount != 1:
                return False
            conn.execute("UPDATE skus SET reserved = reserved - ? WHERE sku = ?", (row["qty"], row["sku"]))
        return True

    def set_status(self, reservation_id: int, status: str) -> None:"""),
    ("stock/services/reservations.py",
     """        units = self._units_for(sku, qty)
        for component, needed in units.items():
            item = self._skus.get(component)
            if item.available < needed:
                raise InsufficientStock(f"{component}: {item.available} available, {needed} requested")
        expires = self._clock.now() + timedelta(minutes=RESERVATION_MINUTES)
        for component, needed in units.items():
            item = self._skus.get(component)
            self._skus.set_reserved(component, item.reserved + needed)
            self._reservations.create(cart_id, component, needed, expires)""",
     """        units = self._units_for(sku, qty)
        expires = self._clock.now() + timedelta(minutes=RESERVATION_MINUTES)
        if not self._reservations.reserve_units(cart_id, units, expires):
            raise InsufficientStock(f"not enough stock for {qty} x {sku}")"""),
    ("stock/services/reservations.py",
     "            self._skus.adjust_reserved(r.sku, -r.qty)\n            released += 1",
     "            if self._reservations.release_if_active(r.reservation_id):\n                released += 1"),
]
