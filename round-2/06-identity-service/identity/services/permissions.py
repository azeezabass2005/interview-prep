from ..cache import TTLCache
from ..config import PERMISSION_CACHE_SECONDS, ROLE_PERMISSIONS
from ..errors import NotFound, ValidationError


class PermissionService:
    """A user's permissions come from their roles. They're read on every request, so they're cached for 10 minutes."""

    def __init__(self, users, clock):
        self._users = users
        self._cache = TTLCache(clock, PERMISSION_CACHE_SECONDS)

    def permissions(self, user_id: str) -> frozenset:
        cached = self._cache.get(user_id)
        if cached is not None:
            return cached
        perms = set()
        for role in self._users.roles(user_id):
            perms |= ROLE_PERMISSIONS.get(role, set())
        result = frozenset(perms)
        self._cache.set(user_id, result)
        return result

    def grant(self, user_id: str, role: str) -> None:
        self._check(user_id, role)
        self._users.grant(user_id, role)

    def revoke(self, user_id: str, role: str) -> None:
        self._check(user_id, role)
        self._users.revoke(user_id, role)

    def _check(self, user_id: str, role: str) -> None:
        if role not in ROLE_PERMISSIONS:
            raise ValidationError(f"unknown role {role}")
        if self._users.get(user_id) is None:
            raise NotFound("user not found")
