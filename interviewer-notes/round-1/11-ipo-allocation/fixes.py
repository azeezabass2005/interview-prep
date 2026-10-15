FIXES = [
    ("ipo/allocation.py", "    return int(round(shares / LOT_SIZE)) * LOT_SIZE", "    return int(shares // LOT_SIZE) * LOT_SIZE"),
    ("ipo/allocation.py", "for order in sorted(orders, key=lambda o: o.shares, reverse=True):", "for order in sorted(orders, key=lambda o: o.seq):"),
    ("ipo/allocation.py", "key=lambda o: (o.shares - alloc[o.investor], o.seq))", "key=lambda o: (o.shares - alloc[o.investor], -o.seq))"),
    ("ipo/book.py", "        if shares <= 0:\n            raise ValueError(\"order must be positive\")\n",
     "        if self.closed:\n            raise BookClosed(\"book is closed\")\n"
     "        if shares <= 0 or shares % LOT_SIZE:\n            raise ValueError(\"order must be a positive number of whole lots\")\n"),
]
