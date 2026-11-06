import json
import os
import tempfile
from datetime import datetime
from urllib.parse import urlsplit

from edge.adapters.transport import HttpResult
from edge.clock import FixedClock
from edge.db import Database
from edge.http import Request
from edge.ids import SequentialIds
from edge.wiring import build

NOW = datetime(2026, 6, 1, 14, 0)
PARTNER_KEY = "fxp_live_secret"


class FakeUpstreams:
    """Every upstream answers 200 with an echo unless results are queued for it (by host, e.g. 'orders.internal')."""

    def __init__(self):
        self.calls = []
        self.scripts: dict[str, list] = {}

    def queue(self, host: str, *results) -> None:
        self.scripts.setdefault(host, []).extend(results)

    def send(self, method, url, headers, body, timeout):
        host = urlsplit(url).hostname
        self.calls.append({"method": method, "url": url, "host": host, "headers": dict(headers), "body": body})
        script = self.scripts.get(host)
        result = script.pop(0) if script else HttpResult(200, {"ok": True, "path": urlsplit(url).path})
        if isinstance(result, Exception):
            raise result
        return result

    def to(self, host):
        return [c for c in self.calls if c["host"] == host]


class World:
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.clock = FixedClock(NOW)
        self.upstreams = FakeUpstreams()
        self.db = Database(os.path.join(self._dir.name, "edge.db"))
        self.c = build(self.db, self.clock, SequentialIds(), self.upstreams, partner_api_key=PARTNER_KEY)
        self.alder = self.c.auth.issue("svc_alder", "org_alder", {"client"}, ttl_hours=24 * 30)
        self.birch = self.c.auth.issue("svc_birch", "org_birch", {"client"}, ttl_hours=24 * 30)
        self.ops = self.c.auth.issue("usr_ops", "org_internal", {"ops"}, ttl_hours=24 * 30)

    def cleanup(self):
        self._dir.cleanup()

    def call(self, method, target, token=None, body=None, headers=None):
        h = dict(headers or {})
        if token:
            h["Authorization"] = f"Bearer {token}"
        raw = json.dumps(body).encode() if body is not None else b""
        if raw:
            h.setdefault("Content-Type", "application/json")
        return self.c.app.handle(Request.build(method, target, h, raw))

    def breaker(self, name):
        return self.c.proxy.breakers[name]
