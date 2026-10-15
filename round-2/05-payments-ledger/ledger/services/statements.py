from typing import Optional

from ..config import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from ..db import Database
from ..repositories.entries import EntryRepository
from .money import format_cents


class StatementService:
    def __init__(self, db: Database):
        self._entries = EntryRepository(db)

    def page(self, account_id: str, cursor: Optional[str] = None, limit: int = DEFAULT_PAGE_SIZE) -> dict:
        limit = max(1, min(limit, MAX_PAGE_SIZE))
        entries = self._entries.page_after(account_id, cursor, limit)
        next_cursor = entries[-1].created_at.isoformat() if len(entries) == limit else None
        return {
            "entries": [{"entry_id": e.entry_id, "amount": format_cents(e.amount_cents), "kind": e.kind,
                         "reference": e.reference, "at": e.created_at.isoformat()} for e in entries],
            "next_cursor": next_cursor,
        }
