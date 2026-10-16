# Prime Brokerage Margin Engine

A prime broker lends clients cash against the securities they hold. Every evening a **margin run** values each account using the latest
prices, and issues a **margin call** if collateral falls short. Clients cure calls by depositing cash. The repository contains the margin engine.

## Valuation

- **Market value (MV)** = quantity × latest price. Longs have positive quantity, shorts negative.
- **Haircut** by asset class: EQUITY **25%**, ETF **15%**, BOND **10%**.
- **Concentration:** a long position worth **more than 40%** of the account's **gross long MV** (sum of long MVs) gets at least a **50%** haircut.
- **Stale prices:** if a security's latest price is dated **before the previous calendar day** relative to the run date, add **10 percentage
  points** to its haircut (after the concentration rule).
- **Collateral** = Σ long MV × (1 − haircut) + cash if positive.
- **Requirement** = loan (−cash, if cash is negative) + Σ |short MV| × **130%**.
- **Excess** = collateral − requirement.

## Calls

- If excess is negative, a **margin call** is issued for −excess **rounded up to the next $100**, unless the account already has an open call.
- A call is **met** when cash **deposited after the call was issued** adds up to at least the call amount, or when a later run shows
  excess ≥ 0.

## Liquidation plan

For an unmet call, suggest whole shares to sell, **highest haircut first** (ties: larger MV first). Selling one share improves excess by
price × haircut. Sell only as many as needed.

## Data model

| Entity | Fields |
|---|---|
| Security | symbol, asset class |
| Price | symbol, date, price |
| Account | account id, cash, positions (symbol → quantity) |
| Call | account, issued on, amount, status (OPEN / MET) |
| Deposit | account, date, amount |

## Example

Cash −$100,000; AAPL 400 @ $200, TLT 300 @ $100, SPY 50 @ $400 (all prices from the run date). Gross long MV $130,000; AAPL is 61.5% → 50%.
Collateral 40,000 + 27,000 + 17,000 = $84,000; requirement $100,000 → **call $16,000**. Plan: **sell 160 AAPL**.
