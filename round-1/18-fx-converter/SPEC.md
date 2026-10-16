# FX Payments Service

Customers send money abroad in two steps: they request a **quote** (how much the recipient will get), then **book** a payment against that
quote. The repository contains the rate book, quoting, booking and limits.

## Rates

- Mid-market rates are published per pair `BASEQUOTE` = units of QUOTE per 1 BASE, always against USD: e.g. `EURUSD 1.0850`, `USDJPY 151.20`.
- Cross rates go through USD.
- A rate older than **60 seconds** must not be used; quoting with one fails.

## Quotes

- **Spread** by the amount's **USD equivalent** at mid: under $10,000 → 1.00%; $10,000 to under $100,000 → 0.50%; $100,000+ → 0.25%.
- Target amount = source × cross mid × (1 − spread), **rounded down** to the target currency's minor unit (USD/EUR/GBP: 2 decimals,
  **JPY: 0**, KWD: 3).
- A quote is valid for **30 seconds**.

## Booking

- A payment is booked against a **valid** (unexpired) quote, at exactly the quoted amounts. Each quote can be booked once.
- **Daily limit:** each customer may book at most **$50,000** USD-equivalent (the quote's USD equivalent) per calendar day (UTC).
- A payment can be **cancelled** within 30 minutes of booking; cancelled payments don't count toward the daily limit.

## Data model

| Entity | Fields |
|---|---|
| Rate | pair, rate, published at |
| Quote | quote id, customer, source currency/amount, target currency/amount, mid, spread, USD equivalent, created at, booked? |
| Payment | payment id, quote id, customer, booked at, status (BOOKED / CANCELLED) |

## Example

1,000 EUR → JPY: 1,000 × 1.0850 = 1,085 USD → × 151.20 = 164,052 JPY mid. USD equivalent $1,085 → 1% → 162,411.48 → **¥162,411**.
