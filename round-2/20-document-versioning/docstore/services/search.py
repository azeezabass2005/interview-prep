from typing import List

from ..db import Database
from ..repositories.versions import VersionRepository


class SearchService:
    def __init__(self, db: Database):
        self._versions = VersionRepository(db)

    def search(self, text: str) -> List[int]:
        text = text.strip()
        if len(text) < 3:
            return []
        return self._versions.search(text)
