from dataclasses import dataclass
from datetime import date

TIERS = ("BASE", "SILVER", "GOLD", "PLATINUM")


@dataclass(frozen=True)
class Member:
    member_id: str
    tier: str

    def __post_init__(self):
        if self.tier not in TIERS:
            raise ValueError(f"unknown tier {self.tier}")


@dataclass
class Lot:
    earned_on: date
    miles: int
    remaining: int


class InsufficientMiles(Exception):
    pass
