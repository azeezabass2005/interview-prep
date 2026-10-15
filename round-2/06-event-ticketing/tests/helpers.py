import os
import tempfile
from datetime import datetime

from boxoffice.api.handlers import BoxOfficeApi
from boxoffice.clock import FakeClock
from boxoffice.db import Database
from boxoffice.models import Event
from boxoffice.repositories.events import EventRepository
from boxoffice.services.checkout import CheckoutService
from boxoffice.services.refunds import RefundService
from boxoffice.services.seating import SeatService

# Thursday 2026-09-10 20:00 in New York (= 2026-09-11 00:00 UTC)
SHOW = Event("ev1", "Riverside Jazz", "America/New_York", datetime(2026, 9, 10, 20, 0), 4500)
SEATS = ["A1", "A2", "A3", "B1", "B2", "B3"]


class World:
    def __init__(self, now=datetime(2026, 9, 1, 19, 0)):
        self._dir = tempfile.TemporaryDirectory()
        self.db = Database(os.path.join(self._dir.name, "box.db"))
        self.db.initialize()
        self.clock = FakeClock(now)
        EventRepository(self.db).add(SHOW, SEATS)
        self.seats = SeatService(self.db, self.clock)
        self.api = BoxOfficeApi(self.seats, CheckoutService(self.db, self.clock), RefundService(self.db, self.clock))

    def seat_service(self):
        """Another API instance."""
        return SeatService(self.db, self.clock)

    def cleanup(self):
        self._dir.cleanup()
