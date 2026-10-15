FIXES = [
    ("classes/booking.py",
     "        if member in state.booked:\n            raise BookingError(f\"{member.member_id} already booked\")\n",
     "        if member in state.booked or member in state.waitlist:\n            raise BookingError(f\"{member.member_id} already has a place\")\n"),
    ("classes/booking.py",
     "        state.waitlist.append(member)\n        return WAITLISTED",
     "        if len(state.waitlist) >= MAX_WAITLIST:\n            raise BookingError(\"waitlist is full\")\n"
     "        position = len(state.waitlist)\n"
     "        if member.premium:\n"
     "            position = sum(1 for m in state.waitlist if m.premium)\n"
     "        state.waitlist.insert(position, member)\n        return WAITLISTED"),
    ("classes/booking.py",
     "        fee = LATE_CANCEL_FEE if time_left < LATE_CANCEL_WINDOW else Decimal(\"0.00\")\n        if member in state.booked:\n",
     "        fee = Decimal(\"0.00\")\n        if member in state.booked:\n"
     "            if time_left < LATE_CANCEL_WINDOW:\n                fee = LATE_CANCEL_FEE\n"),
    ("classes/booking.py",
     "        if state.waitlist and len(state.booked) < cls.capacity:\n            state.booked.append(state.waitlist[0])",
     "        if cls.starts_at - self._clock.now() < PROMOTION_CUTOFF:\n            return\n"
     "        if state.waitlist and len(state.booked) < cls.capacity:\n            state.booked.append(state.waitlist.pop(0))"),
]
