from dataclasses import asdict

from ..http import Request, Response


def expense_json(e) -> dict:
    return {k: v for k, v in asdict(e).items() if k != "deleted_at"}


class Handlers:
    def __init__(self, reports):
        self._reports = reports

    def register(self, router) -> None:
        router.get("/health", lambda r: Response(200, {"status": "ok"}))
        router.get("/reports", self.mine)
        router.post("/reports", self.create)
        router.get("/reports/{report_id}", self.get)
        router.post("/reports/{report_id}/expenses", self.add_expense)
        router.post("/reports/{report_id}/submit", self.submit)
        router.post("/reports/{report_id}/approve", self.approve)
        router.post("/reports/{report_id}/reject", self.reject)
        router.patch("/expenses/{expense_id}", self.update_expense)
        router.delete("/expenses/{expense_id}", self.delete_expense)
        router.post("/expenses/{expense_id}/receipt", self.receipt)
        router.get("/team/reports", self.awaiting)

    def mine(self, request: Request) -> Response:
        return Response(200, {"reports": [asdict(r) for r in self._reports.mine(request.principal)]})

    def create(self, request: Request) -> Response:
        return Response(201, asdict(self._reports.create(request.principal, str(request.json().get("title", "")))))

    def get(self, request: Request) -> Response:
        data = self._reports.get(request.principal, request.params["report_id"])
        return Response(200, {**asdict(data["report"]), "expenses": [expense_json(e) for e in data["expenses"]],
                              "total_usd_cents": data["total_usd_cents"]})

    def add_expense(self, request: Request) -> Response:
        return Response(201, expense_json(self._reports.add_expense(request.principal, request.params["report_id"], request.json())))

    def update_expense(self, request: Request) -> Response:
        return Response(200, expense_json(self._reports.update_expense(request.principal, request.params["expense_id"],
                                                                       request.json())))

    def delete_expense(self, request: Request) -> Response:
        self._reports.delete_expense(request.principal, request.params["expense_id"])
        return Response(204)

    def receipt(self, request: Request) -> Response:
        self._reports.attach_receipt(request.principal, request.params["expense_id"], str(request.json().get("image", "")))
        return Response(202, {"status": "queued"})

    def submit(self, request: Request) -> Response:
        return Response(200, asdict(self._reports.submit(request.principal, request.params["report_id"])))

    def approve(self, request: Request) -> Response:
        return Response(200, asdict(self._reports.decide(request.principal, request.params["report_id"], True)))

    def reject(self, request: Request) -> Response:
        return Response(200, asdict(self._reports.decide(request.principal, request.params["report_id"], False)))

    def awaiting(self, request: Request) -> Response:
        return Response(200, {"reports": [asdict(r) for r in self._reports.awaiting_me(request.principal)]})
