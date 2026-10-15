from dataclasses import dataclass, field

from ..errors import BoardError
from ..services.ranking import RankingService
from ..services.scoring import ScoreService


@dataclass
class Response:
    status: int
    body: dict = field(default_factory=dict)


def standing_json(s) -> dict:
    return {"rank": s.rank, "participant_id": s.participant_id, "name": s.name, "score": s.score}


class LeaderboardApi:
    def __init__(self, scoring: ScoreService, ranking: RankingService):
        self._scoring = scoring
        self._ranking = ranking

    def post_points(self, participant_id: str, body: dict) -> Response:
        try:
            return Response(200, {"total": self._scoring.add_points(participant_id, body.get("points"))})
        except BoardError as e:
            return Response(e.status, {"error": str(e)})

    def get_page(self, page: int = 1, size: int = 20) -> Response:
        return Response(200, {"standings": [standing_json(s) for s in self._ranking.page(page, size)]})

    def get_weekly(self) -> Response:
        return Response(200, {"standings": [standing_json(s) for s in self._ranking.weekly()]})
