from collections import defaultdict
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from .models import Account, DividendEvent, Enrolment, Payment


class InMemoryStore:
    def __init__(self):
        self.accounts: Dict[str, Account] = {}
        self.enrolments: Dict[Tuple[str, str], List[Enrolment]] = defaultdict(list)
        self.events: Dict[str, DividendEvent] = {}
        self.payments: Dict[str, List[Payment]] = defaultdict(list)
        self.leftovers: Dict[Tuple[str, str], Decimal] = {}

    def add_account(self, account: Account) -> None:
        self.accounts[account.account_id] = account

    def account(self, account_id: str) -> Optional[Account]:
        return self.accounts.get(account_id)

    def add_enrolment(self, e: Enrolment) -> None:
        history = self.enrolments[(e.account_id, e.security)]
        history.append(e)
        history.sort(key=lambda x: x.effective_from)

    def enrolment_history(self, account_id: str, security: str) -> List[Enrolment]:
        return list(self.enrolments.get((account_id, security), []))

    def add_event(self, event: DividendEvent) -> None:
        self.events[event.event_id] = event

    def save_payments(self, event_id: str, payments: List[Payment]) -> None:
        self.payments[event_id] = payments

    def leftover(self, account_id: str, security: str) -> Decimal:
        return self.leftovers.get((account_id, security), Decimal("0"))

    def set_leftover(self, account_id: str, security: str, amount: Decimal) -> None:
        self.leftovers[(account_id, security)] = amount
