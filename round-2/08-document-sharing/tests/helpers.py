import json
import os
import tempfile
from datetime import datetime

from vault.clock import FixedClock
from vault.db import Database
from vault.http import Request
from vault.ids import SequentialIds
from vault.wiring import build

NOW = datetime(2026, 6, 1, 9, 0)


class World:
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.clock = FixedClock(NOW)
        self.db = Database(os.path.join(self._dir.name, "vault.db"))
        self.c = build(self.db, self.clock, SequentialIds())
        issue = lambda uid, ws: self.c.auth.issue(uid, ws, {"member"}, ttl_hours=24 * 365)
        self.nadia = issue("usr_nadia", "ws_ib")
        self.tom = issue("usr_tom", "ws_ib")
        self.uma = issue("usr_uma", "ws_ib")
        self.outsider = issue("usr_ola", "ws_other")

    def cleanup(self):
        self._dir.cleanup()

    def call(self, method, target, token=None, body=None, headers=None, raw: bytes | None = None):
        h = dict(headers or {})
        if token:
            h["Authorization"] = f"Bearer {token}"
        data = raw if raw is not None else (json.dumps(body).encode() if body is not None else b"")
        return self.c.app.handle(Request.build(method, target, h, data))

    def doc(self, token, title="Q3 plan", content="Draft one"):
        return self.call("POST", "/documents", token, {"title": title, "content": content}).body
