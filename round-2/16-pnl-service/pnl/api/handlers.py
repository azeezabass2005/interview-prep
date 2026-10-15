from dataclasses import dataclass, field
from datetime import date

from ..errors import PnlError
from ..services.pnl import PnlService


@dataclass
class Response:
    status: int
    body: dict = field(default_factory=dict)


class PnlApi:
    def __init__(self, service: PnlService):
        self._service = service

    def get_positions(self, book: str, as_of: str) -> Response:
        try:
            rows = self._service.position_pnl(book, date.fromisoformat(as_of))
        except PnlError as e:
            return Response(e.status, {"error": str(e)})
        return Response(200, {sec: {k: str(v) for k, v in row.items()} for sec, row in rows.items()})

    def get_book_total(self, book: str, as_of: str) -> Response:
        try:
            return Response(200, {"book": book, "total_usd": str(self._service.book_total_usd(book, date.fromisoformat(as_of)))})
        except PnlError as e:
            return Response(e.status, {"error": str(e)})
