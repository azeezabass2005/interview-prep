from datetime import timedelta

from ..config import FRAUD_VELOCITY_MAX_WITHDRAWALS, FRAUD_VELOCITY_WINDOW_SECONDS
from ..repositories.entries import EntryRepository


class FraudMonitor:

    def __init__(self, entries: EntryRepository, clock):
        self._entries = entries
        self._clock = clock
        self.flags = []

    def after_withdrawal(self, account_id: str) -> None:
        since = self._clock.now() - timedelta(seconds=FRAUD_VELOCITY_WINDOW_SECONDS)
        if self._entries.withdrawals_since(account_id, since) > FRAUD_VELOCITY_MAX_WITHDRAWALS:
            self.flags.append(account_id)
