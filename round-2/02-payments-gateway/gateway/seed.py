"""Demo merchant for the web app: python -m gateway.seed (prints an API token)."""
import os

from .adapters.transport import UrllibTransport
from .clock import SystemClock
from .db import Database
from .ids import IdGenerator
from .wiring import build

if __name__ == "__main__":
    c = build(Database(os.environ.get("DB_PATH", "gateway.db")), SystemClock(), IdGenerator(), UrllibTransport(), "whsec_dev")
    c.db.execute("INSERT OR IGNORE INTO merchants (id, name, country) VALUES ('mch_kyoto', 'Kyoto Tea House', 'JP')")
    c.db.execute("INSERT OR IGNORE INTO merchants (id, name, country) VALUES ('mch_bean', 'Bean & Co', 'US')")
    print("Kyoto Tea House:", c.auth.issue("usr_kyoto", "mch_kyoto", {"merchant"}))
    print("Bean & Co:      ", c.auth.issue("usr_bean", "mch_bean", {"merchant"}))
