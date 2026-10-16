import re
import uuid

from ..errors import NotFound, ValidationError
from ..models import Participant
from ..store import InMemoryStore

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ParticipantService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def register(self, name: str, email: str) -> Participant:
        name = (name or "").strip()
        email = (email or "").strip()
        if not name:
            raise ValidationError("name is required")
        if not _EMAIL.match(email):
            raise ValidationError("invalid e-mail")
        if self._store.participant_id_for_email(email):
            raise ValidationError("e-mail already registered")
        participant = Participant(f"p-{uuid.uuid4().hex[:8]}", name, email)
        self._store.add_participant(participant)
        return participant

    def get(self, participant_id: str) -> Participant:
        participant = self._store.participant(participant_id)
        if participant is None:
            raise NotFound(f"participant {participant_id}")
        return participant
