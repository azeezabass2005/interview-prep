SCHEMA = """
CREATE TABLE IF NOT EXISTS employees (
    id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    name TEXT NOT NULL,
    manager_id TEXT
);
CREATE TABLE IF NOT EXISTS reports (
    id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL REFERENCES employees(id),
    title TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('draft', 'submitted', 'approved', 'rejected')),
    submitted_at TEXT,
    decided_by TEXT,
    decided_at TEXT
);
CREATE TABLE IF NOT EXISTS expenses (
    id TEXT PRIMARY KEY,
    report_id TEXT NOT NULL REFERENCES reports(id),
    spent_on TEXT NOT NULL,
    merchant TEXT NOT NULL,
    category TEXT NOT NULL,
    amount_minor INTEGER NOT NULL,
    currency TEXT NOT NULL,
    usd_cents INTEGER NOT NULL,
    receipt_status TEXT NOT NULL DEFAULT 'none',
    receipt_total TEXT,
    receipt_error TEXT,
    deleted_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_expenses_report ON expenses (report_id);
CREATE TABLE IF NOT EXISTS receipts (
    expense_id TEXT PRIMARY KEY REFERENCES expenses(id),
    image_b64 TEXT NOT NULL
);
"""
