from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation

from ..config import SERVICES
from ..errors import TipsError
from ..models import Declaration, Shift
from ..store import InMemoryStore
from .distribution import shares
from .pools import pool_amount, weights


class TipService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def record_shift(self, employee: str, role: str, start: datetime, end: datetime) -> Shift:
        if end <= start:
            raise TipsError("shift must end after it starts")
        shift = Shift(employee.lower(), role, start, end)
        self._store.shifts.append(shift)
        return shift

    def declare(self, day: date, service: str, card, cash) -> Declaration:
        if service not in SERVICES:
            raise TipsError(f"unknown service {service}")
        try:
            d = Declaration(day, service, Decimal(str(card)), Decimal(str(cash)))
        except InvalidOperation:
            raise TipsError("amounts must be numbers")
        if d.card < 0 or d.cash < 0:
            raise TipsError("amounts cannot be negative")
        self._store.declarations[(day, service)] = d
        return d

    def distribute(self, day: date, service: str):
        d = self._store.declarations.get((day, service))
        if d is None:
            raise TipsError("no tips declared for that service")
        result = shares(pool_amount(d), weights(self._store.shifts, day, service))
        self._store.payouts[(day, service)] = result
        return result

    def weekly_statement(self, employee: str, monday: date) -> dict:
        employee = employee.lower()
        total, lines = Decimal("0.00"), []
        for (day, service), result in sorted(self._store.payouts.items()):
            if monday <= day < monday + timedelta(days=7) and employee in result:
                lines.append({"day": day.isoformat(), "service": service, "amount": str(result[employee])})
                total += result[employee]
        return {"employee": employee, "lines": lines, "total": str(total)}
