FIXES = [
    ("exchange/engine.py", "            level.popleft()\n            if resting.remaining > 0:\n                level.append(resting)\n",
     "            if resting.remaining == 0:\n                level.popleft()\n"),
    ("exchange/engine.py", "Trade(book.symbol, buy.order_id, sell.order_id, incoming.price, qty)",
     "Trade(book.symbol, buy.order_id, sell.order_id, resting.price, qty)"),
    ("exchange/engine.py", "        if order.remaining > 0:\n            book.side_for(order).add(order)\n",
     "        if order.remaining > 0:\n            if order.order_type == IOC:\n                order.status = CANCELLED\n"
     "            else:\n                book.side_for(order).add(order)\n"),
    ("exchange/engine.py", "        self.book(order.symbol).side_for(order).remove(order)\n        order.status = CANCELLED",
     "        side = self.book(order.symbol).side_for(order)\n        side.remove(order)\n"
     "        side.drop_level_if_empty(order.price)\n        order.status = CANCELLED"),
    ("exchange/engine.py", "        side = self.book(order.symbol).side_for(order)\n        side.remove(order)\n        side.drop_level_if_empty(order.price)\n        order.price, order.quantity",
     "        side = self.book(order.symbol).side_for(order)\n"
     "        if new_price == order.price and new_quantity <= order.quantity:\n"
     "            order.quantity = new_quantity\n            return order\n"
     "        side.remove(order)\n        side.drop_level_if_empty(order.price)\n        order.price, order.quantity"),
]
