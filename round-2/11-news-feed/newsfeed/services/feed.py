from typing import List, Optional

from ..config import DEFAULT_LIMIT, MAX_LIMIT
from ..db import Database
from ..models import Story
from ..repositories.stories import StoryRepository
from .ranking import score


class FeedService:
    def __init__(self, db: Database, clock):
        self._stories = StoryRepository(db)
        self._clock = clock

    def page(self, cursor: Optional[str] = None, limit: int = DEFAULT_LIMIT) -> dict:
        limit = max(1, min(limit, MAX_LIMIT))
        offset = int(cursor) if cursor else 0
        stories = self._stories.newest(limit, offset)
        next_cursor = str(offset + len(stories)) if len(stories) == limit else None
        return {"stories": stories, "next_cursor": next_cursor}

    def top(self, limit: int = 10, window_hours: int = 48) -> List[Story]:
        from datetime import timedelta
        now = self._clock.now()
        recent = self._stories.since(now - timedelta(hours=window_hours))
        return sorted(recent, key=lambda s: score(s, now), reverse=True)[:limit]

    def tagged(self, tag: str) -> List[Story]:
        return self._stories.with_tag(tag)
