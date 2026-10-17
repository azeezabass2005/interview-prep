from ..config import LATE_FEE, LATE_WINDOW, MAX_WAITLIST, PROMOTION_CUTOFF
from ..errors import NotFound, Refused
from ..models import StudioClass
from ..store import InMemoryStore
from .members import MemberService


class BookingService:
    def __init__(self, store: InMemoryStore, members: MemberService, clock):
        self._store = store
        self._members = members
        self._clock = clock

    def add_class(self, cls: StudioClass) -> StudioClass:
        self._store.classes[cls.class_id] = cls
        return cls

    def _class(self, class_id: str) -> StudioClass:
        cls = self._store.classes.get(class_id)
        if cls is None:
            raise NotFound(class_id)
        return cls

    def book(self, class_id: str, member_id: str) -> str:
        cls, member = self._class(class_id), self._members.get(member_id)
        if member_id in cls.booked or member_id in cls.waitlist:
            raise Refused("already has a place")
        if member.plan == "PACK" and member.credits < 1:
            raise Refused("no credits left")
        if len(cls.booked) < cls.capacity:
            if member.plan == "PACK":
                member.credits -= 1
            cls.booked.append(member_id)
            return "BOOKED"
        if len(cls.waitlist) >= MAX_WAITLIST:
            raise Refused("waitlist is full")
        cls.waitlist.append(member_id)
        return "WAITLISTED"

    def cancel(self, class_id: str, member_id: str) -> dict:
        cls, member = self._class(class_id), self._members.get(member_id)
        if member_id in cls.waitlist:
            cls.waitlist.remove(member_id)
            return {"fee": "0.00", "credit_returned": False}
        if member_id not in cls.booked:
            raise NotFound("no place to cancel")
        cls.booked.remove(member_id)
        late = cls.starts_at - self._clock.now() < LATE_WINDOW
        result = {"fee": "0.00", "credit_returned": False}
        if member.plan == "PACK":
            member.credits += 1
            result["credit_returned"] = True
        elif late:
            member.fees += LATE_FEE
            result["fee"] = str(LATE_FEE)
        self._promote(cls)
        return result

    def _promote(self, cls: StudioClass) -> None:
        if len(cls.booked) >= cls.capacity:
            return
        for member_id in cls.waitlist:
            member = self._members.get(member_id)
            if member.plan == "PACK":
                member.credits -= 1
            cls.booked.append(member_id)
            return
