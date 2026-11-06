from datetime import date

from ..auth import Principal
from ..cache import TTLCache
from ..clock import iso
from ..config import CATEGORIES, CURRENCY_EXPONENT, FX_CACHE_SECONDS, MAX_REPORT_USD_CENTS
from ..errors import Conflict, Forbidden, NotFound, ValidationError
from ..models import EXPENSE_COLUMNS, Expense, Report

EDITABLE = set(EXPENSE_COLUMNS) - {"id"}


class ReportService:
    def __init__(self, employees, reports, expenses, fx, clock, ids, logger):
        self._employees = employees
        self._reports = reports
        self._expenses = expenses
        self._fx = fx
        self._clock = clock
        self._ids = ids
        self._logger = logger
        self._rates = TTLCache(clock, FX_CACHE_SECONDS)

    # --- reading -------------------------------------------------------------------------------------------------
    def _visible_report(self, principal: Principal, report_id: str) -> Report:
        report = self._reports.get(report_id)
        if report is None:
            raise NotFound("report not found")
        employee = self._employees.get(report.employee_id)
        if employee is None or employee.org_id != principal.org_id:
            raise NotFound("report not found")
        if report.employee_id == principal.user_id or principal.has_role("manager") or principal.has_role("finance"):
            return report
        raise NotFound("report not found")

    def _own_draft(self, principal: Principal, report_id: str) -> Report:
        report = self._visible_report(principal, report_id)
        if report.employee_id != principal.user_id:
            raise Forbidden("only the employee can change their report")
        if report.status != "draft":
            raise Conflict(f"the report is {report.status}; only drafts can be changed")
        return report

    def get(self, principal: Principal, report_id: str) -> dict:
        report = self._visible_report(principal, report_id)
        return {"report": report, "expenses": self._expenses.for_report(report.id),
                "total_usd_cents": self._reports.total_usd_cents(report.id)}

    def mine(self, principal: Principal) -> list[Report]:
        return self._reports.for_employee(principal.user_id)

    def awaiting_me(self, principal: Principal) -> list[Report]:
        return self._reports.awaiting(principal.user_id)

    # --- employee actions ----------------------------------------------------------------------------------------
    def create(self, principal: Principal, title: str) -> Report:
        if not title.strip():
            raise ValidationError("title is required")
        report = Report(self._ids.new("rep"), principal.user_id, title.strip(), "draft", None, None, None)
        self._reports.add(report)
        return report

    def _usd_cents(self, amount_minor: int, currency: str, spent_on: str) -> int:
        if currency == "USD":
            return amount_minor
        key = f"{currency}USD"
        rate = self._rates.get(key)
        if rate is None:
            rate = self._fx.rate(currency, "USD", spent_on)
            self._rates.set(key, rate)
        major = amount_minor / 10 ** CURRENCY_EXPONENT[currency]
        return round(major * rate * 100)

    def _validated(self, data: dict) -> dict:
        currency = str(data.get("currency", "USD")).upper()
        if currency not in CURRENCY_EXPONENT:
            raise ValidationError(f"unsupported currency {currency}")
        category = data.get("category", "other")
        if category not in CATEGORIES:
            raise ValidationError(f"category must be one of {', '.join(CATEGORIES)}")
        try:
            amount_minor = int(data["amount_minor"])
            spent_on = date.fromisoformat(str(data["spent_on"])).isoformat()
        except (KeyError, TypeError, ValueError) as e:
            raise ValidationError("amount_minor (integer) and spent_on (YYYY-MM-DD) are required") from e
        if amount_minor <= 0:
            raise ValidationError("amount must be positive")
        if spent_on > self._clock.now().date().isoformat():
            raise ValidationError("expenses can't be in the future")
        return {"currency": currency, "category": category, "amount_minor": amount_minor, "spent_on": spent_on,
                "merchant": str(data.get("merchant", "")).strip() or "Unknown"}

    def add_expense(self, principal: Principal, report_id: str, data: dict) -> Expense:
        report = self._own_draft(principal, report_id)
        v = self._validated(data)
        expense = Expense(self._ids.new("exp"), report.id, v["spent_on"], v["merchant"], v["category"], v["amount_minor"],
                          v["currency"], self._usd_cents(v["amount_minor"], v["currency"], v["spent_on"]), "none", None, None,
                          None)
        self._expenses.add(expense)
        return expense

    def update_expense(self, principal: Principal, expense_id: str, data: dict) -> Expense:
        expense = self._expenses.get(expense_id)
        if expense is None:
            raise NotFound("expense not found")
        self._own_draft(principal, expense.report_id)
        fields = {k: v for k, v in data.items() if k in EDITABLE}
        if {"amount_minor", "currency", "spent_on"} & fields.keys():
            merged = self._validated({**expense.__dict__, **fields})
            fields.update(merged)
            fields["usd_cents"] = self._usd_cents(merged["amount_minor"], merged["currency"], merged["spent_on"])
        if fields:
            self._expenses.update(expense.id, **fields)
        return self._expenses.get(expense.id)

    def delete_expense(self, principal: Principal, expense_id: str) -> None:
        expense = self._expenses.get(expense_id)
        if expense is None:
            raise NotFound("expense not found")
        self._own_draft(principal, expense.report_id)
        self._expenses.soft_delete(expense.id, iso(self._clock.now()))

    def attach_receipt(self, principal: Principal, expense_id: str, image_b64: str) -> None:
        expense = self._expenses.get(expense_id)
        if expense is None:
            raise NotFound("expense not found")
        self._own_draft(principal, expense.report_id)
        if not image_b64:
            raise ValidationError("image is required")
        self._expenses.attach_receipt(expense.id, image_b64)

    def submit(self, principal: Principal, report_id: str) -> Report:
        report = self._own_draft(principal, report_id)
        if not self._expenses.for_report(report.id):
            raise ValidationError("add at least one expense before submitting")
        if self._reports.total_usd_cents(report.id) > MAX_REPORT_USD_CENTS:
            raise ValidationError("reports over $25,000 must go through Finance")
        self._reports.set_status(report.id, "submitted", submitted_at=iso(self._clock.now()))
        return self._reports.get(report.id)

    # --- manager actions -----------------------------------------------------------------------------------------
    def decide(self, principal: Principal, report_id: str, approve: bool) -> Report:
        principal.require_role("manager")
        report = self._visible_report(principal, report_id)
        if report.employee_id == principal.user_id:
            raise Forbidden("you can't approve your own expenses")
        if report.status != "submitted":
            raise Conflict(f"the report is {report.status}")
        self._reports.set_status(report.id, "approved" if approve else "rejected", decided_by=principal.user_id,
                                 decided_at=iso(self._clock.now()))
        self._logger.info("report_decided", report_id=report.id, approved=approve, by=principal.user_id)
        return self._reports.get(report.id)
