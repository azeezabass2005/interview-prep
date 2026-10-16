from collections import defaultdict
from typing import Dict, List, Optional

from .models import Account, Trade


class InMemoryStore:
    def __init__(self):
        self.accounts: Dict[str, Account] = {}
        self.trades: Dict[str, Trade] = {}
        self.trades_by_account: Dict[str, List[str]] = defaultdict(list)

    def add_account(self, account: Account) -> None:
        self.accounts[account.account_id] = account

    def account(self, account_id: str) -> Optional[Account]:
        return self.accounts.get(account_id)

    def add_trade(self, trade: Trade) -> None:
        self.trades[trade.trade_id] = trade
        self.trades_by_account[trade.account_id].append(trade.trade_id)

    def trade(self, trade_id: str) -> Optional[Trade]:
        return self.trades.get(trade_id)

    def trades_for(self, account_id: str) -> List[Trade]:
        return [self.trades[t] for t in self.trades_by_account.get(account_id, [])]
