FIXES = [
    ("alerts/repositories/alerts.py",
     "    def set_armed(self, alert_id: int, armed: bool) -> None:",
     """    def try_disarm(self, alert_id: int) -> bool:
        \"\"\"Atomically fire: only one caller wins, and only for an armed, active alert.\"\"\"
        with self._db.transaction() as conn:
            cur = conn.execute("UPDATE alerts SET armed = 0 WHERE alert_id = ? AND armed = 1 AND active = 1",
                               (alert_id,))
        return cur.rowcount == 1

    def rearm(self, alert_id: int) -> None:
        with self._db.transaction() as conn:
            conn.execute("UPDATE alerts SET armed = 1 WHERE alert_id = ? AND armed = 0 AND active = 1", (alert_id,))

    def set_armed(self, alert_id: int, armed: bool) -> None:"""),
    ("alerts/services/evaluator.py",
     """            if self.reached(alert, price):
                self._fire(alert, price)
                enqueued += 1""",
     """            if self.reached(alert, price):
                if self._alerts.try_disarm(alert.alert_id):
                    self._fire(alert, price)
                    enqueued += 1
            elif (price < self.rearm_level(alert)) if alert.direction == "ABOVE" else (price > self.rearm_level(alert)):
                self._alerts.rearm(alert.alert_id)"""),
    ("alerts/services/quiet_hours.py", "    return start <= local < end",
     "    if start <= end:\n        return start <= local < end\n    return local >= start or local < end"),
    ("alerts/repositories/deliveries.py",
     "    def mark_sent(self, delivery_id: int, worker_id: str, at: datetime) -> None:",
     """    def claim(self, delivery_id: int, worker_id: str, at: datetime) -> bool:
        with self._db.transaction() as conn:
            cur = conn.execute(
                "UPDATE deliveries SET status = 'SENDING', sent_by = ?, sent_at = ? "
                "WHERE delivery_id = ? AND status = 'PENDING'",
                (worker_id, at.isoformat(), delivery_id))
        return cur.rowcount == 1

    def mark_sent(self, delivery_id: int, worker_id: str, at: datetime) -> None:"""),
    ("alerts/services/delivery.py",
     "            self._sender.send(d.user_id, d.message)\n",
     "            if not self._deliveries.claim(d.delivery_id, self.worker_id, self._clock.now()):\n"
     "                continue\n            self._sender.send(d.user_id, d.message)\n"),
]
