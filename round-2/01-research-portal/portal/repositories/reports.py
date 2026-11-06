from ..models import Report

COLUMNS = "id, title, sector, analyst_id, status, summary, body, created_at, published_at"


def _report(row) -> Report:
    return Report(*(row[c] for c in COLUMNS.split(", ")))


class ReportRepository:
    def __init__(self, db):
        self._db = db

    def insert(self, r: Report) -> None:
        self._db.execute(
            f"INSERT INTO reports ({COLUMNS}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (r.id, r.title, r.sector, r.analyst_id, r.status, r.summary, r.body, r.created_at, r.published_at),
        )

    def get(self, report_id: str) -> Report | None:
        row = self._db.query_one(f"SELECT {COLUMNS} FROM reports WHERE id = ?", (report_id,))
        return _report(row) if row else None

    def set_status(self, report_id: str, status: str, published_at: str | None) -> None:
        self._db.execute("UPDATE reports SET status = ?, published_at = ? WHERE id = ?", (status, published_at, report_id))

    def published(self, sectors: list[str], limit: int, offset: int) -> list[Report]:
        """Published reports in the given sectors, newest first."""
        if not sectors:
            return []
        marks = ", ".join("?" for _ in sectors)
        rows = self._db.query(
            f"SELECT {COLUMNS} FROM reports WHERE status = 'published' AND sector IN ({marks}) "
            "ORDER BY published_at DESC, id DESC LIMIT ? OFFSET ?",
            (*sectors, limit, offset),
        )
        return [_report(r) for r in rows]

    def published_since(self, sectors: list[str], since: str) -> list[Report]:
        if not sectors:
            return []
        marks = ", ".join("?" for _ in sectors)
        rows = self._db.query(
            f"SELECT {COLUMNS} FROM reports WHERE status = 'published' AND sector IN ({marks}) AND published_at > ? "
            "ORDER BY published_at DESC, id DESC",
            (*sectors, since),
        )
        return [_report(r) for r in rows]

    def record_read(self, report_id: str, user_id: str, at: str) -> None:
        self._db.execute("INSERT INTO report_reads (report_id, user_id, read_at) VALUES (?, ?, ?)", (report_id, user_id, at))

    def read_stats(self, report_id: str) -> dict:
        row = self._db.query_one(
            "SELECT COUNT(*) AS reads, COUNT(DISTINCT user_id) AS readers FROM report_reads WHERE report_id = ?", (report_id,)
        )
        return {"reads": row["reads"], "readers": row["readers"]}
