from ..errors import NotFound, ValidationError
from ..models import Group
from ..store import InMemoryStore


class GroupService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def create(self, group_id: str, name: str, members) -> Group:
        members = sorted({m.strip().lower() for m in members if m and m.strip()})
        if len(members) < 2:
            raise ValidationError("a group needs at least two members")
        if self._store.group(group_id):
            raise ValidationError("group exists")
        group = Group(group_id, name, members)
        self._store.save_group(group)
        return group

    def get(self, group_id: str) -> Group:
        group = self._store.group(group_id)
        if group is None:
            raise NotFound(f"group {group_id}")
        return group

    def require_members(self, group: Group, *names: str) -> None:
        for name in names:
            if name not in group.members:
                raise ValidationError(f"{name} is not in {group.name}")
