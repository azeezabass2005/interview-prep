import os
import tempfile
from datetime import datetime

from board.api.handlers import LeaderboardApi
from board.clock import FakeClock
from board.db import Database
from board.repositories.scores import ScoreRepository
from board.services.ranking import RankingService
from board.services.scoring import ScoreService

WEDNESDAY = datetime(2026, 6, 10, 15, 0)


class World:
    def __init__(self, now=WEDNESDAY):
        self._dir = tempfile.TemporaryDirectory()
        self.db = Database(os.path.join(self._dir.name, "board.db"))
        self.db.initialize()
        self.clock = FakeClock(now)
        self.scores = ScoreRepository(self.db)
        self.api = LeaderboardApi(ScoreService(self.db, self.clock), RankingService(self.db, self.clock))

    def people(self, *names):
        for name in names:
            self.scores.add_participant(name.lower(), name)

    def scoring(self):
        return ScoreService(self.db, self.clock)

    def cleanup(self):
        self._dir.cleanup()
