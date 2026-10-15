# PNL-1601: Realized P&L doesn't match the tax report

**Type:** Bug · **Reporter:** Fund accounting · **Priority:** High

## Description
For positions built in several buys, realized P&L on a sale differs from the tax-lot report, which uses FIFO as per our methodology.

## Steps to reproduce
1. BUY 100 @ 10, BUY 100 @ 20.
2. SELL 100 @ 25.
3. Dashboard realized P&L: **1,000**. Tax report (FIFO): **1,500**.

## Acceptance criteria
- Realized P&L follows FIFO lots.

## Out of scope
- Tax-lot selection by the PM (specific identification).
