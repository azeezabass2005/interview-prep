from ..cache import FlagCache
from ..models import User
from .bucketing import bucket


class Evaluator:
    def __init__(self, cache: FlagCache):
        self._cache = cache

    def is_enabled(self, flag_key: str, user: User, default: bool = False) -> bool:
        flag = self._cache.get(flag_key)
        if flag is None:
            return default
        if not flag.enabled:
            return False
        for rule in flag.rules:
            if user.attributes.get(rule.attribute) == rule.equals:
                return rule.value
        if user.user_id in flag.overrides:
            return flag.overrides[user.user_id]
        return bucket(flag.key, user.user_id) < flag.rollout_percent
