from datetime import date, datetime

from .errors import TipsError
from .services.tips import TipService


class TipsApi:
    def __init__(self, service: TipService):
        self._service = service

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except TipsError as exc:
            return exc.status, {"error": str(exc)}

    def shift(self, body: dict):
        return self._call(lambda: {"ok": bool(self._service.record_shift(
            body["employee"], body["role"], datetime.fromisoformat(body["start"]), datetime.fromisoformat(body["end"])))}, 201)

    def declare(self, body: dict):
        return self._call(lambda: {"ok": bool(self._service.declare(date.fromisoformat(body["day"]), body["service"],
                                                                    body["card"], body["cash"]))}, 201)

    def distribute(self, day: str, service: str):
        return self._call(lambda: {k: str(v) for k, v in self._service.distribute(date.fromisoformat(day), service).items()})

    def statement(self, employee: str, monday: str):
        return self._call(lambda: self._service.weekly_statement(employee, date.fromisoformat(monday)))
