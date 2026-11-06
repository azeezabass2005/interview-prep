"""Demo customer and token: python -m billing.seed"""
import os

from .adapters.transport import UrllibTransport
from .clock import SystemClock
from .db import Database
from .ids import IdGenerator
from .wiring import build

if __name__ == "__main__":
    c = build(Database(os.environ.get("DB_PATH", "billing.db")), SystemClock(), IdGenerator(), UrllibTransport(), "pg_dev")
    if c.customers.get("cus_acme") is None:
        c.customers.add("cus_acme", "Acme Asset Management", "US", 10, 4_999)
    print("Acme billing admin:", c.auth.issue("usr_ann", "cus_acme", {"billing_admin"}))
