from dataclasses import dataclass
from datetime import datetime
from typing import Tuple


@dataclass(frozen=True)
class Story:
    story_id: int
    canonical_url: str
    original_url: str
    headline: str
    source: str
    published_at: datetime
    tags: Tuple[str, ...] = ()
