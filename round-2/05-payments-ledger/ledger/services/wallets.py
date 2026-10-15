from ..db import Database
from ..errors import AccountNotOpen, InsufficientFunds, NotFound
from ..models import OPEN, Account
from ..repositories.accounts import AccountRepository
from ..repositories.entries import EntryRepository
from .fraud import FraudMonitor
from .money import parse_amount


class WalletService:
    def __init__(self, db: Database, clock):
        self._accounts = AccountRepository(db)
        self._entries = EntryRepository(db)
        self._fraud = FraudMonitor(self._entries, clock)
        self._clock = clock

    def open_account(self, account_id: str, owner: str) -> Account:
        self._accounts.create(account_id, owner)
        return self._accounts.get(account_id)

    def close_account(self, account_id: str) -> None:
        self._open_account(account_id)
        self._accounts.set_status(account_id, "CLOSED")

    def get(self, account_id: str) -> Account:
        account = self._accounts.get(account_id)
        if account is None:
            raise NotFound(account_id)
        return account

    def _open_account(self, account_id: str) -> Account:
        account = self.get(account_id)
        if account.status != OPEN:
            raise AccountNotOpen(f"account {account_id} is not open")
        return account

    def deposit(self, account_id: str, amount, reference: str) -> Account:
        cents = parse_amount(amount)
        account = self._open_account(account_id)
        self._accounts.set_balance(account_id, account.balance_cents + cents)
        self._entries.insert(account_id, cents, "DEPOSIT", reference, self._clock.now())
        return self.get(account_id)

    def withdraw(self, account_id: str, amount, reference: str) -> Account:
        cents = parse_amount(amount)
        account = self._open_account(account_id)
        if account.balance_cents < cents:
            raise InsufficientFunds(f"balance {account.balance_cents} < {cents}")
        self._accounts.set_balance(account_id, account.balance_cents - cents)
        self._entries.insert(account_id, -cents, "WITHDRAWAL", reference, self._clock.now())
        self._fraud.after_withdrawal(account_id)
        return self.get(account_id)

    def transfer(self, source: str, target: str, amount, reference: str) -> None:
        if source == target:
            raise AccountNotOpen("cannot transfer to the same account")
        self.withdraw(source, amount, reference)
        self.deposit(target, amount, reference)
