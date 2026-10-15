import contextlib
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS skus (
    sku            TEXT PRIMARY KEY,
    name           TEXT NOT NULL,
    on_hand        INTEGER NOT NULL DEFAULT 0,
    reserved       INTEGER NOT NULL DEFAULT 0,
    reorder_point  INTEGER NOT NULL DEFAULT 0,
    is_bundle      INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS bundle_components (
    bundle_sku     TEXT NOT NULL,
    component_sku  TEXT NOT NULL,
    qty            INTEGER NOT NULL,
    PRIMARY KEY (bundle_sku, component_sku)
);
CREATE TABLE IF NOT EXISTS reservations (
    reservation_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id         TEXT NOT NULL,
    sku             TEXT NOT NULL,
    qty             INTEGER NOT NULL,
    expires_at      TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'ACTIVE'
);
CREATE INDEX IF NOT EXISTS idx_res_cart ON reservations (cart_id, status);
CREATE INDEX IF NOT EXISTS idx_res_expiry ON reservations (status, expires_at);
"""


class Database:
    def __init__(self, path: str):
        self.path = path

    def initialize(self) -> None:
        with self.transaction() as conn:
            conn.executescript(SCHEMA)

    @contextlib.contextmanager
    def transaction(self):
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
