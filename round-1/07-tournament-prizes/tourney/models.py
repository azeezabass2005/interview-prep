from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

REGISTERING, RUNNING, FINISHED = "REGISTERING", "RUNNING", "FINISHED"


@dataclass
class Entry:
    entry_no: int
    player: str
    live: bool = True


@dataclass(frozen=True)
class Elimination:
    hand: int
    eliminated: Tuple[str, ...]
    winners: Tuple[str, ...]


@dataclass
class Tournament:
    tournament_id: str
    status: str = REGISTERING
    level: int = 0
    entries: List[Entry] = field(default_factory=list)
    eliminations: List[Elimination] = field(default_factory=list)
    bounties: Dict[str, int] = field(default_factory=dict)
    places: Dict[str, int] = field(default_factory=dict)
    prizes: Dict[str, int] = field(default_factory=dict)
    winner: Optional[str] = None

    def entries_for(self, player: str) -> List[Entry]:
        return [e for e in self.entries if e.player == player]

    def live_players(self) -> List[str]:
        return sorted({e.player for e in self.entries if e.live})
