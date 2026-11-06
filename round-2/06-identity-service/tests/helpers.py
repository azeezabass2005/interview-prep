import json
import os
import re
import tempfile
from datetime import datetime

from identity.adapters.transport import FakeTransport, HttpResult
from identity.clock import FixedClock, iso
from identity.db import Database
from identity.http import Request
from identity.ids import SequentialIds
from identity.models import User
from identity.passwords import hash_password
from identity.wiring import build

NOW = datetime(2026, 6, 1, 8, 0)
PASSWORD = "Correct-Horse-42"


class World:
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.clock = FixedClock(NOW)
        self.email = FakeTransport(HttpResult(202, {"message_id": "m1"}))
        self.db = Database(os.path.join(self._dir.name, "identity.db"))
        self.c = build(self.db, self.clock, SequentialIds(), self.email)
        hashed = hash_password(PASSWORD)
        for uid, org, email, role in (("usr_ada", "org_acme", "ada@acme.example", "admin"),
                                      ("usr_ben", "org_acme", "ben@acme.example", "member"),
                                      ("usr_cara", "org_other", "cara@other.example", "admin")):
            self.c.users.add(User(uid, org, email, uid[4:].title(), hashed, False, iso(NOW)))
            self.c.users.grant(uid, role)

    def cleanup(self):
        self._dir.cleanup()

    def call(self, method, target, token=None, body=None):
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        raw = json.dumps(body).encode() if body is not None else b""
        return self.c.app.handle(Request.build(method, target, headers, raw))

    def login(self, email, password=PASSWORD):
        return self.call("POST", "/login", body={"email": email, "password": password})

    def token(self, email):
        return self.login(email).body["session_token"]

    def reset_link_token(self) -> str:
        text = self.email.calls[-1].json()["text"]
        return re.search(r"token=(\S+)", text).group(1)
