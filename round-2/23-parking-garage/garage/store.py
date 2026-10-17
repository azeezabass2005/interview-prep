import itertools
from typing import Dict, List, Optional

from .models import Pass, Ticket


class InMemoryStore:
    def __init__(self):
        self.passes: Dict[str, Pass] = {}
        self.tickets: Dict[int, Ticket] = {}
        self.inside_by_plate: Dict[str, int] = {}
        self._ids = itertools.count(1)

    def normalise(self, plate: str) -> str:
        return "".join(plate.split()).upper()

    def save_pass(self, p: Pass) -> None:
        self.passes[self.normalise(p.plate)] = p

    def pass_for(self, plate: str) -> Optional[Pass]:
        return self.passes.get(self.normalise(plate))

    def open_ticket(self, plate: str, at, pass_holder: bool) -> Ticket:
        ticket = Ticket(next(self._ids), self.normalise(plate), at, pass_holder)
        self.tickets[ticket.ticket_id] = ticket
        self.inside_by_plate[ticket.plate] = ticket.ticket_id
        return ticket

    def ticket(self, ticket_id: int) -> Optional[Ticket]:
        return self.tickets.get(ticket_id)

    def ticket_inside_for(self, plate: str) -> Optional[Ticket]:
        ticket_id = self.inside_by_plate.get(self.normalise(plate))
        return self.tickets.get(ticket_id) if ticket_id else None

    def close_ticket(self, ticket: Ticket) -> None:
        self.inside_by_plate.pop(ticket.plate, None)

    def inside(self) -> List[Ticket]:
        return [self.tickets[i] for i in self.inside_by_plate.values()]

    def closed_between(self, start, end) -> List[Ticket]:
        return [t for t in self.tickets.values() if t.exited_at and start <= t.exited_at < end]
