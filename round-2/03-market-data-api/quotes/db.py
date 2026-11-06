import sqlite3
from contextlib import contextmanager

TRACKED = ("SELECT", "INSERT", "UPDATE", "DELETE")


class Database:
    """SQLite access shared by every repository. Each unit of work gets its own connection."""

    def __init__(self, path: str):
        self.path = path
        self.statements: list[str] = []

    def _trace(self, sql: str) -> None:
        if sql.lstrip().upper().startswith(TRACKED):
            self.statements.append(sql)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.set_trace_callback(self._trace)
        return conn

    @contextmanager
    def transaction(self):
        conn = self.connect()
        try:
            yield conn
            conn.commit()
        except BaseException:
            conn.rollback()
            raise
        finally:
            conn.close()

    def query(self, sql: str, params=()) -> list[sqlite3.Row]:
        conn = self.connect()
        try:
            return conn.execute(sql, params).fetchall()
        finally:
            conn.close()

    def query_one(self, sql: str, params=()):
        rows = self.query(sql, params)
        return rows[0] if rows else None

    def execute(self, sql: str, params=()) -> int:
        with self.transaction() as conn:
            return conn.execute(sql, params).rowcount

    def initialize(self, *schemas: str) -> None:
        conn = self.connect()
        try:
            for schema in schemas:
                conn.executescript(schema)
            conn.commit()
        finally:
            conn.close()
