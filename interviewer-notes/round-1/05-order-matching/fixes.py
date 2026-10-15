FIXES = [
    ("engine/book.py", "self._levels.setdefault(order.price, deque()).appendleft(order)",
     "self._levels.setdefault(order.price, deque()).append(order)"),
    ("engine/book.py", "        self._levels[order.price].remove(order)\n",
     "        level = self._levels[order.price]\n        level.remove(order)\n        if not level:\n            del self._levels[order.price]\n\n"
     "    def restore_front(self, order: Order) -> None:\n        self._levels.setdefault(order.price, deque()).appendleft(order)\n"),
    ("engine/matching.py", "fills.append(Fill(incoming.order_id, resting.order_id, incoming.price, qty))",
     "fills.append(Fill(incoming.order_id, resting.order_id, resting.price, qty))"),
    ("engine/matching.py", "                level.append(resting)\n", "                level.appendleft(resting)\n"),
    ("engine/matching.py", "        if not fills:\n            self.book.rest(incoming)\n",
     "        for order in reversed(skipped):\n            opposite.restore_front(order)\n"
     "        if incoming.remaining > 0:\n            self.book.rest(incoming)\n"),
    ("engine/matching.py", "        opposite = self.book.opposite_of(incoming)\n",
     "        opposite = self.book.opposite_of(incoming)\n        skipped: List[Order] = []\n"),
    ("engine/matching.py", "            resting = level.popleft()\n",
     "            resting = level.popleft()\n"
     "            if resting.trader == incoming.trader:\n"
     "                skipped.append(resting)\n"
     "                if not level:\n                    opposite.remove_level(best)\n"
     "                continue\n"),
]
