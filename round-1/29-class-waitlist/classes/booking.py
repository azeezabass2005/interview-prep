from datetime import timedelta
from decimal import Decimal
from typing import Dict, List

from .models import BOOKED, WAITLISTED, BookingError, ClassState, FitnessClass, Member

MAX_WAITLIST = 10
LATE_CANCEL_WINDOW = timedelta(hours=12)
PROMOTION_CUTOFF = timedelta(hours=1)
LATE_CANCEL_FEE = Decimal("10.00")


class BookingService:
    def __init__(self, clock):
        self._clock = clock
        self._state: Dict[str, ClassState] = {}

    def _get(self, cls: FitnessClass) -> ClassState:
        return self._state.setdefault(cls.class_id, ClassState())

    def roster(self, cls: FitnessClass) -> List[str]:
        return [m.member_id for m in self._get(cls).booked]

    def waitlist(self, cls: FitnessClass) -> List[str]:
        return [m.member_id for m in self._get(cls).waitlist]

    def book(self, cls: FitnessClass, member: Member) -> str:
        state = self._get(cls)
        if member in state.booked:
            raise BookingError(f"{member.member_id} already booked")
        if len(state.booked) < cls.capacity:
            state.booked.append(member)
            return BOOKED
        state.waitlist.append(member)
        return WAITLISTED

    def cancel(self, cls: FitnessClass, member: Member) -> Decimal:
        state = self._get(cls)
        time_left = cls.starts_at - self._clock.now()
        fee = LATE_CANCEL_FEE if time_left < LATE_CANCEL_WINDOW else Decimal("0.00")
        if member in state.booked:
            state.booked.remove(member)
            self._promote(cls, state)
        elif member in state.waitlist:
            state.waitlist.remove(member)
        else:
            raise BookingError(f"{member.member_id} has no place in {cls.class_id}")
        return fee

    def _promote(self, cls: FitnessClass, state: ClassState) -> None:
        if state.waitlist and len(state.booked) < cls.capacity:
            state.booked.append(state.waitlist[0])
