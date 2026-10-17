FIXES = [
    ("auction.py", "        if price > floor:", "        if price >= floor:"),
    ("auction.py", "        return second + increment(second)", "        return min(second + increment(second), ranked[0][1][0])"),
    ("auction.py", "key=lambda kv: (-kv[1][0], -kv[1][1])", "key=lambda kv: (-kv[1][0], kv[1][1])"),
    ("auction.py", "            item.closes_at = item.closes_at + SOFT_CLOSE", "            item.closes_at = at + SOFT_CLOSE"),
    ("auction.py", "        price = self.price(item_id)\n        premium",
     "        price = self.price(item_id)\n        if item.reserve is not None and price < item.reserve:\n            return None\n        premium"),
]
