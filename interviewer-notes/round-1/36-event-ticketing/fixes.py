FIXES = [
    ("boxoffice.py", "        return {s for h in self.holds.values() for s in h.seats}",
     "        return {s for h in self.holds.values() if h.expires_at > now for s in h.seats}"),
    ("boxoffice.py", "        if len(seats) > MAX_PER_CUSTOMER:",
     "        bought = sum(len(o.seats) for o in self.orders.values() if o.customer == customer and not o.refunded)\n"
     "        held = sum(len(h.seats) for h in self.holds.values() if h.customer == customer and h.expires_at > now)\n"
     "        if bought + held + len(seats) > MAX_PER_CUSTOMER:"),
    ("boxoffice.py", "            if f\"{row}{n - 1}\" not in taken and f\"{row}{n - 2}\" in taken and n - 1 >= 1:\n                return True",
     "            if f\"{row}{n - 1}\" not in taken and f\"{row}{n - 2}\" in taken and n - 1 >= 1:\n                return True\n"
     "            if f\"{row}{n + 1}\" not in taken and f\"{row}{n + 2}\" in taken and n + 1 <= self.seats_per_row:\n                return True"),
    ("boxoffice.py", "        if row < last_row:", "        if row <= last_row:"),
    ("boxoffice.py", "        order.refunded = True\n        return order.total",
     "        order.refunded = True\n        return order.total - FEE * len(order.seats)"),
]
