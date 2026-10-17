from datetime import date

from ..errors import GarageError
from ..models import Pass
from ..store import InMemoryStore


class PassService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def issue(self, plate: str, holder: str, valid_from: date, valid_to: date) -> Pass:
        if valid_to < valid_from:
            raise GarageError("pass ends before it starts")
        p = Pass(self._store.normalise(plate), holder, valid_from, valid_to)
        self._store.save_pass(p)
        return p

    def has_valid_pass(self, plate: str, day: date) -> bool:
        p = self._store.pass_for(plate)
        return p is not None and p.covers(day)
