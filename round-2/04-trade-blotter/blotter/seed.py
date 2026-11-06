"""Demo counterparties and users: python -m blotter.seed"""
import os

from .clock import SystemClock
from .db import Database
from .ids import IdGenerator
from .models import Counterparty
from .wiring import build

if __name__ == "__main__":
    c = build(Database(os.environ.get("DB_PATH", "blotter.db")), SystemClock(), IdGenerator())
    for cp in (Counterparty("cp_gs", "Goldfinch Securities", "5493001KJTIIGC8Y1R12"),
               Counterparty("cp_ms", "Morrow Stanley", "IGJSJL3JD5P30I6NJZ34")):
        if c.counterparties.get(cp.id) is None:
            c.counterparties.add(cp)
    print("rates trader:   ", c.auth.issue("usr_rita", "rates", {"trader"}))
    print("rates desk head:", c.auth.issue("usr_ray", "rates", {"desk_head"}))
    print("fx trader:      ", c.auth.issue("usr_felix", "fx", {"trader"}))
    print("compliance:     ", c.auth.issue("usr_carla", "compliance", {"compliance"}))
