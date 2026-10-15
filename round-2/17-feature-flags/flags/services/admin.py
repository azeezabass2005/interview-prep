from ..repositories.flags import FlagRepository


class FlagAdmin:
    def __init__(self, repo: FlagRepository, cache):
        self._repo = repo
        self._cache = cache

    def save_flag(self, key: str, enabled: bool = True, rollout_percent: int = 0) -> None:
        if not 0 <= rollout_percent <= 100:
            raise ValueError("rollout_percent must be 0-100")
        self._repo.upsert(key, enabled, rollout_percent)

    def override(self, key: str, user_id: str, value: bool) -> None:
        self._repo.set_override(key, user_id, value)

    def add_rule(self, key: str, position: int, attribute: str, equals: str, value: bool) -> None:
        self._repo.add_rule(key, position, attribute, equals, value)

    def archive(self, key: str) -> None:
        self._repo.archive(key)
