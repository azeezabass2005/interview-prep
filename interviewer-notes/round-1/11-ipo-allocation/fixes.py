FIXES = [
    ("ipo.py", "(o.limit is None or o.limit > price)]", "(o.limit is None or o.limit >= price) and not o.cancelled]"),
    ("ipo.py", "                raise IpoError(\"bad size\")\n", "                raise IpoError(\"bad size\")\n            if shares > order.shares:\n                order.priority = self._tick()\n"),
    ("ipo.py", "        result = self._pro_rata(retail, retail_avail, 1)\n        result.update(self._pro_rata(institutional, inst_avail, 1))",
     "        retail_demand = sum(o.shares for o in retail)\n"
     "        inst_demand = sum(o.shares for o in institutional)\n"
     "        if retail_demand < retail_avail:\n"
     "            inst_avail += retail_avail - retail_demand\n"
     "        elif inst_demand < inst_avail:\n"
     "            retail_avail += inst_avail - inst_demand\n"
     "        result = self._pro_rata(retail, retail_avail, RETAIL_LOT)\n"
     "        result.update(self._pro_rata(institutional, inst_avail, 1))"),
]
