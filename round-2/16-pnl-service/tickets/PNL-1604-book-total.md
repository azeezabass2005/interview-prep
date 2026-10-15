# PNL-1604: Book total P&L is nonsense for multi-currency books

**Type:** Bug · **Reporter:** Risk · **Priority:** Medium

## Description
The Global Equity book shows total P&L of 1.2 million, but its positions' P&L converted to USD sum to about 150k. The book holds Japanese
stocks (JPY P&L in the millions).

## Acceptance criteria
- Book totals are in USD, converting each position at the valuation-date rate.

## Out of scope
- Hedging P&L.
