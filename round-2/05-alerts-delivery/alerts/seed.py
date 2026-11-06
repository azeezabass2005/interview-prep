"""Demo users and tokens: python -m alerts.seed"""
import os

from .adapters.transport import UrllibTransport
from .clock import SystemClock
from .db import Database
from .ids import IdGenerator
from .models import User
from .wiring import build

if __name__ == "__main__":
    c = build(Database(os.environ.get("DB_PATH", "alerts.db")), SystemClock(), IdGenerator(), UrllibTransport(), UrllibTransport())
    if c.users.get("usr_maya") is None:
        c.users.add(User("usr_maya", "org_retail", "Maya", "maya@example.com", "+44 7700 900123"))
    print("Maya:      ", c.auth.issue("usr_maya", "org_retail", {"user"}))
    print("price feed:", c.auth.issue("svc_feed", "org_internal", {"feed"}))
