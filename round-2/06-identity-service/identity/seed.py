"""Demo accounts: python -m identity.seed (password for all: Correct-Horse-42)"""
import os

from .adapters.transport import UrllibTransport
from .clock import SystemClock, iso
from .db import Database
from .ids import IdGenerator
from .models import User
from .passwords import hash_password
from .wiring import build

if __name__ == "__main__":
    c = build(Database(os.environ.get("DB_PATH", "identity.db")), SystemClock(), IdGenerator(), UrllibTransport())
    for uid, email, role in (("usr_ada", "ada@acme.example", "admin"), ("usr_ben", "ben@acme.example", "member")):
        if c.users.get(uid) is None:
            c.users.add(User(uid, "org_acme", email, email.split("@")[0].title(), hash_password("Correct-Horse-42"), False,
                             iso(SystemClock().now())))
            c.users.grant(uid, role)
    print("Log in as ada@acme.example (admin) or ben@acme.example with password Correct-Horse-42")
