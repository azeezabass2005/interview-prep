from typing import Dict, List, Optional

from .models import Branch, Item, Loan, Patron


class InMemoryStore:
    def __init__(self):
        self.branches: Dict[str, Branch] = {}
        self.items: Dict[str, Item] = {}
        self.patrons: Dict[str, Patron] = {}
        self.loans: List[Loan] = []

    def open_loan(self, barcode: str) -> Optional[Loan]:
        return next((l for l in self.loans if l.barcode == barcode and l.returned_on is None), None)

    def loans_for(self, patron_id: str) -> List[Loan]:
        return [l for l in self.loans if l.patron == patron_id and l.returned_on is None]
