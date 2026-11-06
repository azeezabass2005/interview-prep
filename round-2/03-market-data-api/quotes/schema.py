SCHEMA = """
CREATE TABLE IF NOT EXISTS customers (
    org_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    plan TEXT NOT NULL CHECK (plan IN ('basic', 'pro'))
);
CREATE TABLE IF NOT EXISTS instruments (
    symbol TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    exchange TEXT NOT NULL,
    currency TEXT NOT NULL,
    kind TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS daily_bars (
    symbol TEXT NOT NULL REFERENCES instruments(symbol),
    day TEXT NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume INTEGER NOT NULL,
    PRIMARY KEY (symbol, day)
);
"""
