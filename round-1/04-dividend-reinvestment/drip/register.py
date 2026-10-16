from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Dict, List

from .models import Movement


class ShareRegister:
    def __init__(self):
        self._movements: Dict[str, List[Movement]] = defaultdict(list)

    def record(self, movement: Movement) -> None:
        self._movements[movement.security].append(movement)

    def holdings(self, security: str, as_of: date) -> Dict[str, Decimal]:
        totals: Dict[str, Decimal] = defaultdict(Decimal)
        for m in self._movements.get(security, []):
            if m.on <= as_of:
                totals[m.account_id] += m.shares
        return dict(totals)

    def holding(self, account_id: str, security: str, as_of: date) -> Decimal:
        return self.holdings(security, as_of).get(account_id, Decimal("0"))

    def movements(self, security: str) -> List[Movement]:
        return list(self._movements.get(security, []))
