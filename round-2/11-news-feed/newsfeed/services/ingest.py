from datetime import datetime
from typing import Optional

from ..db import Database
from ..errors import NewsError
from ..repositories.stories import StoryRepository
from .urls import canonical_url


class IngestService:
    def __init__(self, db: Database):
        self._stories = StoryRepository(db)

    def ingest(self, url: str, headline: str, source: str, published_at: datetime, tags=()) -> Optional[int]:
        if not url.lower().startswith(("http://", "https://")):
            raise NewsError("url must be http(s)")
        if not headline.strip():
            raise NewsError("headline required")
        return self._stories.insert(canonical_url(url), url, headline.strip(), source, published_at, list(tags))
