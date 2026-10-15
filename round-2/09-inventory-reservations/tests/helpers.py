import os
import tempfile
from datetime import datetime

from stock.api.handlers import InventoryApi
from stock.clock import FakeClock
from stock.db import Database
from stock.repositories.reservations import ReservationRepository
from stock.repositories.skus import SkuRepository
from stock.services.reservations import ReservationService


class World:
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.db = Database(os.path.join(self._dir.name, "stock.db"))
        self.db.initialize()
        self.clock = FakeClock(datetime(2026, 11, 27, 9, 0))
        self.skus = SkuRepository(self.db)
        self.skus.add("KB-1", "Keyboard", 5, reorder_point=10)
        self.skus.add("DOCK", "Docking station", 9, reorder_point=20)
        self.skus.add("USBC", "USB-C cable", 7, reorder_point=30)
        self.skus.add("MOUSE", "Mouse", 40, reorder_point=15)
        self.skus.add_bundle("DESKKIT", "Desk Kit", {"DOCK": 1, "USBC": 2})
        self.api = InventoryApi(self.db, self.clock)
        self.reservations = ReservationRepository(self.db)

    def reservation_service(self):
        return ReservationService(self.db, self.clock)

    def cleanup(self):
        self._dir.cleanup()
