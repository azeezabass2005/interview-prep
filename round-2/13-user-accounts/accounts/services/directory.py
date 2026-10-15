from typing import List

from ..db import Database
from ..repositories.users import UserRepository


class DirectoryService:
    def __init__(self, db: Database):
        self._users = UserRepository(db)

    def search(self, query: str, limit: int = 20) -> List[dict]:
        if len(query.strip()) < 2:
            return []
        return [{"user_id": u.user_id, "display_name": u.display_name}
                for u in self._users.search_by_name(query.strip(), limit)]
