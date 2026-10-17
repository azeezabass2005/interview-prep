from collections import defaultdict
from typing import Dict, List, Optional

from .models import ACTIVE, Draw, Entry, Participant, Settlement


class InMemoryStore:
    def __init__(self):
        self.participants: Dict[str, Participant] = {}
        self.participant_by_email: Dict[str, str] = {}
        self.draws: Dict[int, Draw] = {}
        self.entries: Dict[int, Entry] = {}
        self.entries_by_draw: Dict[int, List[int]] = defaultdict(list)
        self.entries_by_participant: Dict[str, List[int]] = defaultdict(list)
        self.settlements: Dict[int, Settlement] = {}
        self._next_entry_id = 1
        self._next_draw_id = 1

    def add_participant(self, participant: Participant) -> None:
        self.participants[participant.participant_id] = participant
        self.participant_by_email[participant.email.lower()] = participant.participant_id

    def participant(self, participant_id: str) -> Optional[Participant]:
        return self.participants.get(participant_id)

    def participant_id_for_email(self, email: str) -> Optional[str]:
        return self.participant_by_email.get(email.lower())

    def new_draw_id(self) -> int:
        draw_id = self._next_draw_id
        self._next_draw_id += 1
        return draw_id

    def save_draw(self, draw: Draw) -> None:
        self.draws[draw.draw_id] = draw

    def draw(self, draw_id: int) -> Optional[Draw]:
        return self.draws.get(draw_id)

    def latest_draw(self) -> Optional[Draw]:
        if not self.draws:
            return None
        return self.draws[max(self.draws)]

    def add_entry(self, draw_id: int, participant_id: str, code: str, at) -> Entry:
        entry = Entry(self._next_entry_id, draw_id, participant_id, code, ACTIVE, at)
        self._next_entry_id += 1
        self.entries[entry.entry_id] = entry
        self.entries_by_draw[draw_id].append(entry.entry_id)
        self.entries_by_participant[participant_id].append(entry.entry_id)
        return entry

    def entry(self, entry_id: int) -> Optional[Entry]:
        return self.entries.get(entry_id)

    def entries_for_draw(self, draw_id: int, active_only: bool = False) -> List[Entry]:
        result = [self.entries[i] for i in self.entries_by_draw.get(draw_id, [])]
        if active_only:
            result = [e for e in result if e.status == ACTIVE]
        return result

    def entries_for_participant(self, participant_id: str) -> List[Entry]:
        return [self.entries[i] for i in self.entries_by_participant.get(participant_id, [])]

    def save_settlement(self, settlement: Settlement) -> None:
        self.settlements[settlement.draw_id] = settlement

    def settlement(self, draw_id: int) -> Optional[Settlement]:
        return self.settlements.get(draw_id)
