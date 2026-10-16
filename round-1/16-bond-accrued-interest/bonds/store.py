from typing import Dict, List, Optional

from .models import Bond, Trade


class InMemoryStore:
    def __init__(self):
        self.bonds: Dict[str, Bond] = {}
        self.trades: List[Trade] = []

    def bond(self, bond_id: str) -> Optional[Bond]:
        return self.bonds.get(bond_id)
