from datetime import date

from .errors import GarageError
from .services.gates import GateService
from .services.occupancy import Occupancy
from .services.passes import PassService


class GarageApi:
    def __init__(self, gates: GateService, passes: PassService, occupancy: Occupancy):
        self._gates = gates
        self._passes = passes
        self._occupancy = occupancy

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except GarageError as exc:
            return exc.status, {"error": str(exc)}

    def enter(self, plate: str):
        return self._call(lambda: {"ticket_id": self._gates.enter(plate).ticket_id}, 201)

    def validate(self, ticket_id: int):
        return self._call(lambda: {"ticket_id": self._gates.validate(ticket_id).ticket_id, "validated": True})

    def quote(self, ticket_id: int, lost: bool = False):
        return self._call(lambda: {"charge_cents": self._gates.quote(ticket_id, lost)})

    def exit(self, ticket_id: int, lost: bool = False):
        return self._call(lambda: {"charge_cents": self._gates.exit(ticket_id, lost).charge_cents})

    def issue_pass(self, body: dict):
        return self._call(lambda: {"plate": self._passes.issue(body["plate"], body["holder"],
                                                               date.fromisoformat(body["valid_from"]),
                                                               date.fromisoformat(body["valid_to"])).plate}, 201)

    def occupancy(self):
        return self._call(self._occupancy.counts)
