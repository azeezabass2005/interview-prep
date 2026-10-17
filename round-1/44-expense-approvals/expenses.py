import itertools
from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional

RECEIPT_FROM = Decimal("25.00")
LIMITS = {"MEALS": Decimal("75"), "HOTEL": Decimal("250"), "TAXI": Decimal("100")}
MANAGER_ONLY = Decimal("500")
CFO_ABOVE = Decimal("5000")


class ExpenseError(Exception):
    pass


@dataclass
class Item:
    category: str
    amount: Decimal
    receipt: bool = False
    justification: Optional[str] = None


@dataclass
class Report:
    report_id: int
    submitter: str
    items: List[Item]
    chain: List[str] = field(default_factory=list)
    approved_by: List[str] = field(default_factory=list)
    status: str = "SUBMITTED"

    @property
    def total(self):
        return sum((i.amount for i in self.items), Decimal("0"))


class Expenses:
    def __init__(self, managers, director, cfo):
        self.managers = dict(managers)
        self.director = director
        self.cfo = cfo
        self.reports = {}
        self._ids = itertools.count(1)

    def _validate(self, items):
        for item in items:
            if item.category not in LIMITS or item.amount <= 0:
                raise ExpenseError("bad item")
            if item.amount > RECEIPT_FROM and not item.receipt:
                raise ExpenseError("receipt required")
            if item.amount > LIMITS[item.category] and not item.justification:
                raise ExpenseError("justification required")

    def _chain(self, submitter, total):
        chain = [self.managers[submitter]]
        if total >= MANAGER_ONLY:
            chain.append(self.director)
        if total > CFO_ABOVE:
            chain.append(self.cfo)
        return chain

    def submit(self, submitter, items):
        self._validate(items)
        report = Report(next(self._ids), submitter, list(items))
        report.chain = self._chain(submitter, report.total)
        self.reports[report.report_id] = report
        return report

    def pending_approver(self, report_id):
        report = self.reports[report_id]
        remaining = [a for a in report.chain if a not in report.approved_by]
        return remaining[0] if remaining else None

    def approve(self, report_id, approver):
        report = self.reports[report_id]
        if report.status != "SUBMITTED" or approver not in report.chain or approver in report.approved_by:
            raise ExpenseError("not your step")
        report.approved_by.append(approver)
        if self.pending_approver(report_id) is None:
            report.status = "APPROVED"
        return report

    def reject(self, report_id, approver):
        report = self.reports[report_id]
        if report.status != "SUBMITTED" or approver != self.pending_approver(report_id):
            raise ExpenseError("not your step")
        report.status = "REJECTED"
        return report

    def resubmit(self, report_id, items):
        report = self.reports[report_id]
        if report.status != "REJECTED":
            raise ExpenseError("only rejected reports can be resubmitted")
        self._validate(items)
        report.items = list(items)
        report.chain = self._chain(report.submitter, report.total)
        report.status = "SUBMITTED"
        return report
