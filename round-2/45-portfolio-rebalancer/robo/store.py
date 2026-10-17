from typing import Dict

from .models import Account, Model


class InMemoryStore:
    def __init__(self):
        self.models: Dict[str, Model] = {}
        self.accounts: Dict[str, Account] = {}
        self.prices: Dict[str, object] = {}
