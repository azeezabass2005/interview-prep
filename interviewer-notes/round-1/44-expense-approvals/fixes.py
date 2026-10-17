FIXES = [
    ("expenses.py", "        if total >= MANAGER_ONLY:", "        if total > MANAGER_ONLY:"),
    ("expenses.py", "            if item.amount > RECEIPT_FROM and not item.receipt:", "            if item.amount >= RECEIPT_FROM and not item.receipt:"),
    ("expenses.py", "        return chain\n", "        return [a for a in chain if a != submitter]\n"),
    ("expenses.py", "        if report.status != \"SUBMITTED\" or approver not in report.chain or approver in report.approved_by:",
     "        if report.status != \"SUBMITTED\" or approver != self.pending_approver(report_id):"),
    ("expenses.py", "        report.chain = self._chain(report.submitter, report.total)\n        report.status = \"SUBMITTED\"",
     "        report.chain = self._chain(report.submitter, report.total)\n        report.approved_by = []\n        report.status = \"SUBMITTED\""),
]
