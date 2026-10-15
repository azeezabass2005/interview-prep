from datetime import timedelta
from typing import Optional

from ..codes import generate_code
from ..db import Database
from ..errors import AliasTaken, NotFound
from ..models import Link
from ..repositories.links import LinkRepository
from .analytics import ClickRecorder
from .validation import validate_alias, validate_target


class LinkService:
    def __init__(self, db: Database, clock):
        self._links = LinkRepository(db)
        self._clicks = ClickRecorder(self._links, clock)
        self._clock = clock

    def create(self, owner: str, target_url: str, alias: Optional[str] = None,
               ttl_days: Optional[int] = None) -> Link:
        target_url = validate_target(target_url)
        now = self._clock.now()
        expires_at = now + timedelta(days=ttl_days) if ttl_days else None
        if alias is not None:
            code = validate_alias(alias)
            if self._links.get(code) is not None:
                raise AliasTaken(f"alias {alias} is taken")
        else:
            code = generate_code()
        link = Link(code, target_url, owner, now, expires_at, 0)
        self._links.save(link)
        return link

    def resolve(self, code: str, referrer: Optional[str] = None) -> str:
        link = self._links.lookup(code)
        if link is None:
            raise NotFound(code)
        self._clicks.record(link, referrer)
        return link.target_url

    def info(self, code: str) -> dict:
        link = self._links.lookup(code)
        if link is None:
            raise NotFound(code)
        return {"code": link.code, "target_url": link.target_url, "owner": link.owner, "clicks": link.clicks,
                "expires_at": link.expires_at.isoformat() if link.expires_at else None,
                "expired": link.is_expired(self._clock.now())}
