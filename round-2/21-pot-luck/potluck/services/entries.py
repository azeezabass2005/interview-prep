from typing import List

from ..codes import CodeGenerator
from ..config import MAX_ACTIVE_ENTRIES_PER_DRAW
from ..errors import InvalidState, LimitExceeded, NotFound, ValidationError
from ..models import ACTIVE, CANCELLED, OPEN, Entry
from ..store import InMemoryStore
from .draws import DrawService
from .participants import ParticipantService


class EntryService:
    def __init__(self, store: InMemoryStore, draws: DrawService, participants: ParticipantService,
                 codes: CodeGenerator, clock):
        self._store = store
        self._draws = draws
        self._participants = participants
        self._codes = codes
        self._clock = clock

    def active_count(self, participant_id: str) -> int:
        return sum(1 for e in self._store.entries_for_participant(participant_id) if e.status == ACTIVE)

    def buy(self, participant_id: str, quantity: int) -> List[Entry]:
        self._participants.get(participant_id)
        if not isinstance(quantity, int) or quantity < 1:
            raise ValidationError("quantity must be a positive integer")
        draw = self._draws.current_open_draw()
        if self.active_count(participant_id) + quantity > MAX_ACTIVE_ENTRIES_PER_DRAW:
            raise LimitExceeded(f"at most {MAX_ACTIVE_ENTRIES_PER_DRAW} active entries per draw")
        now = self._clock.now()
        return [self._store.add_entry(draw.draw_id, participant_id, self._codes.next_code(), now)
                for _ in range(quantity)]

    def cancel(self, entry_id: int, participant_id: str) -> Entry:
        entry = self._store.entry(entry_id)
        if entry is None or entry.participant_id != participant_id:
            raise NotFound(f"entry {entry_id}")
        if entry.status != ACTIVE:
            raise InvalidState("entry already cancelled")
        if self._draws.get(entry.draw_id).status != OPEN:
            raise InvalidState("draw is closed")
        entry.status = CANCELLED
        return entry
