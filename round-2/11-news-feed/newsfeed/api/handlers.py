from dataclasses import dataclass, field
from datetime import datetime

from ..errors import NewsError
from ..models import Story
from ..services.feed import FeedService
from ..services.ingest import IngestService


@dataclass
class Response:
    status: int
    body: dict = field(default_factory=dict)


def story_json(s: Story) -> dict:
    return {"story_id": s.story_id, "headline": s.headline, "url": s.original_url, "source": s.source,
            "published_at": s.published_at.isoformat(), "tags": list(s.tags)}


class NewsApi:
    def __init__(self, ingest: IngestService, feed: FeedService):
        self._ingest = ingest
        self._feed = feed

    def post_story(self, body: dict) -> Response:
        try:
            story_id = self._ingest.ingest(body["url"], body["headline"], body.get("source", "partner"),
                                           datetime.fromisoformat(body["published_at"]), body.get("tags", []))
        except NewsError as e:
            return Response(e.status, {"error": str(e)})
        if story_id is None:
            return Response(200, {"duplicate": True})
        return Response(201, {"story_id": story_id})

    def get_feed(self, cursor=None, limit=20) -> Response:
        page = self._feed.page(cursor, limit)
        return Response(200, {"stories": [story_json(s) for s in page["stories"]], "next_cursor": page["next_cursor"]})

    def get_top(self, limit=10) -> Response:
        return Response(200, {"stories": [story_json(s) for s in self._feed.top(limit)]})

    def get_tag(self, tag: str) -> Response:
        return Response(200, {"stories": [story_json(s) for s in self._feed.tagged(tag)]})
