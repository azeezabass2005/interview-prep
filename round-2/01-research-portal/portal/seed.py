"""Demo data for the web app: python -m portal.seed (prints a token per user)."""
import os

from .adapters.transport import UrllibTransport
from .clock import SystemClock
from .db import Database
from .ids import IdGenerator
from .models import Org, User
from .wiring import build

if __name__ == "__main__":
    c = build(Database(os.environ.get("DB_PATH", "portal.db")), SystemClock(), IdGenerator(), UrllibTransport())
    c.orgs.insert(Org("org_internal", "Research", "internal"))
    c.orgs.insert(Org("org_hartwell", "Hartwell Capital", "client"))
    c.users.insert(User("usr_ana", "org_internal", "ana@research.example", "Ana Analyst", False, None))
    c.users.insert(User("usr_hal", "org_hartwell", "hal@hartwell.example", "Hal Client", True, None))
    c.entitlements.add("sub_1", "org_hartwell", "energy", "2026-01-01", "2027-01-01")
    print("analyst:", c.auth.issue("usr_ana", "org_internal", {"analyst", "editor"}))
    print("client: ", c.auth.issue("usr_hal", "org_hartwell", {"reader"}))
