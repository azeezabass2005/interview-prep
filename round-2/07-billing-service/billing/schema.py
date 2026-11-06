SCHEMA = """
CREATE TABLE IF NOT EXISTS customers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    seats INTEGER NOT NULL,
    seat_price_cents INTEGER NOT NULL,
    active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS charges (
    id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES customers(id),
    description TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    invoice_id TEXT
);
CREATE TABLE IF NOT EXISTS usage_events (
    id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES customers(id),
    quantity INTEGER NOT NULL,
    occurred_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_usage_customer_time ON usage_events (customer_id, occurred_at);
CREATE TABLE IF NOT EXISTS invoices (
    id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES customers(id),
    period TEXT NOT NULL,
    subtotal_cents INTEGER NOT NULL,
    tax_cents INTEGER NOT NULL,
    total_cents INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('open', 'pending_tax', 'paid')),
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_invoices_customer_period ON invoices (customer_id, period);
CREATE TABLE IF NOT EXISTS invoice_lines (
    invoice_id TEXT NOT NULL REFERENCES invoices(id),
    position INTEGER NOT NULL,
    description TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    PRIMARY KEY (invoice_id, position)
);
CREATE TABLE IF NOT EXISTS payments (
    id TEXT PRIMARY KEY,
    invoice_id TEXT NOT NULL REFERENCES invoices(id),
    provider_payment_id TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    received_at TEXT NOT NULL
);
"""
