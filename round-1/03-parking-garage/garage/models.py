from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass(frozen=True)
class Pass:
    plate: str
    holder: str
    valid_from: date
    valid_to: date

    def covers(self, day: date) -> bool:
        return self.valid_from <= day <= self.valid_to


@dataclass
class Ticket:
    ticket_id: int
    plate: str
    entered_at: datetime
    pass_holder: bool
    validated: bool = False
    exited_at: Optional[datetime] = None
    charge_cents: Optional[int] = None

    @property
    def inside(self) -> bool:
        return self.exited_at is None
