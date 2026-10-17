from .errors import PotLuckError
from .services.draws import DrawService
from .services.entries import EntryService
from .services.participants import ParticipantService
from .services.statements import draw_summary, participant_statement
from .store import InMemoryStore


class PotLuckApi:
    def __init__(self, store: InMemoryStore, participants: ParticipantService, draws: DrawService,
                 entries: EntryService):
        self._store = store
        self._participants = participants
        self._draws = draws
        self._entries = entries

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except PotLuckError as exc:
            return exc.status, {"error": str(exc)}

    def register(self, body: dict):
        def go():
            p = self._participants.register(body.get("name"), body.get("email"))
            return {"participant_id": p.participant_id}
        return self._call(go, 201)

    def buy(self, participant_id: str, body: dict):
        def go():
            entries = self._entries.buy(participant_id, body.get("quantity", 1))
            return {"entries": [{"entry_id": e.entry_id, "code": e.code} for e in entries]}
        return self._call(go, 201)

    def cancel(self, participant_id: str, entry_id: int):
        return self._call(lambda: {"entry_id": self._entries.cancel(entry_id, participant_id).entry_id,
                                   "refund_cents": 500})

    def open_draw(self):
        return self._call(lambda: {"draw_id": self._draws.open_draw().draw_id}, 201)

    def close_draw(self, draw_id: int):
        def go():
            d = self._draws.close_draw(draw_id)
            return {"winning_code": d.winning_code, "pot_cents": d.pot_cents}
        return self._call(go)

    def settle_draw(self, draw_id: int):
        def go():
            s = self._draws.settle(draw_id)
            return {"awarded_cents": s.awarded_cents, "rollover_cents": s.rollover_cents,
                    "payouts": [{"entry_id": p.entry_id, "matches": p.matches, "amount_cents": p.amount_cents}
                                for p in s.payouts]}
        return self._call(go)

    def summary(self, draw_id: int):
        return self._call(lambda: draw_summary(self._store, self._draws.get(draw_id).draw_id))

    def statement(self, participant_id: str):
        def go():
            self._participants.get(participant_id)
            return participant_statement(self._store, participant_id)
        return self._call(go)
