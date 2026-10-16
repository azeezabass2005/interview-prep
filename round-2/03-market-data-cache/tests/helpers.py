import os
import tempfile

from mdcache.api.handlers import MarketDataApi
from mdcache.cache import TtlCache
from mdcache.clock import FakeClock
from mdcache.config import CACHE_TTL_MS
from mdcache.db import Database
from mdcache.providers import ScriptedProvider
from mdcache.repositories.history import CloseRepository
from mdcache.services.consolidation import VenueBook
from mdcache.services.quotes import QuoteService


class World:

    def __init__(self, prices=None):
        self._dir = tempfile.TemporaryDirectory()
        self.db = Database(os.path.join(self._dir.name, "md.db"))
        self.db.initialize()
        self.clock = FakeClock()
        self.provider = ScriptedProvider(self.clock, prices or {"IBM": "180.00", "AAPL": "210.00"})
        self.closes = CloseRepository(self.db)
        self.service = QuoteService(self.provider, TtlCache(self.clock, CACHE_TTL_MS), self.closes)
        self.venues = VenueBook()
        self.api = MarketDataApi(self.service, self.venues, self.clock)

    def cleanup(self):
        self._dir.cleanup()
