import json
import os
import tempfile
from datetime import datetime
from urllib.parse import parse_qs, urlsplit

from quotes.adapters.transport import HttpResult
from quotes.clock import FixedClock
from quotes.db import Database
from quotes.http import Request
from quotes.ids import SequentialIds
from quotes.models import Bar, Instrument
from quotes.seed import INSTRUMENTS
from quotes.wiring import build

NOW = datetime(2026, 6, 1, 14, 30)
LB_ADDR = "10.0.0.2"  # every request reaches us through the load balancer


class FakeTickstream:
    """Serves prices from a dict; set .down = True to return 503s. Records each call's URL."""

    def __init__(self):
        self.prices = {"AAPL": (190.0, "USD"), "MSFT": (420.0, "USD"), "ORLY": (1050.0, "USD"),
                       "VOD": (0.72, "GBP"), "SAP": (180.0, "EUR")}
        self.fx = {"USDEUR": 0.9, "USDGBP": 0.8, "GBPUSD": 1.25, "EURUSD": 1.1}
        self.down = False
        self.calls = []

    def send(self, method, url, headers, body, timeout):
        self.calls.append(url)
        if self.down:
            return HttpResult(503, {"error": "maintenance"})
        parts = urlsplit(url)
        params = {k: v[0] for k, v in parse_qs(parts.query).items()}
        if parts.path.endswith("/quotes"):
            return HttpResult(200, {"quotes": [{"symbol": s, "price": self.prices[s][0], "currency": self.prices[s][1],
                                                "ts": "2026-06-01T14:30:00"} for s in params["symbols"].split(",")
                                               if s in self.prices]})
        return HttpResult(200, {"rate": self.fx[params["pair"]]})

    def quote_calls(self):
        return [u for u in self.calls if "/quotes" in u]


class World:
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.clock = FixedClock(NOW)
        self.vendor = FakeTickstream()
        self.db = Database(os.path.join(self._dir.name, "quotes.db"))
        self.c = build(self.db, self.clock, SequentialIds(), self.vendor)
        for i in INSTRUMENTS:
            self.c.instruments.add(i)
        self.c.bars.add("AAPL", Bar("2026-05-28", 188, 191, 187, 190, 1000))
        self.c.bars.add("AAPL", Bar("2026-05-29", 190, 193, 189, 192, 1200))
        self.basic = self.c.auth.issue("usr_basic", "org_alder", {"basic"})
        self.pro = self.c.auth.issue("usr_pro", "org_birch", {"pro"})
        self.ops = self.c.auth.issue("usr_ops", "org_internal", {"pro", "ops"})

    def cleanup(self):
        self._dir.cleanup()

    def get(self, target, token=None, remote_addr=LB_ADDR):
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        return self.c.app.handle(Request.build("GET", target, headers, b"", remote_addr))
