from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

CAPACITY = 100
RESERVED = 10
FREE_MINUTES = 15
HOURLY = Decimal("3.00")
DAILY_MAX = Decimal("20.00")
DAY_MINUTES = 24 * 60
VALIDATION_HOURS = 2
EXIT_GRACE = timedelta(minutes=15)


class GarageError(Exception):
    pass


@dataclass
class Ticket:
    ticket_id: int
    plate: str
    entered_at: datetime
    permit: bool
    validations: int = 0
    paid: Decimal = Decimal("0.00")
    paid_at: Optional[datetime] = None
    exited_at: Optional[datetime] = None


class Garage:
    def __init__(self, capacity=CAPACITY, reserved=RESERVED):
        self.capacity = capacity
        self.reserved = reserved
        self.tickets = {}

    @property
    def inside(self):
        return [t for t in self.tickets.values() if t.exited_at is None]

    def enter(self, plate, at, permit=False):
        if any(t.plate == plate for t in self.inside):
            raise GarageError("plate already inside")
        if len(self.inside) >= self.capacity:
            raise GarageError("garage full")
        ticket = Ticket(len(self.tickets) + 1, plate, at, permit)
        self.tickets[ticket.ticket_id] = ticket
        return ticket.ticket_id

    def _ticket(self, ticket_id):
        ticket = self.tickets.get(ticket_id)
        if ticket is None or ticket.exited_at is not None:
            raise GarageError("unknown ticket")
        return ticket

    def validate(self, ticket_id):
        ticket = self._ticket(ticket_id)
        ticket.validations += 1

    def _charge(self, minutes, validated):
        if minutes < FREE_MINUTES:
            return Decimal("0.00")
        days, rest = divmod(minutes, DAY_MINUTES)
        hours = -(-rest // 60)
        total = min(HOURLY * (days * 24 + hours), DAILY_MAX)
        if validated:
            total -= HOURLY * VALIDATION_HOURS
        return max(total, Decimal("0.00"))

    def amount_due(self, ticket_id, at):
        ticket = self._ticket(ticket_id)
        if ticket.permit:
            return Decimal("0.00")
        minutes = int((at - ticket.entered_at).total_seconds() // 60)
        return self._charge(minutes, ticket.validations > 0) - ticket.paid

    def pay(self, ticket_id, at):
        ticket = self._ticket(ticket_id)
        due = self.amount_due(ticket_id, at)
        ticket.paid += due
        ticket.paid_at = at
        return due

    def exit(self, ticket_id, at):
        ticket = self._ticket(ticket_id)
        due = self.amount_due(ticket_id, at)
        if due > 0:
            raise GarageError(f"please pay {due}")
        if ticket.paid_at is not None and at - ticket.paid_at > EXIT_GRACE:
            raise GarageError("exit grace expired, please pay again")
        ticket.exited_at = at
        return True
