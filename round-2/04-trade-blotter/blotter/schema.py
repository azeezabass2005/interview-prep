SCHEMA = """
CREATE TABLE IF NOT EXISTS counterparties (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    lei TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS trades (
    id TEXT PRIMARY KEY,
    desk TEXT NOT NULL,
    trader_id TEXT NOT NULL,
    counterparty_id TEXT NOT NULL REFERENCES counterparties(id),
    symbol TEXT NOT NULL,
    side TEXT NOT NULL CHECK (side IN ('buy', 'sell')),
    quantity INTEGER NOT NULL,
    price_cents INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('live', 'cancelled')),
    trade_date TEXT NOT NULL,
    booked_at TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_trades_desk_date ON trades (desk, trade_date);
CREATE TABLE IF NOT EXISTS positions (
    desk TEXT NOT NULL,
    symbol TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    PRIMARY KEY (desk, symbol)
);
CREATE TABLE IF NOT EXISTS position_snapshots (
    desk TEXT NOT NULL,
    symbol TEXT NOT NULL,
    business_date TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    taken_at TEXT NOT NULL,
    PRIMARY KEY (desk, symbol, business_date)
);
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id TEXT NOT NULL,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    detail TEXT NOT NULL,
    at TEXT NOT NULL
);
"""
