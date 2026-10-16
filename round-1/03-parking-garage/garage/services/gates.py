from ..errors import GarageFull, InvalidState, NotFound
from ..models import Ticket
from ..store import InMemoryStore
from .occupancy import Occupancy
from .passes import PassService
from .pricing import charge


class GateService:
    def __init__(self, store: InMemoryStore, passes: PassService, clock):
        self._store = store
        self._passes = passes
        self._occupancy = Occupancy(store)
        self._clock = clock

    def enter(self, plate: str) -> Ticket:
        if self._store.ticket_inside_for(plate):
            raise InvalidState(f"{plate} is already inside")
        now = self._clock.now()
        pass_holder = self._passes.has_valid_pass(plate, now.date())
        if not self._occupancy.can_admit(pass_holder):
            raise GarageFull("no spaces available")
        return self._store.open_ticket(plate, now, pass_holder)

    def validate(self, ticket_id: int) -> Ticket:
        ticket = self._get_inside(ticket_id)
        ticket.validated = True
        return ticket

    def quote(self, ticket_id: int, lost: bool = False) -> int:
        ticket = self._get_inside(ticket_id)
        return self._price(ticket, self._clock.now(), lost)

    def exit(self, ticket_id: int, lost: bool = False) -> Ticket:
        ticket = self._get_inside(ticket_id)
        now = self._clock.now()
        ticket.charge_cents = self._price(ticket, now, lost)
        ticket.exited_at = now
        self._store.close_ticket(ticket)
        return ticket

    def _price(self, ticket: Ticket, now, lost: bool) -> int:
        if ticket.pass_holder and now.weekday() < 5 and not lost:
            return 0
        return charge(ticket.entered_at, now, lost=lost, validated=ticket.validated)

    def _get_inside(self, ticket_id: int) -> Ticket:
        ticket = self._store.ticket(ticket_id)
        if ticket is None:
            raise NotFound(f"ticket {ticket_id}")
        if not ticket.inside:
            raise InvalidState(f"ticket {ticket_id} already closed")
        return ticket
