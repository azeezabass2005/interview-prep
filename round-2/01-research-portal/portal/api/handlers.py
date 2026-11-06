from ..errors import ValidationError
from ..http import Request, Response
from . import serializers


def _int(request: Request, name: str, default: int) -> int:
    try:
        return int(request.query.get(name, default))
    except ValueError as e:
        raise ValidationError(f"{name} must be an integer") from e


class ReportHandlers:
    def __init__(self, reports):
        self._reports = reports

    def register(self, router) -> None:
        router.get("/health", self.health)
        router.get("/reports", self.list_reports)
        router.post("/reports", self.create)
        router.get("/reports/{report_id}", self.get)
        router.get("/reports/{report_id}/pdf", self.pdf)
        router.get("/reports/{report_id}/stats", self.stats)
        router.post("/reports/{report_id}/publish", self.publish)
        router.post("/reports/{report_id}/withdraw", self.withdraw)

    def health(self, request: Request) -> Response:
        return Response(200, {"status": "ok"})

    def list_reports(self, request: Request) -> Response:
        result = self._reports.list_reports(request.principal, request.query.get("sector"), _int(request, "page", 1),
                                            _int(request, "page_size", 20))
        return Response(200, serializers.page(result))

    def get(self, request: Request) -> Response:
        return Response(200, serializers.report_full(self._reports.read_report(request.principal, request.params["report_id"])))

    def pdf(self, request: Request) -> Response:
        report = self._reports.read_report(request.principal, request.params["report_id"])
        return Response(200, {"filename": f"{report.id}.pdf", "content": f"{report.title}\n\n{report.body}"})

    def stats(self, request: Request) -> Response:
        return Response(200, self._reports.stats(request.principal, request.params["report_id"]))

    def create(self, request: Request) -> Response:
        data = request.json()
        report = self._reports.create_draft(request.principal, str(data.get("title", "")), str(data.get("sector", "")),
                                            str(data.get("summary", "")), str(data.get("body", "")))
        return Response(201, serializers.report_full(report))

    def publish(self, request: Request) -> Response:
        return Response(200, serializers.report_full(self._reports.publish(request.principal, request.params["report_id"])))

    def withdraw(self, request: Request) -> Response:
        return Response(200, serializers.report_full(self._reports.withdraw(request.principal, request.params["report_id"])))
