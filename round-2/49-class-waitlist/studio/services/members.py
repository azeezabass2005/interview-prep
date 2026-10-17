from ..config import PLANS
from ..errors import NotFound, StudioError
from ..models import Member
from ..store import InMemoryStore


class MemberService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def join(self, member_id: str, plan: str, credits: int = 0) -> Member:
        if plan not in PLANS:
            raise StudioError(f"unknown plan {plan}")
        m = Member(member_id, plan, credits if plan == "PACK" else 0)
        self._store.members[member_id] = m
        return m

    def get(self, member_id: str) -> Member:
        m = self._store.members.get(member_id)
        if m is None:
            raise NotFound(member_id)
        return m

    def top_up(self, member_id: str, credits: int) -> Member:
        m = self.get(member_id)
        if m.plan != "PACK" or credits <= 0:
            raise StudioError("only PACK members can buy credits")
        m.credits += credits
        return m
