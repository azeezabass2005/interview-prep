import os
import tempfile
from datetime import datetime

from jobq.api.handlers import QueueApi
from jobq.clock import FakeClock
from jobq.db import Database
from jobq.handlers_registry import HandlerRegistry
from jobq.repositories.jobs import JobRepository
from jobq.services.queue import JobQueue
from jobq.services.worker import Worker


class World:
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.db = Database(os.path.join(self._dir.name, "jobs.db"))
        self.db.initialize()
        self.clock = FakeClock(datetime(2026, 5, 1, 12, 0, 0))
        self.queue = JobQueue(self.db, self.clock)
        self.api = QueueApi(self.queue)
        self.registry = HandlerRegistry()
        self.repo = JobRepository(self.db)

    def worker(self, name="w1", registry=None):
        return Worker(self.db, self.clock, registry or self.registry, name)

    def cleanup(self):
        self._dir.cleanup()


def always_fails(payload, ctx):
    raise RuntimeError("downstream unavailable")
