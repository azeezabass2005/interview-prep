from typing import List, Tuple

from ..config import MAX_PAGE_SIZE
from ..db import Database
from ..models import Standing
from ..repositories.scores import ScoreRepository
from .weeks import week_start


def rank(rows: List[Tuple[str, str, int]]) -> List[Standing]:
    standings, rank_no, previous = [], 0, None
    for pid, name, score in rows:
        if score != previous:
            rank_no += 1
            previous = score
        standings.append(Standing(rank_no, pid, name, score))
    return standings


class RankingService:
    def __init__(self, db: Database, clock):
        self._scores = ScoreRepository(db)
        self._clock = clock

    def page(self, page: int, size: int) -> List[Standing]:
        size = max(1, min(size, MAX_PAGE_SIZE))
        rows = self._scores.all_time_page(size, (page - 1) * size)
        ranks = {s.participant_id: s.rank for s in rank(self._scores.all_time())}
        return [Standing(ranks[pid], pid, name, score) for pid, name, score in rows]

    def weekly(self) -> List[Standing]:
        return rank(self._scores.weekly(week_start(self._clock.now())))
