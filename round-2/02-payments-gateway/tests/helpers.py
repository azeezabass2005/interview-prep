import json
import os
import tempfile
from datetime import datetime

from gateway.adapters.transport import FakeTransport, HttpResult
from gateway.adapters.webhooks import sign
from gateway.clock import FixedClock
from gateway.db import Database
from gateway.http import Request
from gateway.ids import SequentialIds
from gateway.wiring import build

NOW = datetime(2026, 6, 1, 9, 0)
WEBHOOK_SECRET = "whsec_test"
CARD = "tok_card_visa_4242"


def charge_ok(charge_id="ch_1", status="succeeded"):
    return HttpResult(200, {"id": charge_id, "status": status})


class World:
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.clock = FixedClock(NOW)
        self.psp = FakeTransport(charge_ok())
        self.db = Database(os.path.join(self._dir.name, "gateway.db"))
        self.c = build(self.db, self.clock, SequentialIds(), self.psp, WEBHOOK_SECRET)
        self.db.execute("INSERT INTO merchants (id, name, country) VALUES ('mch_bean', 'Bean & Co', 'US')")
        self.db.execute("INSERT INTO merchants (id, name, country) VALUES ('mch_kyoto', 'Kyoto Tea House', 'JP')")
        self.bean = self.c.auth.issue("usr_bean", "mch_bean", {"merchant"})
        self.kyoto = self.c.auth.issue("usr_kyoto", "mch_kyoto", {"merchant"})

    def cleanup(self):
        self._dir.cleanup()

    def call(self, method, target, token=None, body=None, headers=None, raw: bytes | None = None):
        h = dict(headers or {})
        if token:
            h["Authorization"] = f"Bearer {token}"
        data = raw if raw is not None else (json.dumps(body).encode() if body is not None else b"")
        return self.c.app.handle(Request.build(method, target, h, data))

    def pay(self, token=None, key="order-1", amount="12.50", currency="USD", card=CARD):
        return self.call("POST", "/payments", token or self.bean,
                         {"amount": amount, "currency": currency, "card_token": card, "description": "Coffee beans"},
                         {"Idempotency-Key": key})

    def webhook(self, event: dict, raw: bytes | None = None, secret=WEBHOOK_SECRET, at=None):
        body = raw if raw is not None else json.dumps(event, separators=(",", ":")).encode()
        ts = int((at or self.clock.now()).timestamp())
        header = f"t={ts},v1={sign(secret, ts, body)}"
        return self.call("POST", "/webhooks/paystream", headers={"Paystream-Signature": header}, raw=body)
