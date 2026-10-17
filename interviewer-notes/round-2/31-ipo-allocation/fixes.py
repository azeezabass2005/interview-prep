FIXES = [
    ("ipo/services/closing.py", "        live = [o for o in offering.orders.values() if o.status == ACTIVE]",
     "        live = [o for o in offering.orders.values() if o.status == ACTIVE and o.limit >= price]"),
    ("ipo/services/closing.py", "        institutional_tranche = offering.shares - retail_tranche\n",
     "        retail_demand = sum(o.shares for o in retail)\n"
     "        institutional_tranche = offering.shares - retail_tranche + max(0, retail_tranche - retail_demand)\n"),
    ("ipo/services/allocation.py", "    return int(round(shares / LOT_SIZE)) * LOT_SIZE", "    return int(shares // LOT_SIZE) * LOT_SIZE"),
    ("ipo/services/allocation.py", "key=lambda o: (o.shares - alloc[o.investor], o.seq))", "key=lambda o: (o.shares - alloc[o.investor], -o.seq))"),
    ("ipo/services/book.py", "        order.shares, order.limit = new_shares, new_limit\n",
     "        order.shares, order.limit = new_shares, new_limit\n        order.seq = self._store.next_seq()\n"),
]
