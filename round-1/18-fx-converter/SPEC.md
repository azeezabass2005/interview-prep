# FX Converter

A payments company converts money between currencies for its clients. A client asks for a **quote**, then **books** it.
`fx.py` holds the rate book, quotes and bookings.

## Rates

The rate book holds a **mid rate per currency, in units per 1 USD** (e.g. EUR 0.92, JPY 155). The mid rate from currency A to currency B is
`rate[B] ÷ rate[A]` (USD has rate 1). Rates can be updated at any time; a quote keeps the rate it was given.

## Quotes

- The client rate is the mid rate **minus a 0.5% spread** (the client always gets slightly less than mid).
- The amount the client receives is rounded **down** to the destination currency's minor unit: 2 decimals for USD, EUR and GBP,
  **0 decimals for JPY**.
- A quote is valid for **30 seconds** from when it's issued; it can be booked up to and including the 30th second.

## Booking

- A quote can be booked once.
- **Daily limit:** a client can convert at most **USD 50,000 equivalent per UTC day**, counting all their bookings that day. The USD
  equivalent of a booking is its source amount converted at the **mid** rate.

## Other operations

- A client can **cancel** an open quote; `expire_quotes` marks quotes past their validity as EXPIRED.
- `usage(client, day)`: USD equivalent booked that day and what's left of the limit.
- `blotter(day)`: the day's bookings (client, source currency, amount, target currency, amount received), sorted.

## Example

USD 1,000 → EUR with EUR at 0.9200 per USD → client rate 0.9154 → **EUR 915.40**.
