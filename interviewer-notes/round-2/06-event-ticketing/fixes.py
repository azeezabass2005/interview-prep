FIXES = [
    ("boxoffice/services/pricing.py", "    fees = SERVICE_FEE_CENTS\n", "    fees = SERVICE_FEE_CENTS * seat_count\n"),
    ("boxoffice/services/refunds.py", "from ..config import REFUND_CUTOFF_HOURS",
     "from datetime import timezone\nfrom zoneinfo import ZoneInfo\n\nfrom ..config import REFUND_CUTOFF_HOURS"),
    ("boxoffice/services/refunds.py",
     "        return (event.starts_at_local - self._clock.now()).total_seconds() / 3600",
     "        starts_utc = event.starts_at_local.replace(tzinfo=ZoneInfo(event.venue_tz)).astimezone(timezone.utc)\n"
     "        now_utc = self._clock.now().replace(tzinfo=timezone.utc)\n"
     "        return (starts_utc - now_utc).total_seconds() / 3600"),
    ("boxoffice/services/seating.py", "seat.hold_expires_at < str(self._clock.now())",
     "seat.hold_expires_at < self._clock.now().isoformat()"),
    ("boxoffice/repositories/seats.py",
     "    def mark_sold(self, event_id: str, seat_ids, order_id: str) -> None:",
     """    def try_hold(self, event_id: str, seat_ids, customer: str, expires_at: datetime, now: datetime) -> bool:
        \"\"\"Hold every seat or none. A seat is claimable if AVAILABLE or its hold has expired.\"\"\"
        with self._db.transaction() as conn:
            conn.execute("BEGIN IMMEDIATE")
            for seat_id in seat_ids:
                cur = conn.execute(
                    "UPDATE seats SET status = 'HELD', held_by = ?, hold_expires_at = ? "
                    "WHERE event_id = ? AND seat_id = ? AND "
                    "(status = 'AVAILABLE' OR (status = 'HELD' AND hold_expires_at < ?))",
                    (customer, expires_at.isoformat(), event_id, seat_id, now.isoformat()))
                if cur.rowcount != 1:
                    conn.rollback()
                    return False
        return True

    def mark_sold(self, event_id: str, seat_ids, order_id: str) -> None:"""),
    ("boxoffice/services/seating.py",
     """        expires = self._clock.now() + timedelta(minutes=HOLD_MINUTES)
        for seat in seats:
            self._seats.set_hold(event_id, seat.seat_id, customer, expires)""",
     """        now = self._clock.now()
        expires = now + timedelta(minutes=HOLD_MINUTES)
        if not self._seats.try_hold(event_id, [s.seat_id for s in seats], customer, expires, now):
            raise SeatUnavailable("one or more seats were just taken")"""),
]
