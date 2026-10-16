from collections import defaultdict
from typing import Dict, List, Optional

from .models import Account, Call, Deposit, Price


class InMemoryStore:
    def __init__(self):
        self.securities: Dict[str, str] = {}
        self.prices: Dict[str, List[Price]] = defaultdict(list)
        self.accounts: Dict[str, Account] = {}
        self.calls: Dict[str, List[Call]] = defaultdict(list)
        self.deposits: Dict[str, List[Deposit]] = defaultdict(list)

    def account(self, account_id: str) -> Optional[Account]:
        return self.accounts.get(account_id)

    def open_call(self, account_id: str) -> Optional[Call]:
        return next((c for c in self.calls[account_id] if c.status == "OPEN"), None)
