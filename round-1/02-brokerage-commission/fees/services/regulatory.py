from decimal import Decimal

from ..config import REG_FEE_RATE
from ..models import SELL, Trade
from ..money import ZERO, half_up
from .commission import notional


def regulatory_fee(trade: Trade) -> Decimal:
    if trade.side != SELL:
        return ZERO
    return half_up(notional(trade) * REG_FEE_RATE)
