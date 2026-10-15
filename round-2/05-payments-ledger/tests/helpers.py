import os
import tempfile
from datetime import datetime

from ledger.api.handlers import WalletApi
from ledger.clock import FakeClock
from ledger.db import Database
from ledger.repositories.entries import EntryRepository
from ledger.services.statements import StatementService
from ledger.services.wallets import WalletService


class World:
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.db = Database(os.path.join(self._dir.name, "ledger.db"))
        self.db.initialize()
        self.clock = FakeClock(datetime(2026, 7, 1, 12, 0, 0))
        self.wallets = WalletService(self.db, self.clock)
        self.api = WalletApi(self.wallets, StatementService(self.db))
        self.entries = EntryRepository(self.db)

    def instance(self):
        """Another API instance sharing the same database."""
        return WalletService(self.db, self.clock)

    def cleanup(self):
        self._dir.cleanup()
