from ..db import Database
from ..errors import BoardError
from ..repositories.scores import ScoreRepository
from .weeks import week_start


class ScoreService:
    def __init__(self, db: Database, clock):
        self._scores = ScoreRepository(db)
        self._clock = clock

    def add_points(self, participant_id: str, points: int) -> int:
        if not isinstance(points, int) or abs(points) > 1_000_000:
            raise BoardError("points must be an integer within ±1,000,000")
        now = self._clock.now()
        self._scores.record_event(participant_id, points, now)
        current = self._scores.total(participant_id)
        self._scores.set_total(participant_id, current + points)
        self._scores.add_weekly(participant_id, week_start(now), points)
        return current + points
