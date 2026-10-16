from typing import Dict, Optional

from .models import Account


class InMemoryStore:
    def __init__(self):
        self.accounts: Dict[str, Account] = {}

    def account(self, account_id: str) -> Optional[Account]:
        return self.accounts.get(account_id)
