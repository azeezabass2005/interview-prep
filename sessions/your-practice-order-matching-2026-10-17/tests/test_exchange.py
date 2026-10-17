import unittest
from unittest.mock import patch

from exchange.app import build_app
from exchange.book import BookSide
from exchange.errors import Rejected
from exchange.models import BUY, CANCELLED, FILLED, IOC, LIMIT, NEW, PARTIAL, SELL, Order


class TestExchange(unittest.TestCase):
    def test_simple_cross(self):
        # Verify that a matching buy order is accepted and fully filled.
        api, _ = build_app()
        api.submit("m1", {"order_id": "S1", "symbol": "ABC", "side": "SELL", "price": 100, "quantity": 10})
        status, body = api.submit("m2", {"order_id": "B1", "symbol": "ABC", "side": "BUY", "price": 100, "quantity": 10})
        self.assertEqual(status, 201)
        self.assertEqual(body["status"], "FILLED")

    def test_invalid_orders_are_rejected_before_book_add(self):
        # Verify invalid submissions are rejected without adding an order to the book.
        invalid_fields = [
            {"price": 0},
            {"price": -100},
            {"price": "invalid"},
            {"price": None},
            {"quantity": 0},
            {"quantity": -10},
            {"quantity": "invalid"},
            {"quantity": None},
            {"side": "INVALID"},
            {"symbol": "UNKNOWN"},
            {"type": "INVALID"},
        ]
        valid_body = {"order_id": "B1", "symbol": "ABC", "side": BUY,
                      "price": 100, "quantity": 10, "type": LIMIT}
        invalid_bodies = [dict(valid_body, **fields) for fields in invalid_fields]
        for field in ("symbol", "side", "price", "quantity"):
            body = valid_body.copy()
            del body[field]
            invalid_bodies.append(body)

        for body in invalid_bodies:
            with self.subTest(body=body):
                api, engine = build_app()
                with patch.object(BookSide, "add") as add:
                    status, response = api.submit("m1", body)
                self.assertEqual(status, 400)
                self.assertIn("error", response)
                add.assert_not_called()
                self.assertEqual(engine.orders, {})
                self.assertEqual(engine.books, {})

    def test_valid_order_is_created_and_added_to_book(self):
        # Verify valid submissions create Order instances on the appropriate book side.
        for side in (BUY, SELL):
            with self.subTest(side=side):
                api, engine = build_app()
                status, response = api.submit("m1", {
                    "order_id": "O1", "symbol": "ABC", "side": side,
                    "price": 100, "quantity": 10, "type": LIMIT,
                })
                self.assertEqual(status, 201)
                self.assertEqual(response, {"status": NEW, "filled": 0, "trades": []})
                order = engine.orders["O1"]
                self.assertIsInstance(order, Order)
                self.assertEqual(
                    (order.order_id, order.member, order.symbol, order.side,
                     order.price, order.quantity, order.order_type),
                    ("O1", "m1", "ABC", side, 100, 10, LIMIT),
                )
                self.assertEqual(order.remaining, 10)
                book = engine.book("ABC")
                self.assertEqual(list(book.side_for(order).levels[100]), [order])
                self.assertEqual(book.opposite(order).levels, {})

    def test_engine_rejects_unsupported_order_types(self):
        # Verify direct engine submissions reject unsupported types before changing state.
        for order_type in ("INVALID", "limit", "ioc", "", None):
            with self.subTest(order_type=order_type):
                _, engine = build_app()
                order = Order("B1", "m1", "ABC", BUY, 100, 10, order_type)
                with patch.object(BookSide, "add") as add:
                    with self.assertRaisesRegex(Rejected, "bad order type"):
                        engine.submit(order)
                add.assert_not_called()
                self.assertEqual(engine.orders, {})
                self.assertEqual(engine.books, {})
                self.assertEqual(engine.tape.trades, [])
                self.assertEqual(order.seq, 0)

    def test_order_type_defaults_to_limit(self):
        # Verify an omitted type defaults to LIMIT and leaves unmatched quantity resting.
        for side in (BUY, SELL):
            with self.subTest(side=side):
                api, engine = build_app()
                status, response = api.submit("m1", {
                    "order_id": "O1", "symbol": "ABC", "side": side,
                    "price": 100, "quantity": 10,
                })
                self.assertEqual(status, 201)
                self.assertEqual(response["status"], NEW)
                order = engine.orders["O1"]
                self.assertEqual(order.order_type, LIMIT)
                self.assertEqual(list(engine.book("ABC").side_for(order).levels[100]), [order])

    def test_order_types_match_multiple_orders_before_handling_remainder(self):
        # Verify LIMIT and IOC exhaust eligible resting orders before handling any remainder.
        for order_type in (LIMIT, IOC):
            for side in (BUY, SELL):
                with self.subTest(order_type=order_type, side=side):
                    api, engine = build_app()
                    opposite = SELL if side == BUY else BUY
                    for order_id in ("R1", "R2"):
                        api.submit("m1", {"order_id": order_id, "symbol": "ABC",
                                          "side": opposite, "price": 100, "quantity": 3})
                    status, response = api.submit("m2", {
                        "order_id": "I1", "symbol": "ABC", "side": side,
                        "price": 100, "quantity": 10, "type": order_type,
                    })
                    self.assertEqual(status, 201)
                    self.assertEqual(response["filled"], 6)
                    self.assertEqual(len(response["trades"]), 2)
                    self.assertEqual(engine.orders["R1"].status, FILLED)
                    self.assertEqual(engine.orders["R2"].status, FILLED)
                    order = engine.orders["I1"]
                    self.assertEqual(order.remaining, 4)
                    book_side = engine.book("ABC").side_for(order)
                    if order_type == LIMIT:
                        self.assertEqual(order.status, PARTIAL)
                        self.assertEqual(list(book_side.levels[100]), [order])
                    else:
                        self.assertEqual(order.status, CANCELLED)
                        self.assertFalse(order.is_live)
                        self.assertEqual(book_side.levels, {})

    def test_bookside_remove_preserves_other_orders(self):
        # Verify removing an order leaves other orders at the same price untouched.
        side = BookSide(is_bid=True)
        first = Order("B1", "m1", "ABC", BUY, 100, 10)
        second = Order("B2", "m2", "ABC", BUY, 100, 20)
        side.add(first)
        side.add(second)

        side.remove(first)

        self.assertEqual(list(side.levels[100]), [second])
        self.assertEqual(side.depth(1), [(100, 20)])

    def test_cancel_removes_order_from_book(self):
        # Verify cancellation removes a resting order and rejects repeat cancellation.
        api, engine = build_app()
        api.submit("m1", {"order_id": "B1", "symbol": "ABC", "side": BUY,
                          "price": 100, "quantity": 10})

        status, response = api.cancel("B1")

        self.assertEqual(status, 200)
        self.assertEqual(response, {"status": CANCELLED})
        order = engine.orders["B1"]
        self.assertFalse(order.is_live)
        self.assertFalse(any(order in level for level in engine.book("ABC").bids.levels.values()))
        status, response = api.cancel("B1")
        self.assertEqual(status, 404)
        self.assertIn("error", response)

    def test_best_price_returns_highest_bid_or_lowest_ask(self):
        # Verify BUY levels prefer the highest price and SELL levels prefer the lowest.
        for order_side, expected in ((BUY, 110), (SELL, 90)):
            with self.subTest(side=order_side):
                side = BookSide(is_bid=order_side == BUY)
                self.assertIsNone(side.best_price())
                for index, price in enumerate((100, 90, 110)):
                    side.add(Order(str(index), "m1", "ABC", order_side, price, 10))
                self.assertEqual(side.best_price(), expected)

    def test_matching_respects_buy_and_sell_price_limits(self):
        # Verify BUY orders accept equal or lower asks and SELL orders accept equal or higher bids.
        for incoming_side in (BUY, SELL):
            resting_side = SELL if incoming_side == BUY else BUY
            for resting_price in (90, 100, 110):
                with self.subTest(side=incoming_side, resting_price=resting_price):
                    api, engine = build_app()
                    api.submit("m1", {"order_id": "R1", "symbol": "ABC", "side": resting_side,
                                      "price": resting_price, "quantity": 10})
                    status, response = api.submit("m2", {
                        "order_id": "I1", "symbol": "ABC", "side": incoming_side,
                        "price": 100, "quantity": 10,
                    })
                    eligible = resting_price <= 100 if incoming_side == BUY else resting_price >= 100
                    self.assertEqual(status, 201)
                    self.assertEqual(response["status"], FILLED if eligible else NEW)
                    self.assertEqual(response["filled"], 10 if eligible else 0)
                    self.assertEqual(engine.orders["R1"].remaining, 0 if eligible else 10)

    def test_matching_prioritizes_best_price_before_arrival_time(self):
        # Verify incoming orders consume better prices before earlier arrivals at worse prices.
        for incoming_side in (BUY, SELL):
            for order_type in (LIMIT, IOC):
                with self.subTest(side=incoming_side, order_type=order_type):
                    api, engine = build_app()
                    resting_side = SELL if incoming_side == BUY else BUY
                    prices = (110, 90, 100) if incoming_side == BUY else (90, 110, 100)
                    for order_id, price in zip(("R1", "R2", "R3"), prices):
                        status, _ = api.submit("m1", {
                            "order_id": order_id, "symbol": "ABC", "side": resting_side,
                            "price": price, "quantity": 10,
                        })
                        self.assertEqual(status, 201)

                    status, response = api.submit("m2", {
                        "order_id": "I1", "symbol": "ABC", "side": incoming_side,
                        "price": 110 if incoming_side == BUY else 90,
                        "quantity": 25, "type": order_type,
                    })

                    self.assertEqual(status, 201)
                    self.assertEqual(response["status"], FILLED)
                    resting_key = "sell" if incoming_side == BUY else "buy"
                    self.assertEqual(
                        [(trade[resting_key], trade["quantity"]) for trade in response["trades"]],
                        [("R2", 10), ("R3", 10), ("R1", 5)],
                    )
                    self.assertEqual(
                        [trade["price"] for trade in response["trades"]],
                        [prices[1], prices[2], prices[0]],
                    )
                    self.assertEqual(
                        [trade.price for trade in engine.tape.trades],
                        [prices[1], prices[2], prices[0]],
                    )
                    self.assertEqual(engine.orders["R2"].status, FILLED)
                    self.assertEqual(engine.orders["R3"].status, FILLED)
                    self.assertEqual(engine.orders["R1"].status, PARTIAL)
                    self.assertEqual(engine.orders["R1"].remaining, 5)

    def test_matching_skips_empty_levels_after_cancellation(self):
        # Verify a cancelled price level cannot block matching against remaining liquidity.
        for incoming_side in (BUY, SELL):
            for order_type in (LIMIT, IOC):
                for has_remaining_order in (False, True):
                    with self.subTest(side=incoming_side, order_type=order_type,
                                      has_remaining_order=has_remaining_order):
                        api, engine = build_app()
                        resting_side = SELL if incoming_side == BUY else BUY
                        best_price = 90 if incoming_side == BUY else 110
                        status, _ = api.submit("m1", {
                            "order_id": "R1", "symbol": "ABC", "side": resting_side,
                            "price": best_price, "quantity": 10,
                        })
                        self.assertEqual(status, 201)
                        if has_remaining_order:
                            status, _ = api.submit("m1", {
                                "order_id": "R2", "symbol": "ABC", "side": resting_side,
                                "price": 100, "quantity": 10,
                            })
                            self.assertEqual(status, 201)
                        status, _ = api.cancel("R1")
                        self.assertEqual(status, 200)

                        status, response = api.submit("m2", {
                            "order_id": "I1", "symbol": "ABC", "side": incoming_side,
                            "price": 100, "quantity": 10, "type": order_type,
                        })

                        self.assertEqual(status, 201)
                        book = engine.book("ABC")
                        incoming = engine.orders["I1"]
                        self.assertEqual(book.opposite(incoming).levels, {})
                        self.assertEqual(engine.orders["R1"].filled, 0)
                        if has_remaining_order:
                            self.assertEqual(response["status"], FILLED)
                            self.assertEqual(response["filled"], 10)
                            resting_key = "sell" if incoming_side == BUY else "buy"
                            self.assertEqual(
                                [trade[resting_key] for trade in response["trades"]], ["R2"],
                            )
                            self.assertEqual(engine.orders["R2"].status, FILLED)
                        else:
                            self.assertEqual(response["filled"], 0)
                            self.assertEqual(response["trades"], [])
                            self.assertEqual(response["status"], NEW if order_type == LIMIT else CANCELLED)

    def test_matching_prioritizes_earliest_arrival_at_same_price(self):
        # Verify equally priced resting orders match in arrival order rather than order-ID order.
        for incoming_side in (BUY, SELL):
            for order_type in (LIMIT, IOC):
                with self.subTest(side=incoming_side, order_type=order_type):
                    api, engine = build_app()
                    resting_side = SELL if incoming_side == BUY else BUY
                    for order_id in ("Z_FIRST", "A_SECOND", "M_THIRD"):
                        status, _ = api.submit("m1", {
                            "order_id": order_id, "symbol": "ABC", "side": resting_side,
                            "price": 100, "quantity": 10,
                        })
                        self.assertEqual(status, 201)

                    status, response = api.submit("m2", {
                        "order_id": "I1", "symbol": "ABC", "side": incoming_side,
                        "price": 100, "quantity": 15, "type": order_type,
                    })

                    self.assertEqual(status, 201)
                    self.assertEqual(response["status"], FILLED)
                    resting_key = "sell" if incoming_side == BUY else "buy"
                    self.assertEqual(
                        [(trade[resting_key], trade["quantity"]) for trade in response["trades"]],
                        [("Z_FIRST", 10), ("A_SECOND", 5)],
                    )
                    self.assertEqual(engine.orders["Z_FIRST"].status, FILLED)
                    self.assertEqual(engine.orders["A_SECOND"].remaining, 5)
                    self.assertEqual(engine.orders["M_THIRD"].filled, 0)

    def test_matching_preserves_partially_filled_resting_order_priority(self):
        # Verify a partially filled resting order matches before later orders at the same price.
        for incoming_side in (BUY, SELL):
            for order_type in (LIMIT, IOC):
                with self.subTest(side=incoming_side, order_type=order_type):
                    api, engine = build_app()
                    resting_side = SELL if incoming_side == BUY else BUY
                    for order_id in ("R1", "R2"):
                        status, _ = api.submit("m1", {
                            "order_id": order_id, "symbol": "ABC", "side": resting_side,
                            "price": 100, "quantity": 10,
                        })
                        self.assertEqual(status, 201)
                    status, response = api.submit("m2", {
                        "order_id": "I1", "symbol": "ABC", "side": incoming_side,
                        "price": 100, "quantity": 4, "type": order_type,
                    })
                    self.assertEqual(status, 201)
                    self.assertEqual(response["status"], FILLED)
                    resting_key = "sell" if incoming_side == BUY else "buy"
                    self.assertEqual(
                        [(trade[resting_key], trade["quantity"]) for trade in response["trades"]],
                        [("R1", 4)],
                    )
                    self.assertEqual(engine.orders["R1"].remaining, 6)

                    status, response = api.submit("m3", {
                        "order_id": "I2", "symbol": "ABC", "side": incoming_side,
                        "price": 100, "quantity": 10, "type": order_type,
                    })

                    self.assertEqual(status, 201)
                    self.assertEqual(response["status"], FILLED)
                    self.assertEqual(
                        [(trade[resting_key], trade["quantity"]) for trade in response["trades"]],
                        [("R1", 6), ("R2", 4)],
                    )
                    self.assertEqual(engine.orders["R1"].status, FILLED)
                    self.assertEqual(engine.orders["R2"].remaining, 6)
                    book_side = engine.book("ABC").side_for(engine.orders["R2"])
                    self.assertEqual(list(book_side.levels[100]), [engine.orders["R2"]])

    def test_limit_remainder_rests_and_can_be_fully_filled_later(self):
        # Verify a partially filled LIMIT order waits on the book until a later order fills it.
        for incoming_side in (BUY, SELL):
            with self.subTest(side=incoming_side):
                opposite = SELL if incoming_side == BUY else BUY
                api, engine = build_app()
                api.submit("m1", {"order_id": "R1", "symbol": "ABC", "side": opposite,
                                  "price": 100, "quantity": 4})
                status, response = api.submit("m2", {
                    "order_id": "L1", "symbol": "ABC", "side": incoming_side,
                    "price": 100, "quantity": 10, "type": LIMIT,
                })
                self.assertEqual(status, 201)
                self.assertEqual(response["status"], PARTIAL)
                self.assertEqual(response["filled"], 4)
                order = engine.orders["L1"]
                side = engine.book("ABC").side_for(order)
                self.assertEqual(order.remaining, 6)
                self.assertEqual(list(side.levels[100]), [order])

                status, response = api.submit("m3", {
                    "order_id": "R2", "symbol": "ABC", "side": opposite,
                    "price": 100, "quantity": 6,
                })

                self.assertEqual(status, 201)
                self.assertEqual(response["status"], FILLED)
                self.assertEqual(order.status, FILLED)
                self.assertEqual(order.filled, 10)
                self.assertEqual(order.remaining, 0)
                self.assertFalse(order.is_live)
                self.assertEqual(side.levels, {})

    def test_ioc_cancels_remainder_after_partial_fill(self):
        # Verify an IOC order keeps its completed trades but cancels its unfilled remainder.
        for incoming_side in (BUY, SELL):
            with self.subTest(side=incoming_side):
                opposite = SELL if incoming_side == BUY else BUY
                api, engine = build_app()
                api.submit("m1", {"order_id": "R1", "symbol": "ABC", "side": opposite,
                                  "price": 100, "quantity": 4})
                status, response = api.submit("m2", {
                    "order_id": "I1", "symbol": "ABC", "side": incoming_side,
                    "price": 100, "quantity": 10, "type": IOC,
                })
                self.assertEqual(status, 201)
                self.assertEqual(response["filled"], 4)
                self.assertEqual(sum(trade["quantity"] for trade in response["trades"]), 4)
                order = engine.orders["I1"]
                self.assertEqual(order.remaining, 6)
                self.assertEqual(response["status"], CANCELLED)
                self.assertEqual(order.status, CANCELLED)
                self.assertFalse(order.is_live)
                self.assertEqual(engine.book("ABC").side_for(order).levels, {})

                api.submit("m3", {"order_id": "R2", "symbol": "ABC", "side": opposite,
                                  "price": 100, "quantity": 6})
                self.assertEqual(order.filled, 4)
                self.assertEqual(engine.orders["R2"].filled, 0)
                status, response = api.cancel("I1")
                self.assertEqual(status, 404)
                self.assertIn("error", response)
                status, response = api.amend("I1", {"quantity": 20})
                self.assertEqual(status, 404)
                self.assertIn("error", response)

    def test_ioc_cancels_when_no_orders_cross(self):
        # Verify an IOC order is cancelled without resting when no eligible liquidity exists.
        for incoming_side in (BUY, SELL):
            with self.subTest(side=incoming_side):
                api, engine = build_app()
                status, response = api.submit("m1", {
                    "order_id": "I1", "symbol": "ABC", "side": incoming_side,
                    "price": 100, "quantity": 10, "type": IOC,
                })
                self.assertEqual(status, 201)
                self.assertEqual(response, {"status": CANCELLED, "filled": 0, "trades": []})
                order = engine.orders["I1"]
                self.assertFalse(order.is_live)
                self.assertEqual(engine.book("ABC").side_for(order).levels, {})

    def test_ioc_full_fill_is_not_cancelled(self):
        # Verify an IOC order that fills completely is marked filled rather than cancelled.
        for incoming_side in (BUY, SELL):
            with self.subTest(side=incoming_side):
                opposite = SELL if incoming_side == BUY else BUY
                api, engine = build_app()
                api.submit("m1", {"order_id": "R1", "symbol": "ABC", "side": opposite,
                                  "price": 100, "quantity": 10})
                status, response = api.submit("m2", {
                    "order_id": "I1", "symbol": "ABC", "side": incoming_side,
                    "price": 100, "quantity": 10, "type": IOC,
                })
                self.assertEqual(status, 201)
                self.assertEqual(response["status"], FILLED)
                self.assertEqual(response["filled"], 10)
                order = engine.orders["I1"]
                self.assertEqual(order.remaining, 0)
                self.assertEqual(order.status, FILLED)
                self.assertFalse(order.is_live)
                self.assertEqual(engine.book("ABC").side_for(order).levels, {})


if __name__ == "__main__":
    unittest.main()
