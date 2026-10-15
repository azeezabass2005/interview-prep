from decimal import ROUND_HALF_UP
from typing import Iterable

from .commission import commission_for, regulatory_fee
from .models import Statement, StatementLine, Trade
from .schedule import CENT, VOLUME_DISCOUNT_FROM_TRADE, VOLUME_DISCOUNT_RATE, ZERO


def build_statement(account: str, trades: Iterable[Trade]) -> Statement:
    """Build one account's monthly statement from that month's trades."""
    statement = Statement(account=account)
    account_trades = [t for t in trades if t.account == account]

    for i, trade in enumerate(account_trades):
        commission = commission_for(trade.notional)
        discount = ZERO
        if i > VOLUME_DISCOUNT_FROM_TRADE - 1:
            discount = (commission * VOLUME_DISCOUNT_RATE).quantize(CENT, rounding=ROUND_HALF_UP)
        statement.lines.append(
            StatementLine(
                trade_id=trade.trade_id,
                commission=commission,
                discount=discount,
                reg_fee=regulatory_fee(trade.side, trade.notional),
            )
        )
    return statement
