FIXES = [
    ("hotel.py", "range((check_out - check_in).days + 1)]", "range((check_out - check_in).days)]"),
    ("hotel.py", "WEEKEND_NIGHTS = (5, 6)", "WEEKEND_NIGHTS = (4, 5)"),
    ("hotel.py", "(check_in - booked_at.date()).days > ADVANCE_DAYS:", "(check_in - booked_at.date()).days >= ADVANCE_DAYS:"),
    ("hotel.py", "        if self._booked(room_type, nights[0]) >= self.inventory[room_type]:",
     "        if any(self._booked(room_type, n) >= self.inventory[room_type] for n in nights):"),
    ("hotel.py", "datetime.combine(r.check_in, time(0, 0))", "datetime.combine(r.check_in, CHECK_IN_TIME)"),
]
