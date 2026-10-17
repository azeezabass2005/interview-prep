from datetime import date

from ..errors import NotFound
from ..models import Enrolment
from ..store import InMemoryStore


class EnrolmentService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def set(self, account_id: str, security: str, enrolled: bool, effective_from: date) -> Enrolment:
        if self._store.account(account_id) is None:
            raise NotFound(f"account {account_id}")
        e = Enrolment(account_id, security, effective_from, enrolled)
        self._store.add_enrolment(e)
        return e

    def enrolled_on(self, account_id: str, security: str, on: date) -> bool:
        state = False
        for e in self._store.enrolment_history(account_id, security):
            if e.effective_from <= on:
                state = e.enrolled
        return state

    def currently_enrolled(self, account_id: str, security: str) -> bool:
        history = self._store.enrolment_history(account_id, security)
        return history[-1].enrolled if history else False
