import os
import tempfile
from datetime import datetime

from shortlinks.api.handlers import LinkApi
from shortlinks.clock import FakeClock
from shortlinks.db import Database
from shortlinks.repositories.links import LinkRepository
from shortlinks.services.links import LinkService


class World:
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.db = Database(os.path.join(self._dir.name, "links.db"))
        self.db.initialize()
        self.clock = FakeClock(datetime(2026, 3, 1, 9, 0))
        self.service = LinkService(self.db, self.clock)
        self.api = LinkApi(self.service)
        self.repo = LinkRepository(self.db)

    def instance(self):
        return LinkService(self.db, self.clock)

    def cleanup(self):
        self._dir.cleanup()
