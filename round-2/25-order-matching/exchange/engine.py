import itertools
from typing import Dict, List

from .book import OrderBook
from .errors import NotFound, Rejected
from .models import BUY, CANCELLED, FILLED, IOC, PARTIAL, Order, Trade
from .tape import TradeTape


class MatchingEngine:
    def __init__(self, tape: TradeTape = None):
        self.books: Dict[str, OrderBook] = {}
        self.orders: Dict[str, Order] = {}
        self.tape = tape or TradeTape()
        self._seq = itertools.count(1)

    def book(self, symbol: str) -> OrderBook:
        return self.books.setdefault(symbol, OrderBook(symbol))

    def submit(self, order: Order) -> List[Trade]:
        if order.order_id in self.orders:
            raise Rejected(f"duplicate order id {order.order_id}")
        order.seq = next(self._seq)
        self.orders[order.order_id] = order
        book = self.book(order.symbol)
        trades = self._match(book, order)
        if order.remaining > 0:
            book.side_for(order).add(order)
        return trades

    def _crosses(self, incoming: Order, price: int) -> bool:
        return price <= incoming.price if incoming.side == BUY else price >= incoming.price

    def _match(self, book: OrderBook, incoming: Order) -> List[Trade]:
        trades = []
        opposite = book.opposite(incoming)
        while incoming.remaining > 0:
            best = opposite.best_price()
            if best is None or not self._crosses(incoming, best):
                break
            level = opposite.levels[best]
            resting = level[0]
            qty = min(incoming.remaining, resting.remaining)
            buy, sell = (incoming, resting) if incoming.side == BUY else (resting, incoming)
            trade = Trade(book.symbol, buy.order_id, sell.order_id, incoming.price, qty)
            self.tape.publish(trade)
            trades.append(trade)
            for o in (incoming, resting):
                o.filled += qty
                o.status = FILLED if o.remaining == 0 else PARTIAL
            level.popleft()
            if resting.remaining > 0:
                level.append(resting)
            opposite.drop_level_if_empty(best)
        return trades

    def _live(self, order_id: str) -> Order:
        order = self.orders.get(order_id)
        if order is None or not order.is_live:
            raise NotFound(f"no live order {order_id}")
        return order

    def cancel(self, order_id: str) -> Order:
        order = self._live(order_id)
        self.book(order.symbol).side_for(order).remove(order)
        order.status = CANCELLED
        return order

    def amend(self, order_id: str, price: int = None, quantity: int = None) -> Order:
        order = self._live(order_id)
        new_price = order.price if price is None else price
        new_quantity = order.quantity if quantity is None else quantity
        if new_price <= 0 or new_quantity <= order.filled:
            raise Rejected("amended quantity must exceed the filled quantity")
        side = self.book(order.symbol).side_for(order)
        side.remove(order)
        side.drop_level_if_empty(order.price)
        order.price, order.quantity = new_price, new_quantity
        order.seq = next(self._seq)
        side.add(order)
        return order
