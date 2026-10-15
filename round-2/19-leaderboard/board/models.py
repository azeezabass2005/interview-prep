from dataclasses import dataclass


@dataclass(frozen=True)
class Standing:
    rank: int
    participant_id: str
    name: str
    score: int
