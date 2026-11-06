"""Demo instruments and tokens: python -m quotes.seed"""
import os

from .adapters.transport import UrllibTransport
from .clock import SystemClock
from .db import Database
from .ids import IdGenerator
from .models import Instrument
from .wiring import build

INSTRUMENTS = [
    Instrument("AAPL", "Apple Inc", "XNAS", "USD", "equity"),
    Instrument("MSFT", "Microsoft Corp", "XNAS", "USD", "equity"),
    Instrument("ORLY", "O'Reilly Automotive Inc", "XNAS", "USD", "equity"),
    Instrument("VOD", "Vodafone Group PLC", "XLON", "GBP", "equity"),
    Instrument("SAP", "SAP SE", "XETR", "EUR", "equity"),
]

if __name__ == "__main__":
    c = build(Database(os.environ.get("DB_PATH", "quotes.db")), SystemClock(), IdGenerator(), UrllibTransport())
    for i in INSTRUMENTS:
        if c.instruments.get(i.symbol) is None:
            c.instruments.add(i)
    print("basic customer:", c.auth.issue("usr_basic", "org_alder", {"basic"}))
    print("pro customer:  ", c.auth.issue("usr_pro", "org_birch", {"pro"}))
    print("ops:           ", c.auth.issue("usr_ops", "org_internal", {"pro", "ops"}))
