# Brokerage Fee Engine

A retail broker charges fees on every equity and option trade and sends each account a **monthly statement**. Trades arrive from the
execution system during the day; occasionally the exchange **busts** (cancels) a trade after the fact. The repository contains the fee
engine that records trades and produces statements.

## Equity commission

Commission is tiered on the trade's **notional** (price × quantity), like tax brackets:

| Portion of notional | Rate |
|---|---|
| first $10,000 | 0.10% |
| $10,000 – $50,000 | 0.05% |
| above $50,000 | 0.02% |

Equity commission is rounded half-up to the cent, then a **minimum of $1.00** and a **maximum of $50.00** apply.

## Option commission

**$0.65 per contract**, minimum **$1.00** per trade. There is **no maximum** for options. An option contract covers 100 shares, so an
option trade's notional is contracts × price × 100.

## Regulatory fee

On **sells only** (equities and options): notional × **0.0000278**, always rounded **up** to the next cent. It's not commission:
no minimum, no maximum, no discount.

## Volume discount

From an account's **51st trade of the calendar month** onward (counting equity and option trades in execution-time order), the commission
is discounted by **20%** (discount rounded half-up to the cent). **Busted trades don't count**: they're treated as if they never happened.

## Statements

A statement covers one calendar month: trades executed from the 1st at 00:00 up to, but not including, the 1st of the next month.
It lists one line per non-busted trade (commission, discount, regulatory fee, total) and the month's total.

## Data model

| Entity | Fields |
|---|---|
| Account | account id, owner |
| Trade | trade id, account, asset class (EQUITY / OPTION), side (BUY / SELL), quantity or contracts, price, executed at, status (ACTIVE / BUSTED) |
| Statement line | trade id, commission, discount, regulatory fee, total |

## Examples

- Equity buy, notional $60,000 → 10.00 + 20.00 + 2.00 = **$32.00** commission.
- Equity sell, notional $5,000 → **$5.00** commission + **$0.14** regulatory fee (0.139 rounded up).
- Option buy, 10 contracts → **$6.50** commission.
