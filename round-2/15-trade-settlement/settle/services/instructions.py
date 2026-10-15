from decimal import Decimal

from ..calendars import BusinessCalendar
from ..db import Database
from ..repositories.instructions import InstructionRepository
from ..repositories.trades import TradeRepository
from .netting import group_settle_date, netting_groups


class InstructionJob:
    """Nightly job: send netted settlement instructions for trades. Ops may re-run it after a failure."""

    def __init__(self, db: Database, calendar: BusinessCalendar = None):
        self._trades = TradeRepository(db)
        self._instructions = InstructionRepository(db)
        self._calendar = calendar or BusinessCalendar()

    def run(self) -> int:
        created = 0
        for (account, security), group in sorted(netting_groups(self._trades.all(), self._calendar).items()):
            net_qty = sum(t.signed_qty for t in group)
            net_cash = sum((-t.signed_qty * t.price for t in group), Decimal("0"))
            self._instructions.create(account, security, group_settle_date(group, self._calendar), net_qty, net_cash,
                                      [t.trade_id for t in group])
            created += 1
        return created
