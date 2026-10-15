from ..db import Database
from ..repositories.executions import ExecutionRepository


class PositionService:
    def __init__(self, db: Database):
        self._executions = ExecutionRepository(db)

    def position(self, account: str, symbol: str) -> int:
        return sum(self._executions.signed_quantities(account, symbol.upper()))
