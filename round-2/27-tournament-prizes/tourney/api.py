from .errors import TourneyError
from .services.play import PlayService
from .services.pool import prize_pool
from .services.registration import RegistrationService
from .services.results import compute_places, compute_prizes


class TourneyApi:
    def __init__(self, registration: RegistrationService, play: PlayService):
        self._reg = registration
        self._play = play

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except TourneyError as exc:
            return exc.status, {"error": str(exc)}

    def create(self, tournament_id: str):
        return self._call(lambda: {"tournament_id": self._reg.create(tournament_id).tournament_id}, 201)

    def enter(self, tournament_id: str, player: str):
        return self._call(lambda: {"entry_no": self._reg.enter(tournament_id, player).entry_no}, 201)

    def start(self, tournament_id: str):
        return self._call(lambda: {"level": self._reg.start(tournament_id).level})

    def next_level(self, tournament_id: str):
        return self._call(lambda: {"level": self._reg.next_level(tournament_id)})

    def eliminate(self, tournament_id: str, body: dict):
        return self._call(lambda: {"hand": self._play.eliminate(tournament_id, body["hand"], body["eliminated"],
                                                                body["winners"]).hand})

    def finish(self, tournament_id: str):
        def go():
            t = self._play.finish(tournament_id)
            return {"winner": t.winner, "pool_cents": prize_pool(len(t.entries)), "places": compute_places(t),
                    "prizes": compute_prizes(t), "bounties": dict(t.bounties)}
        return self._call(go)

    def pool(self, tournament_id: str):
        return self._call(lambda: {"pool_cents": prize_pool(len(self._reg.get(tournament_id).entries))})
