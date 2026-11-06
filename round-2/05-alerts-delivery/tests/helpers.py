import json
import os
import tempfile
from datetime import datetime

from alerts.adapters.transport import FakeTransport, HttpResult
from alerts.clock import FixedClock
from alerts.db import Database
from alerts.http import Request
from alerts.ids import SequentialIds
from alerts.models import User
from alerts.wiring import build

NOW = datetime(2026, 6, 1, 13, 30)


class World:
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.clock = FixedClock(NOW)
        self.sms = FakeTransport(HttpResult(201, {"sid": "SM1"}))
        self.email = FakeTransport(HttpResult(202, {"message_id": "msg_1"}))
        self.db = Database(os.path.join(self._dir.name, "alerts.db"))
        self.c = build(self.db, self.clock, SequentialIds(), self.sms, self.email)
        self.c.users.add(User("usr_maya", "org_retail", "Maya", "maya.lee@example.com", "+447700900123"))
        self.c.users.add(User("usr_omar", "org_retail", "Omar", "omar@example.com", "+44 7700 900456"))
        self.maya = self.c.auth.issue("usr_maya", "org_retail", {"user"})
        self.omar = self.c.auth.issue("usr_omar", "org_retail", {"user"})
        self.support = self.c.auth.issue("usr_sam", "org_retail", {"user", "support"})
        self.feed = self.c.auth.issue("svc_feed", "org_internal", {"feed"})
        self.worker = self.c.worker()

    def cleanup(self):
        self._dir.cleanup()

    def call(self, method, target, token, body=None):
        raw = json.dumps(body).encode() if body is not None else b""
        return self.c.app.handle(Request.build(method, target, {"Authorization": f"Bearer {token}"}, raw))

    def rule(self, token, symbol="AAPL", direction="above", threshold=200, channel="sms"):
        return self.call("POST", "/rules", token, {"symbol": symbol, "direction": direction, "threshold": threshold,
                                                   "channel": channel})

    def tick(self, symbol, price):
        return self.call("POST", "/internal/prices", self.feed, {"symbol": symbol, "price": price})
