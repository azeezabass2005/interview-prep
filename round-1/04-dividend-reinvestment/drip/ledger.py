from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Dict


class Ledger:
    """Append-only record of share movements per account."""

    def __init__(self):
        self._moves = []  # (date, account_id, Decimal shares)

    def record(self, on: date, account_id: str, shares) -> None:
        self._moves.append((on, account_id, Decimal(shares)))

    def positions_as_of(self, on: date) -> Dict[str, Decimal]:
        totals = defaultdict(Decimal)
        for moved_on, account_id, shares in self._moves:
            if moved_on <= on:
                totals[account_id] += shares
        return dict(totals)

    def positions(self) -> Dict[str, Decimal]:
        totals = defaultdict(Decimal)
        for _, account_id, shares in self._moves:
            totals[account_id] += shares
        return dict(totals)
