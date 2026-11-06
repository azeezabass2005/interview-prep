import json
import os
import tempfile
from datetime import datetime
from urllib.parse import parse_qs, urlsplit

from expenses.adapters.transport import HttpResult
from expenses.clock import FixedClock
from expenses.db import Database
from expenses.http import Request
from expenses.ids import SequentialIds
from expenses.models import Employee
from expenses.wiring import build

NOW = datetime(2026, 6, 20, 10, 0)


class FakeRatesy:
    """EUR/USD and GBP/USD by date; unknown dates use the 'default' rate."""

    def __init__(self):
        self.rates = {("EUR", "2026-06-02"): 1.08, ("EUR", "2026-06-18"): 1.15, ("GBP", "default"): 1.25,
                      ("EUR", "default"): 1.10, ("JPY", "default"): 0.0064}
        self.calls = []

    def send(self, method, url, headers, body, timeout):
        q = {k: v[0] for k, v in parse_qs(urlsplit(url).query).items()}
        self.calls.append(q)
        rate = self.rates.get((q["base"], q["date"]), self.rates[(q["base"], "default")])
        return HttpResult(200, {"base": q["base"], "date": q["date"], "rates": {q["symbols"]: rate}})


class FakeScanly:
    """Reads 'total=<x>' out of the (fake) image; 'blurry' images are unreadable (422)."""

    def __init__(self):
        self.calls = 0

    def send(self, method, url, headers, body, timeout):
        self.calls += 1
        image = json.loads(body)["image"]
        if "blurry" in image:
            return HttpResult(422, {"error": "receipt is unreadable"})
        return HttpResult(200, {"total": image.split("total=")[1]})


class World:
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.clock = FixedClock(NOW)
        self.fx, self.ocr = FakeRatesy(), FakeScanly()
        self.db = Database(os.path.join(self._dir.name, "expenses.db"))
        self.c = build(self.db, self.clock, SequentialIds(), self.fx, self.ocr)
        for e in (Employee("emp_dir", "org_acme", "Dana (director)", None),
                  Employee("emp_maria", "org_acme", "Maria", "emp_dir"),
                  Employee("emp_omar", "org_acme", "Omar", "emp_dir"),
                  Employee("emp_eli", "org_acme", "Eli", "emp_maria"),
                  Employee("emp_finn", "org_acme", "Finn", "emp_omar"),
                  Employee("emp_zoe", "org_other", "Zoe", None)):
            self.c.employees.add(e)
        issue = lambda uid, org, roles: self.c.auth.issue(uid, org, roles, ttl_hours=24 * 30)
        self.eli = issue("emp_eli", "org_acme", {"employee"})
        self.finn = issue("emp_finn", "org_acme", {"employee"})
        self.maria = issue("emp_maria", "org_acme", {"employee", "manager"})
        self.omar = issue("emp_omar", "org_acme", {"employee", "manager"})
        self.zoe = issue("emp_zoe", "org_other", {"employee", "manager"})

    def cleanup(self):
        self._dir.cleanup()

    def call(self, method, target, token, body=None):
        raw = json.dumps(body).encode() if body is not None else b""
        return self.c.app.handle(Request.build(method, target, {"Authorization": f"Bearer {token}"}, raw))

    def report(self, token, title="Berlin client visit"):
        return self.call("POST", "/reports", token, {"title": title}).body["id"]

    def expense(self, token, report_id, amount_minor=4_250, currency="USD", spent_on="2026-06-10", merchant="Cafe",
                category="meals"):
        return self.call("POST", f"/reports/{report_id}/expenses", token,
                         {"amount_minor": amount_minor, "currency": currency, "spent_on": spent_on, "merchant": merchant,
                          "category": category})

    def submitted_report(self, token):
        rid = self.report(token)
        self.expense(token, rid)
        self.call("POST", f"/reports/{rid}/submit", token)
        return rid
