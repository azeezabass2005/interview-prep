FIXES = [
    ("studio/services/booking.py", "        cls.waitlist.append(member_id)\n        return \"WAITLISTED\"",
     "        position = len(cls.waitlist)\n"
     "        if member.premium:\n"
     "            position = sum(1 for m in cls.waitlist if self._members.get(m).premium)\n"
     "        cls.waitlist.insert(position, member_id)\n        return \"WAITLISTED\""),
    ("studio/services/booking.py",
     "        if member.plan == \"PACK\":\n            member.credits += 1\n            result[\"credit_returned\"] = True\n        elif late:",
     "        if member.plan == \"PACK\":\n            if not late:\n                member.credits += 1\n                result[\"credit_returned\"] = True\n        elif late:"),
    ("studio/services/booking.py",
     """        if len(cls.booked) >= cls.capacity:
            return
        for member_id in cls.waitlist:
            member = self._members.get(member_id)
            if member.plan == "PACK":
                member.credits -= 1
            cls.booked.append(member_id)
            return""",
     """        if len(cls.booked) >= cls.capacity or cls.starts_at - self._clock.now() < PROMOTION_CUTOFF:
            return
        for member_id in cls.waitlist:
            member = self._members.get(member_id)
            if member.plan == "PACK":
                if member.credits < 1:
                    continue
                member.credits -= 1
            cls.waitlist.remove(member_id)
            cls.booked.append(member_id)
            return"""),
]
