from ..schema import SECTORS


class EntitlementRepository:
    """Which sectors an organisation may read, from its subscriptions. A subscription with no end date is open-ended."""

    def __init__(self, db):
        self._db = db

    def add(self, sub_id: str, org_id: str, sector: str, starts_on: str, ends_on: str | None = None) -> None:
        if sector not in SECTORS:
            raise ValueError(f"unknown sector {sector}")
        self._db.execute(
            "INSERT INTO subscriptions (id, org_id, sector, starts_on, ends_on) VALUES (?, ?, ?, ?, ?)",
            (sub_id, org_id, sector, starts_on, ends_on),
        )

    def sectors_for(self, org_id: str, on_date: str) -> set[str]:
        rows = self._db.query(
            "SELECT DISTINCT sector FROM subscriptions "
            "WHERE org_id = ? AND starts_on <= ? AND ends_on > ? OR ends_on IS NULL",
            (org_id, on_date, on_date),
        )
        return {r["sector"] for r in rows}
