import math
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, Set

DRIFT_BAND = Decimal("0.05")
CASH_BUFFER = Decimal("0.02")
MIN_TRADE = Decimal("100")


class RebalanceError(Exception):
    pass


@dataclass
class Account:
    cash: Decimal
    shares: Dict[str, int] = field(default_factory=dict)
    restricted: Set[str] = field(default_factory=set)


class Rebalancer:
    def __init__(self, prices):
        self.prices = {t: Decimal(str(p)) for t, p in prices.items()}

    @staticmethod
    def validate(model):
        model = {t: Decimal(str(w)) for t, w in model.items()}
        if sum(model.values()) != 1 or any(w < 0 for w in model.values()):
            raise RebalanceError("model weights must be non-negative and add up to 1")
        return model

    def _value(self, account, ticker):
        return account.shares.get(ticker, 0) * self.prices[ticker]

    def total(self, account):
        return account.cash + sum((self._value(account, t) for t in account.shares), Decimal("0"))

    def drift(self, account, model):
        total = self.total(account)
        tickers = set(model) | set(account.shares)
        return max(abs(self._value(account, t) / total - model.get(t, Decimal("0"))) for t in tickers)

    def plan(self, account, model):
        model = self.validate(model)
        if self.drift(account, model) < DRIFT_BAND:
            return []
        restricted_value = sum((self._value(account, t) for t in account.restricted), Decimal("0"))
        investable = self.total(account) - restricted_value
        weights = {t: w for t, w in model.items() if t not in account.restricted}
        trades = []
        for ticker in sorted(set(weights) | (set(account.shares) - account.restricted)):
            target = investable * weights.get(ticker, Decimal("0"))
            diff = target - self._value(account, ticker)
            shares = math.floor(diff / self.prices[ticker])
            if shares == 0 or abs(shares * self.prices[ticker]) < MIN_TRADE:
                continue
            trades.append((ticker, "BUY" if shares > 0 else "SELL", abs(shares)))
        return trades

    def weights(self, account):
        total = self.total(account)
        held = {t: self._value(account, t) / total for t in sorted(account.shares) if account.shares[t]}
        held["CASH"] = account.cash / total
        return held

    def execute(self, account, trades):
        for ticker, side, shares in trades:
            if ticker in account.restricted:
                raise RebalanceError(f"{ticker} is restricted")
            if side not in ("BUY", "SELL") or shares <= 0:
                raise RebalanceError("bad trade")
        for ticker, side, shares in trades:
            value = shares * self.prices[ticker]
            if side == "SELL":
                if account.shares.get(ticker, 0) < shares:
                    raise RebalanceError(f"not enough {ticker} to sell")
                account.shares[ticker] -= shares
                account.cash += value
            else:
                if account.cash < value:
                    raise RebalanceError("not enough cash")
                account.shares[ticker] = account.shares.get(ticker, 0) + shares
                account.cash -= value
        return account

    def rebalance(self, account, model):
        planned = self.plan(account, model)
        self.execute(account, planned)
        return planned
