import os
import tempfile
from datetime import datetime, timedelta

from newsfeed.api.handlers import NewsApi
from newsfeed.clock import FakeClock
from newsfeed.db import Database
from newsfeed.repositories.stories import StoryRepository
from newsfeed.services.feed import FeedService
from newsfeed.services.ingest import IngestService

NOW = datetime(2026, 3, 18, 14, 0)


class World:
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.db = Database(os.path.join(self._dir.name, "news.db"))
        self.db.initialize()
        self.clock = FakeClock(NOW)
        self.api = NewsApi(IngestService(self.db), FeedService(self.db, self.clock))
        self.stories = StoryRepository(self.db)

    def post(self, n, minutes_ago=None, source="partner", tags=(), url=None):
        published = NOW - timedelta(minutes=minutes_ago if minutes_ago is not None else 100 - n)
        return self.api.post_story({"url": url or f"https://partner.example/s{n}", "headline": f"S{n}",
                                    "source": source, "published_at": published.isoformat(), "tags": list(tags)})

    def cleanup(self):
        self._dir.cleanup()
