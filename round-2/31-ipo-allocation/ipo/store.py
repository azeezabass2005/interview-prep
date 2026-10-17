import itertools
from typing import Dict, Optional

from .models import Offering


class InMemoryStore:
    def __init__(self):
        self.offerings: Dict[str, Offering] = {}
        self._seq = itertools.count(1)

    def next_seq(self) -> int:
        return next(self._seq)

    def save(self, offering: Offering) -> None:
        self.offerings[offering.offering_id] = offering

    def get(self, offering_id: str) -> Optional[Offering]:
        return self.offerings.get(offering_id)
