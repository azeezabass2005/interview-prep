from ..codes import CodeGenerator
from ..config import ENTRY_PRICE_CENTS, SEED_CENTS
from ..errors import InvalidState, NotFound
from ..models import CLOSED, OPEN, SETTLED, Draw, Settlement
from ..store import InMemoryStore
from .payouts import build_settlement


class DrawService:
    def __init__(self, store: InMemoryStore, codes: CodeGenerator, clock):
        self._store = store
        self._codes = codes
        self._clock = clock

    def open_draw(self) -> Draw:
        latest = self._store.latest_draw()
        carried_in = 0
        if latest is not None:
            if latest.status != SETTLED:
                raise InvalidState(f"draw {latest.number} is still {latest.status}")
            carried_in = self._store.settlement(latest.draw_id).rollover_cents
        number = latest.number + 1 if latest else 1
        draw = Draw(self._store.new_draw_id(), number, OPEN, carried_in, self._clock.now())
        self._store.save_draw(draw)
        return draw

    def current_open_draw(self) -> Draw:
        latest = self._store.latest_draw()
        if latest is None or latest.status != OPEN:
            raise InvalidState("no draw is open")
        return latest

    def get(self, draw_id: int) -> Draw:
        draw = self._store.draw(draw_id)
        if draw is None:
            raise NotFound(f"draw {draw_id}")
        return draw

    def pot_for(self, draw: Draw) -> int:
        entries = self._store.entries_for_draw(draw.draw_id)
        return SEED_CENTS + ENTRY_PRICE_CENTS * len(entries) + draw.carried_in_cents

    def close_draw(self, draw_id: int) -> Draw:
        draw = self.get(draw_id)
        if draw.status != OPEN:
            raise InvalidState(f"draw {draw.number} is {draw.status}")
        draw.pot_cents = self.pot_for(draw)
        draw.winning_code = self._codes.next_code()
        draw.entry_ids = tuple(e.entry_id for e in self._store.entries_for_draw(draw_id, active_only=True))
        draw.closed_at = self._clock.now()
        draw.status = CLOSED
        return draw

    def settle(self, draw_id: int) -> Settlement:
        draw = self.get(draw_id)
        if draw.status != CLOSED:
            raise InvalidState(f"draw {draw.number} is {draw.status}")
        entries = [self._store.entry(i) for i in draw.entry_ids]
        settlement = build_settlement(draw, entries)
        self._store.save_settlement(settlement)
        draw.status = SETTLED
        return settlement
