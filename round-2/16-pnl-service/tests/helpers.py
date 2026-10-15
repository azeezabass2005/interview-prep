import os
import tempfile
from datetime import date

from pnl.api.handlers import PnlApi
from pnl.db import Database
from pnl.repositories.market import FillRepository, FxRepository, PriceRepository, SplitRepository
from pnl.services.pnl import PnlService


class World:
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.db = Database(os.path.join(self._dir.name, "pnl.db"))
        self.db.initialize()
        self.fills = FillRepository(self.db)
        self.prices = PriceRepository(self.db)
        self.splits = SplitRepository(self.db)
        self.fx = FxRepository(self.db)
        self.api = PnlApi(PnlService(self.db))

    def buy(self, qty, price, on, security="IBM", book="GEQ", currency="USD"):
        self.fills.add(book, security, currency, "BUY", qty, price, on)

    def sell(self, qty, price, on, security="IBM", book="GEQ", currency="USD"):
        self.fills.add(book, security, currency, "SELL", qty, price, on)

    def cleanup(self):
        self._dir.cleanup()


D = lambda m, d: date(2026, m, d)
