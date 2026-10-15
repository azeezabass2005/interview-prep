from datetime import date, timedelta

from ..calendars import BusinessCalendar
from ..config import SETTLEMENT_CYCLE
from ..errors import SettlementError
from ..models import Trade


def settlement_date(trade: Trade, calendar: BusinessCalendar) -> date:
    if trade.asset_class not in SETTLEMENT_CYCLE:
        raise SettlementError(f"unknown asset class {trade.asset_class}")
    days = SETTLEMENT_CYCLE[trade.asset_class]
    return calendar.roll_forward(trade.trade_date + timedelta(days=days))
