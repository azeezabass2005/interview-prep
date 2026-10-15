from dataclasses import dataclass, field

from ..errors import ExpenseError
from ..services.reports import ReportService
from ..services.workflow import ExpenseWorkflow


@dataclass
class Response:
    status: int
    body: dict = field(default_factory=dict)


class ExpensesApi:
    def __init__(self, workflow: ExpenseWorkflow, reports: ReportService):
        self._workflow = workflow
        self._reports = reports

    def _run(self, fn):
        try:
            return fn()
        except ExpenseError as e:
            return Response(e.status, {"error": str(e)})

    def post_expense(self, employee_id: str, body: dict) -> Response:
        return self._run(lambda: Response(201, {"expense_id": self._workflow.submit(
            employee_id, body.get("amount"), body.get("currency"), body.get("date"), body.get("description", ""))}))

    def post_approve(self, expense_id: int, approver_id: str) -> Response:
        return self._run(lambda: Response(200, {"status": self._workflow.approve(expense_id, approver_id)}))

    def get_expense(self, expense_id: int) -> Response:
        return self._run(lambda: Response(200, {"status": self._workflow.get(expense_id).status}))

    def get_team_report(self, team: str, year: int, month: int) -> Response:
        return Response(200, {"team": team, "total_usd": str(self._reports.team_month_total_usd(team, year, month))})
