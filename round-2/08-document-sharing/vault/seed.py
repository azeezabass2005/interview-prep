"""Demo users: python -m vault.seed"""
import os

from .clock import SystemClock
from .db import Database
from .ids import IdGenerator
from .wiring import build

if __name__ == "__main__":
    c = build(Database(os.environ.get("DB_PATH", "vault.db")), SystemClock(), IdGenerator())
    print("Nadia (deals team):", c.auth.issue("usr_nadia", "ws_ib", {"member"}))
    print("Tom (analyst):     ", c.auth.issue("usr_tom", "ws_ib", {"member"}))
