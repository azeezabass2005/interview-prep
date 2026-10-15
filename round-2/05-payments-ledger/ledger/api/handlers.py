from dataclasses import dataclass, field

from ..errors import LedgerError
from ..services.money import format_cents
from ..services.statements import StatementService
from ..services.wallets import WalletService


@dataclass
class Response:
    status: int
    body: dict = field(default_factory=dict)


class WalletApi:
    def __init__(self, wallets: WalletService, statements: StatementService):
        self._wallets = wallets
        self._statements = statements

    def _account_body(self, account) -> dict:
        return {"account_id": account.account_id, "balance": format_cents(account.balance_cents),
                "status": account.status}

    def _run(self, fn):
        try:
            return fn()
        except LedgerError as e:
            return Response(e.status, {"error": str(e)})

    def get_account(self, account_id: str) -> Response:
        return self._run(lambda: Response(200, self._account_body(self._wallets.get(account_id))))

    def post_deposit(self, account_id: str, body: dict) -> Response:
        return self._run(lambda: Response(200, self._account_body(
            self._wallets.deposit(account_id, body.get("amount"), body.get("reference", "")))))

    def post_withdrawal(self, account_id: str, body: dict) -> Response:
        return self._run(lambda: Response(200, self._account_body(
            self._wallets.withdraw(account_id, body.get("amount"), body.get("reference", "")))))

    def post_transfer(self, body: dict) -> Response:
        def go():
            self._wallets.transfer(body["from"], body["to"], body.get("amount"), body.get("reference", ""))
            return Response(200, {"status": "ok"})
        return self._run(go)

    def get_statement(self, account_id: str, cursor=None, limit=50) -> Response:
        return Response(200, self._statements.page(account_id, cursor, limit))
