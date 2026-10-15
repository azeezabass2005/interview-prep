import os
import tempfile

from flags.app import Instance
from flags.clock import FakeClock
from flags.db import Database
from flags.models import User


class World:
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.db = Database(os.path.join(self._dir.name, "flags.db"))
        self.db.initialize()
        self.clock = FakeClock()

    def instance(self):
        return Instance(self.db, self.clock)

    def cleanup(self):
        self._dir.cleanup()


def user(uid, **attrs):
    return User(uid, attrs)
