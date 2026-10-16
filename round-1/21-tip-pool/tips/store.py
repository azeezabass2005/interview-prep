from typing import Dict, List, Tuple

from .models import Declaration, Shift


class InMemoryStore:
    def __init__(self):
        self.shifts: List[Shift] = []
        self.declarations: Dict[Tuple, Declaration] = {}
        self.payouts: Dict[Tuple, Dict[str, object]] = {}
