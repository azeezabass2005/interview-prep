import json
import os
import tempfile
from datetime import datetime

from blotter.clock import FixedClock
from blotter.db import Database
from blotter.http import Request
from blotter.ids import SequentialIds
from blotter.models import Counterparty
from blotter.wiring import build

NOW = datetime(2026, 6, 5, 14, 0)  # Friday, 10:00 in New York


class World:
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.clock = FixedClock(NOW)
        self.db = Database(os.path.join(self._dir.name, "blotter.db"))
        self.c = build(self.db, self.clock, SequentialIds())
        self.c.counterparties.add(Counterparty("cp_gs", "Goldfinch Securities", "5493001KJTIIGC8Y1R12"))
        self.c.counterparties.add(Counterparty("cp_ms", "Morrow Stanley", "IGJSJL3JD5P30I6NJZ34"))
        self.c.counterparties.add(Counterparty("cp_jp", "JP Margate", "8I5DZWZKVSZI1NUHU748"))
        issue = self.c.auth.issue
        self.rita = issue("usr_rita", "rates", {"trader"})
        self.rob = issue("usr_rob", "rates", {"trader"})
        self.ray = issue("usr_ray", "rates", {"desk_head"})
        self.felix = issue("usr_felix", "fx", {"trader"})
        self.fay = issue("usr_fay", "fx", {"desk_head"})
        self.carla = issue("usr_carla", "compliance", {"compliance"})

    def cleanup(self):
        self._dir.cleanup()

    def call(self, method, target, token, body=None):
        raw = json.dumps(body).encode() if body is not None else b""
        return self.c.app.handle(Request.build(method, target, {"Authorization": f"Bearer {token}"}, raw))

    def book(self, token, symbol="UST10Y", side="buy", quantity=100, price_cents=9_850, cp="cp_gs"):
        return self.call("POST", "/trades", token, {"symbol": symbol, "side": side, "quantity": quantity,
                                                    "price_cents": price_cents, "counterparty_id": cp})
