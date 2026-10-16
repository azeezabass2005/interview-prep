from datetime import datetime

from .errors import StudioError
from .models import StudioClass
from .services.booking import BookingService
from .services.members import MemberService


class StudioApi:
    def __init__(self, members: MemberService, booking: BookingService):
        self._members = members
        self._booking = booking

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except StudioError as exc:
            return exc.status, {"error": str(exc)}

    def join(self, member_id, plan, credits=0):
        return self._call(lambda: {"member_id": self._members.join(member_id, plan, credits).member_id}, 201)

    def add_class(self, class_id, starts_at, capacity):
        return self._call(lambda: {"class_id": self._booking.add_class(StudioClass(class_id, datetime.fromisoformat(starts_at), capacity)).class_id}, 201)

    def book(self, class_id, member_id):
        return self._call(lambda: {"status": self._booking.book(class_id, member_id)}, 201)

    def cancel(self, class_id, member_id):
        return self._call(lambda: self._booking.cancel(class_id, member_id))

    def roster(self, class_id):
        cls = self._booking._class(class_id)
        return 200, {"booked": list(cls.booked), "waitlist": list(cls.waitlist)}

    def member(self, member_id):
        m = self._members.get(member_id)
        return 200, {"credits": m.credits, "fees": str(m.fees)}
