import itertools
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .pricing import parking_fee


@dataclass
class Ticket:
    ticket_id: int
    plate: str
    entered_at: datetime
    pass_holder: bool = False
    exited_at: Optional[datetime] = None
    charged_cents: Optional[int] = None


class Garage:
    def __init__(self, clock):
        self._clock = clock
        self._tickets = {}
        self._ids = itertools.count(1)

    def issue_ticket(self, plate: str, pass_holder: bool = False) -> Ticket:
        ticket = Ticket(next(self._ids), plate, self._clock.now(), pass_holder)
        self._tickets[ticket.ticket_id] = ticket
        return ticket

    def exit(self, ticket_id: int, lost_ticket: bool = False) -> int:
        ticket = self._tickets[ticket_id]
        now = self._clock.now()
        charge = parking_fee(ticket.entered_at, now,
                             pass_holder=ticket.pass_holder, lost_ticket=lost_ticket)
        ticket.exited_at = now
        ticket.charged_cents = charge
        return charge

    def open_tickets(self):
        return [t for t in self._tickets.values() if t.exited_at is None]
