# Charity Auction Platform

A charity gala runs an online auction alongside the live event. Registered bidders place **maximum bids** on lots; the platform bids on
their behalf (proxy bidding). Each lot closes at a scheduled time, with a soft-close extension. After the event every winning bidder gets
one invoice. The repository contains the auction service.

## Bidding

- A bid is a bidder's **maximum** for a lot. A bidder may raise their maximum later; a new bid **lower than or equal to** their current maximum is rejected.
- Bids are accepted only before the lot's **closing time**.
- **Soft close:** a bid placed in the **last 2 minutes** before closing moves the closing time to **2 minutes after that bid**.

## Current price and winner

- The **winner** is the bidder with the highest maximum. If two maximums are equal, the one placed **first** wins.
- The **current price** is the runner-up's maximum **plus one increment**, but never more than the winner's maximum and never less than
  the lot's **opening price**. With a single bidder, the price is the opening price.
- The **increment depends on the runner-up's maximum**:

| Runner-up's maximum | Increment |
|---|---|
| under $100 | $5 |
| $100 – $499.99 | $10 |
| $500 and above | $25 |

- At closing, if the lot has a **reserve** and the final price is below it, the lot is unsold.

## Invoices

- The winner pays the **hammer price** (the final current price) plus a **10% buyer's premium** on the hammer price, rounded half-up to the cent.
- One invoice per bidder covers all lots they won.
- Each lot has a **fair market value (FMV)**. The tax-deductible donation for a lot is **hammer − FMV**, never below zero.

## Data model

| Entity | Fields |
|---|---|
| Lot | lot id, title, opening price, reserve (optional), FMV, closes at |
| Bidder | paddle number, name |
| Bid | lot, paddle, maximum, placed at, sequence |
| Invoice | paddle, lines (lot, hammer, premium, deductible), total |

## Example

Lot opening $50, FMV $100. Bids: A max $150, then B max $180, then C max $175.
Winner B; runner-up C ($175 → increment $10) → price min(185, 180) = **$180**. Invoice: 180 + 18 premium = **$198.00**; deductible $80.
