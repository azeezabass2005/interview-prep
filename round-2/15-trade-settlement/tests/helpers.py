import os
import tempfile
from datetime import date
from decimal import Decimal

from settle.api.handlers import SettlementApi
from settle.db import Database
from settle.models import Confirm, Trade
from settle.repositories.trades import ConfirmRepository, TradeRepository


class World:
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.db = Database(os.path.join(self._dir.name, "settle.db"))
        self.db.initialize()
        self.trades = TradeRepository(self.db)
        self.confirms = ConfirmRepository(self.db)
        self.api = SettlementApi(self.db)

    def trade(self, trade_id, on, side="BUY", qty=100, price="101.25", asset="EQUITY", account="FUND1", security="IBM"):
        self.trades.add(Trade(trade_id, account, security, asset, side, qty, Decimal(price), on))

    def confirm(self, trade_id, price, side="BUY", qty=100, ref=None):
        self.confirms.add(Confirm(ref or f"BRK-{trade_id}", trade_id, side, qty, price))

    def cleanup(self):
        self._dir.cleanup()


MON, TUE, WED, THU, FRI = (date(2026, 6, 8), date(2026, 6, 9), date(2026, 6, 10), date(2026, 6, 11), date(2026, 6, 12))
