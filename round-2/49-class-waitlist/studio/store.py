from typing import Dict

from .models import Member, StudioClass


class InMemoryStore:
    def __init__(self):
        self.members: Dict[str, Member] = {}
        self.classes: Dict[str, StudioClass] = {}
