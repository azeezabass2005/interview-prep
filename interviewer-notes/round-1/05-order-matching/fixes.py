FIXES = [
    ("orderbook.py", "\"price\": order.price, \"quantity\": qty}", "\"price\": resting.price, \"quantity\": qty}"),
    ("orderbook.py", "setdefault(order.price, deque()).appendleft(order)", "setdefault(order.price, deque()).append(order)"),
    ("orderbook.py", "            if order.tif == \"IOC\" and order.remaining == order.quantity:", "            if order.tif == \"IOC\":"),
    ("orderbook.py", "        return price < order.price if order.side == \"BUY\" else price > order.price",
     "        return price <= order.price if order.side == \"BUY\" else price >= order.price"),
    ("orderbook.py", "            resting = queue[0]\n",
     "            resting = queue[0]\n"
     "            if resting.trader == order.trader:\n"
     "                queue.popleft()\n"
     "                resting.status = \"CANCELLED\"\n"
     "                if not queue:\n"
     "                    del opposite[best]\n"
     "                continue\n"),
]
