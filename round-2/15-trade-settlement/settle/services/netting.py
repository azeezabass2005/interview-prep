from collections import defaultdict
from typing import Dict, List, Tuple

from ..calendars import BusinessCalendar
from ..models import Trade
from .settlement_dates import settlement_date


def netting_groups(trades: List[Trade], calendar: BusinessCalendar) -> Dict[Tuple, List[Trade]]:
    groups: Dict[Tuple, List[Trade]] = defaultdict(list)
    for t in trades:
        groups[(t.account, t.security)].append(t)
    return dict(groups)


def group_settle_date(group: List[Trade], calendar: BusinessCalendar):
    return max(settlement_date(t, calendar) for t in group)
