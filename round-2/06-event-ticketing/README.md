# Box Office Service

Sells reserved-seating tickets for concerts and shows. A customer picks seats, which places a short **hold** on them; they then
**purchase** the held seats. Customers can **refund** an order before the event. Several API instances share one database.

Pick one ticket from `tickets/`, make a bounded change and prove it. One ticket done properly is a full pass.

## Running

```
python -m unittest discover -s tests -v
```

## Layout

```
boxoffice/api/handlers.py          BoxOfficeApi
boxoffice/services/seating.py      SeatService: holds, availability
boxoffice/services/checkout.py     CheckoutService: purchase held seats
boxoffice/services/refunds.py      RefundService
boxoffice/services/pricing.py      order totals
boxoffice/repositories/*.py        events, seats, orders (SQLite)
boxoffice/notifications.py         e-mail receipts (outbox)
boxoffice/reporting.py             sales by event
boxoffice/db.py, clock.py, errors.py, models.py, config.py
```

## Policy

- A **hold** lasts **10 minutes**. After it expires, the seat is available to anyone again.
- A seat can be held by **one customer at a time** and **sold once**.
- **Purchase:** only seats currently held by that customer. Each ticket costs its **face value + a $3.50 service fee per ticket**.
- **Refunds:** allowed until **48 hours before the event starts**. The refund is the **face value only**; service fees are non-refundable.
  Refunded seats become available again.
- Event start times are stored in the **venue's local time** with the venue's time zone. The server clock is UTC.
