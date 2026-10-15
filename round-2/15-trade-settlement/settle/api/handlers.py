from dataclasses import dataclass, field

from ..calendars import BusinessCalendar
from ..repositories.instructions import InstructionRepository
from ..repositories.trades import ConfirmRepository, TradeRepository
from ..services.instructions import InstructionJob
from ..services.recon import reconcile
from ..services.settlement_dates import settlement_date


@dataclass
class Response:
    status: int
    body: dict = field(default_factory=dict)


class SettlementApi:
    def __init__(self, db, calendar: BusinessCalendar = None):
        self._calendar = calendar or BusinessCalendar()
        self._trades = TradeRepository(db)
        self._confirms = ConfirmRepository(db)
        self._instructions = InstructionRepository(db)
        self._job = InstructionJob(db, self._calendar)

    def get_settlement_date(self, trade_id: str) -> Response:
        trade = self._trades.get(trade_id)
        if trade is None:
            return Response(404, {"error": "unknown trade"})
        return Response(200, {"trade_id": trade_id, "settle_date": settlement_date(trade, self._calendar).isoformat()})

    def get_breaks(self) -> Response:
        return Response(200, {"breaks": reconcile(self._trades.all(), self._confirms.all())})

    def post_run_instructions(self) -> Response:
        return Response(200, {"created": self._job.run()})

    def get_instructions(self) -> Response:
        return Response(200, {"instructions": [
            {"account": i.account, "security": i.security, "settle_date": i.settle_date.isoformat(),
             "net_quantity": i.net_quantity, "net_cash": str(i.net_cash), "trades": list(i.trade_ids)}
            for i in self._instructions.all()]})
