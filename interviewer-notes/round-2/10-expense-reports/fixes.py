FIXES = [
    ("expenses/services/reports.py",
     '''        if report.employee_id == principal.user_id:
            raise Forbidden("you can't approve your own expenses")''',
     '''        if report.employee_id == principal.user_id:
            raise Forbidden("you can't approve your own expenses")
        if self._employees.get(report.employee_id).manager_id != principal.user_id:
            raise Forbidden("only the employee's manager can approve or reject")'''),
    ("expenses/services/reports.py", '''        key = f"{currency}USD"''', '''        key = f"{currency}USD:{spent_on}"'''),
    ("expenses/services/receipts.py",
     '''        for row in batch:
            total = self._scanly.read_total(row["image_b64"])
            self._expenses.update(row["id"], receipt_status="done", receipt_total=total)''',
     '''        for row in batch:
            try:
                total = self._scanly.read_total(row["image_b64"])
            except ScanlyError as e:
                if e.retryable:
                    self._expenses.update(row["id"], receipt_status="queued")
                else:
                    self._expenses.update(row["id"], receipt_status="failed", receipt_error=str(e))
                self._logger.warning("receipt_failed", expense_id=row["id"], retryable=e.retryable, error=str(e))
                continue
            self._expenses.update(row["id"], receipt_status="done", receipt_total=total)'''),
    ("expenses/services/receipts.py", "from ..config import OCR_BATCH_SIZE\n",
     "from ..adapters.scanly import ScanlyError\nfrom ..config import OCR_BATCH_SIZE\n"),
    ("expenses/repositories/store.py",
     '''"SELECT COALESCE(SUM(usd_cents), 0) AS total FROM expenses WHERE report_id = ?"''',
     '''"SELECT COALESCE(SUM(usd_cents), 0) AS total FROM expenses WHERE report_id = ? AND deleted_at IS NULL"'''),
    ("expenses/services/reports.py", '''EDITABLE = set(EXPENSE_COLUMNS) - {"id"}''',
     '''EDITABLE = {"merchant", "category", "amount_minor", "currency", "spent_on"}'''),
    ("expenses/services/reports.py",
     '''        fields = {k: v for k, v in data.items() if k in EDITABLE}''',
     '''        if set(data) - EDITABLE:
            raise ValidationError(f"these fields can't be changed: {', '.join(sorted(set(data) - EDITABLE))}")
        fields = {k: v for k, v in data.items() if k in EDITABLE}'''),
]
GROUPS = [[0], [1], [2, 3], [4], [5, 6]]
