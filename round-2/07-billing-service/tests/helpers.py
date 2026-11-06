import json
import os
import tempfile
from datetime import datetime

from billing.adapters.transport import HttpResult, TransportTimeout
from billing.clock import FixedClock
from billing.db import Database
from billing.http import Request
from billing.ids import SequentialIds
from billing.wiring import build

NOW = datetime(2026, 6, 16, 10, 0)
SECRET = "pg_secret"


class FakeTaxly:
    """8% in the US, 20% in the UK. Put exceptions in .failures to make the next calls fail."""

    RATES = {"US": 8, "GB": 20}

    def __init__(self):
        self.failures = []
        self.calls = []

    def send(self, method, url, headers, body, timeout):
        payload = json.loads(body)
        self.calls.append(payload)
        if self.failures:
            raise self.failures.pop(0)
        return HttpResult(200, {"tax_amount": payload["amount"] * self.RATES[payload["country"]] // 100})


class World:
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.clock = FixedClock(NOW)
        self.tax = FakeTaxly()
        self.db = Database(os.path.join(self._dir.name, "billing.db"))
        self.c = build(self.db, self.clock, SequentialIds(), self.tax, SECRET)
        self.c.customers.add("cus_acme", "Acme Asset Management", "US", 10, 4_999)
        self.c.customers.add("cus_birch", "Birch Capital", "GB", 3, 4_999)
        self.acme = self.c.auth.issue("usr_ann", "cus_acme", {"billing_admin"}, ttl_hours=24 * 365)
        self.acme_viewer = self.c.auth.issue("usr_vic", "cus_acme", {"viewer"}, ttl_hours=24 * 365)
        self.birch = self.c.auth.issue("usr_bo", "cus_birch", {"billing_admin"}, ttl_hours=24 * 365)
        self.metering = self.c.auth.issue("svc_meter", "internal", {"metering"}, ttl_hours=24 * 365)

    def cleanup(self):
        self._dir.cleanup()

    def call(self, method, target, token=None, body=None, headers=None):
        h = dict(headers or {})
        if token:
            h["Authorization"] = f"Bearer {token}"
        raw = json.dumps(body).encode() if body is not None else b""
        return self.c.app.handle(Request.build(method, target, h, raw))

    def usage(self, event_id, customer_id, quantity, occurred_at):
        return self.call("POST", "/internal/usage", self.metering, {"event_id": event_id, "customer_id": customer_id,
                                                                    "quantity": quantity, "occurred_at": occurred_at})

    def run_invoices(self, period="2026-06"):
        self.c.invoice_run.schedule(period)
        self.c.worker.run_pending()

    def invoices(self, token):
        return self.call("GET", "/invoices", token).body["invoices"]

    def paid(self, invoice_id, payment_id, amount_cents, event_id="evt_1"):
        return self.call("POST", "/webhooks/paygate", headers={"X-Paygate-Secret": SECRET},
                         body={"id": event_id, "type": "payment.succeeded",
                               "data": {"invoice_id": invoice_id, "payment_id": payment_id, "amount_cents": amount_cents}})


__all__ = ["World", "FakeTaxly", "HttpResult", "TransportTimeout", "NOW", "SECRET"]
