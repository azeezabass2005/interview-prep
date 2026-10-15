from typing import Optional

from ..models import Link
from ..repositories.links import LinkRepository


class ClickRecorder:
    def __init__(self, links: LinkRepository, clock):
        self._links = links
        self._clock = clock

    def record(self, link: Link, referrer: Optional[str]) -> None:
        self._links.add_click_event(link.code, self._clock.now(), referrer)
        self._links.set_clicks(link.code, link.clicks + 1)
