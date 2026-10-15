FIXES = [
    ("expenses/repositories/expenses.py",
     "    def set_status(self, expense_id: int, status: str) -> None:",
     "    def transition(self, expense_id: int, from_status: str, to_status: str) -> bool:\n"
     "        with self._db.transaction() as conn:\n"
     "            cur = conn.execute(\"UPDATE expenses SET status = ? WHERE expense_id = ? AND status = ?\",\n"
     "                               (to_status, expense_id, from_status))\n"
     "        return cur.rowcount == 1\n\n"
     "    def set_status(self, expense_id: int, status: str) -> None:"),
    ("expenses/services/workflow.py",
     "        if approver is None:\n            raise NotFound(approver_id)\n",
     "        if approver is None:\n            raise NotFound(approver_id)\n"
     "        if approver_id == expense.employee_id:\n            raise NotAllowed(\"you cannot approve your own expense\")\n"),
    ("expenses/services/workflow.py",
     "            needs_director = expense.amount > DIRECTOR_THRESHOLD_USD",
     "            usd = self._fx.to_usd(expense.amount, expense.currency, expense.expense_date)\n"
     "            needs_director = usd >= DIRECTOR_THRESHOLD_USD"),
    ("expenses/services/workflow.py",
     "        self._expenses.set_status(expense_id, new_status)\n        self._approvals.record(",
     "        if not self._expenses.transition(expense_id, expense.status, new_status):\n"
     "            raise InvalidState(\"expense was changed by someone else\")\n        self._approvals.record("),
    ("expenses/services/reports.py",
     "        return sum((e.amount for e in expenses), Decimal(\"0.00\"))",
     "        return sum((self._fx.to_usd(e.amount, e.currency, e.expense_date) for e in expenses), Decimal(\"0.00\"))"),
]
