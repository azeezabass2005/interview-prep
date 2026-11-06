# MKT-310: Quotes come back in the wrong currency

**Type:** Bug · **Priority:** High · **Reporter:** Customer Success

## Description
Birch's US desk asked for `GET /quotes/AAPL` (no `ccy`) and got `"currency": "EUR"` with a price around 171. A minute later it
was back to USD. It happens right after someone, anywhere, asks for a quote in another currency. A customer in London also once
got a price that had been converted twice (USD → EUR → GBP).

## Steps to reproduce
1. `GET /quotes/AAPL?ccy=EUR` → 171.0 EUR (correct).
2. `GET /quotes/AAPL` → 171.0 EUR (expected 190.0 USD).

## Acceptance criteria
- A quote without `ccy` is in the instrument's own currency; with `ccy` it's converted exactly once.
- One customer's currency choice never affects another customer's response.
