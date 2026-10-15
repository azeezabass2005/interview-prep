import os
import tempfile
from datetime import datetime, timezone

from alerts.api.handlers import AlertsApi
from alerts.clock import FakeClock
from alerts.db import Database
from alerts.models import User
from alerts.repositories.deliveries import DeliveryRepository
from alerts.repositories.users import UserRepository
from alerts.senders import RecordingSender
from alerts.services.alert_service import AlertService
from alerts.services.delivery import DeliveryWorker
from alerts.services.evaluator import Evaluator

# 15:00 UTC = 11:00 in New York (EDT) on this date
NOON_ISH = datetime(2026, 5, 12, 15, 0, tzinfo=timezone.utc)


class World:
    def __init__(self, now=NOON_ISH):
        self._dir = tempfile.TemporaryDirectory()
        self.db = Database(os.path.join(self._dir.name, "alerts.db"))
        self.db.initialize()
        self.clock = FakeClock(now)
        UserRepository(self.db).upsert(User("u1", "America/New_York", "22:00", "07:00"))
        self.service = AlertService(self.db, self.clock)
        self.api = AlertsApi(self.service)
        self.evaluator = Evaluator(self.db, self.clock)
        self.sender = RecordingSender()
        self.deliveries = DeliveryRepository(self.db)

    def worker(self, worker_id="w1"):
        return DeliveryWorker(self.db, self.clock, self.sender, worker_id)

    def cleanup(self):
        self._dir.cleanup()
