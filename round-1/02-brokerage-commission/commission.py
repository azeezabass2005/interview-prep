from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

BANDS = [(300_000, Decimal("0.005")), (None, Decimal("0.003"))]
MIN_COMMISSION = Decimal("1.00")
MAX_PCT = Decimal("0.01")
OPTION_PER_CONTRACT = Decimal("0.65")
REG_FEE_RATE = Decimal("0.0000278")
CENT = Decimal("0.01")
KINDS = ("EQUITY", "OPTION")
SIDES = ("BUY", "SELL")


class FeeError(Exception):
    pass


@dataclass
class Trade:
    trade_id: str
    account: str
    kind: str
    side: str
    quantity: int
    price: Decimal
    month: str
    commission: Decimal = Decimal("0.00")
    reg_fee: Decimal = Decimal("0.00")
    busted: bool = False

    @property
    def value(self):
        multiplier = 100 if self.kind == "OPTION" else 1
        return self.quantity * self.price * multiplier


class FeeEngine:
    def __init__(self):
        self.trades = {}

    def _volume_before(self, account, month):
        return sum(t.quantity for t in self.trades.values() if t.kind == "EQUITY" and t.month == month)

    def _equity_commission(self, trade):
        done = self._volume_before(trade.account, trade.month)
        threshold, low_rate = BANDS[0]
        rate = low_rate if done < threshold else BANDS[1][1]
        raw = trade.quantity * rate
        cap = trade.value * MAX_PCT
        return max(min(raw, cap), MIN_COMMISSION).quantize(CENT, ROUND_HALF_UP)

    def _option_commission(self, trade):
        return max(trade.quantity * OPTION_PER_CONTRACT, MIN_COMMISSION).quantize(CENT, ROUND_HALF_UP)

    def _reg_fee(self, trade):
        if trade.side != "SELL":
            return Decimal("0.00")
        return (trade.value * REG_FEE_RATE).quantize(CENT, rounding=ROUND_HALF_UP)

    def book(self, trade_id, account, kind, side, quantity, price, trade_date):
        if trade_id in self.trades:
            raise FeeError("duplicate trade id")
        if kind not in KINDS or side not in SIDES:
            raise FeeError("bad kind or side")
        price = Decimal(str(price))
        if quantity <= 0 or price <= 0:
            raise FeeError("quantity and price must be positive")
        trade = Trade(trade_id, account, kind, side, quantity, price, trade_date[:7])
        if kind == "EQUITY":
            trade.commission = self._equity_commission(trade)
        else:
            trade.commission = self._option_commission(trade)
        trade.reg_fee = self._reg_fee(trade)
        self.trades[trade_id] = trade
        return trade

    def bust(self, trade_id):
        trade = self.trades.get(trade_id)
        if trade is None:
            raise FeeError("unknown trade")
        if trade.busted:
            raise FeeError("already busted")
        trade.busted = True
        return trade.commission + trade.reg_fee

    def statement(self, account, month):
        trades = [t for t in self.trades.values() if t.account == account and t.month == month and not t.busted]
        commission = sum((t.commission for t in trades), Decimal("0.00"))
        fees = sum((t.reg_fee for t in trades), Decimal("0.00"))
        return {"trades": len(trades), "commission": commission, "reg_fees": fees, "total": commission + fees}
