"""API client tokens: python -m edge.seed"""
import os

from .adapters.transport import UrllibTransport
from .clock import SystemClock
from .db import Database
from .ids import IdGenerator
from .wiring import build

if __name__ == "__main__":
    c = build(Database(os.environ.get("DB_PATH", "edge.db")), SystemClock(), IdGenerator(), UrllibTransport())
    print("client (Alder Partners):", c.auth.issue("svc_alder", "org_alder", {"client"}, ttl_hours=24 * 30))
    print("ops:                    ", c.auth.issue("usr_ops", "org_internal", {"ops"}, ttl_hours=24 * 30))
