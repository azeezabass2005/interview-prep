from typing import Optional

from ..db import Database


class TenantRepository:
    def __init__(self, db: Database):
        self._db = db

    def upsert(self, tenant_id: str, plan: str) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO tenants (tenant_id, plan) VALUES (?, ?) "
                         "ON CONFLICT (tenant_id) DO UPDATE SET plan = excluded.plan", (tenant_id, plan))

    def plan_for(self, tenant_id: str) -> Optional[str]:
        with self._db.transaction() as conn:
            row = conn.execute("SELECT plan FROM tenants WHERE tenant_id = ?", (tenant_id,)).fetchone()
        return row[0] if row else None
