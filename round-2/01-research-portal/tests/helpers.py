import json
import os
import tempfile
from datetime import datetime

from portal.adapters.transport import FakeTransport, HttpResult
from portal.clock import FixedClock, iso
from portal.db import Database
from portal.http import Request
from portal.ids import SequentialIds
from portal.models import Org, Report, User
from portal.wiring import build

NOW = datetime(2026, 6, 1, 9, 0)


class World:
    """A fresh service on a temp database, with a fake email provider and a fixed clock."""

    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.clock = FixedClock(NOW)
        self.email = FakeTransport(HttpResult(202, {"message_id": "msg_1"}))
        self.db = Database(os.path.join(self._dir.name, "portal.db"))
        self.c = build(self.db, self.clock, SequentialIds(), self.email)
        self.c.orgs.insert(Org("org_internal", "Research", "internal"))
        self.c.users.insert(User("usr_analyst", "org_internal", "ana@research.example", "Ana", False, None))
        self.analyst = self.c.auth.issue("usr_analyst", "org_internal", {"analyst", "editor"})

    def cleanup(self):
        self._dir.cleanup()

    def client_user(self, org_id: str, user_id: str, sectors=(), starts_on="2026-01-01", ends_on="2027-01-01",
                    digest=True) -> str:
        if self.c.orgs.get(org_id) is None:
            self.c.orgs.insert(Org(org_id, org_id.replace("org_", "").title(), "client"))
            for i, sector in enumerate(sectors):
                self.c.entitlements.add(f"sub_{org_id}_{i}", org_id, sector, starts_on, ends_on)
        self.c.users.insert(User(user_id, org_id, f"{user_id}@client.example", user_id, digest, None))
        return self.c.auth.issue(user_id, org_id, {"reader"})

    def published(self, title: str, sector: str, at: datetime | None = None) -> Report:
        at = at or self.clock.now()
        report = Report(f"rpt_{title.lower().replace(' ', '_')}", title, sector, "usr_analyst", "published",
                        f"{title} summary", f"{title} body", iso(at), iso(at))
        self.c.reports._reports.insert(report)
        return report

    def call(self, method: str, target: str, token: str | None = None, body: dict | None = None, headers=None):
        h = dict(headers or {})
        if token:
            h["Authorization"] = f"Bearer {token}"
        raw = json.dumps(body).encode() if body is not None else b""
        return self.c.app.handle(Request.build(method, target, h, raw))
