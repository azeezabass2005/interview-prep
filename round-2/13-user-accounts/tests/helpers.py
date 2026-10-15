import os
import tempfile
from datetime import datetime

from accounts.api.handlers import AccountsApi
from accounts.clock import FakeClock
from accounts.db import Database
from accounts.repositories.users import UserRepository

PW = "correct horse battery"


class World:
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.db = Database(os.path.join(self._dir.name, "accounts.db"))
        self.db.initialize()
        self.clock = FakeClock(datetime(2026, 2, 10, 9, 0))
        self.api = AccountsApi(self.db, self.clock)
        self.users = UserRepository(self.db)

    def signup(self, email="ann@example.com", name="Ann Lee", password=PW):
        return self.api.post_signup({"email": email, "name": name, "password": password})

    def login(self, email="ann@example.com", password=PW):
        return self.api.post_login({"email": email, "password": password})

    def cleanup(self):
        self._dir.cleanup()
