from .errors import FeeError
from .services.statements import StatementService
from .services.trades import TradeService


class FeeApi:
    def __init__(self, trades: TradeService, statements: StatementService):
        self._trades = trades
        self._statements = statements

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except FeeError as exc:
            return exc.status, {"error": str(exc)}

    def open_account(self, body: dict):
        return self._call(lambda: {"account_id": self._trades.open_account(body["account_id"], body.get("owner", "")).account_id}, 201)

    def post_trade(self, body: dict):
        return self._call(lambda: {"trade_id": self._trades.record(body).trade_id}, 201)

    def bust_trade(self, trade_id: str):
        return self._call(lambda: {"trade_id": self._trades.bust(trade_id).trade_id, "status": "BUSTED"})

    def statement(self, account_id: str, year: int, month: int):
        def go():
            s = self._statements.build(account_id, year, month)
            return {"lines": [{"trade_id": l.trade_id, "commission": str(l.commission), "discount": str(l.discount),
                               "reg_fee": str(l.reg_fee), "total": str(l.total)} for l in s.lines],
                    "total": str(s.total)}
        return self._call(go)
