# PAY-501: Wallets going negative / reconciliation breaks

**Type:** Bug · **Reporter:** Finance operations · **Priority:** Critical

## Description
Nightly reconciliation flags wallets where the balance doesn't match the sum of entries. In each case the customer made two withdrawals
within the same second (double-tap in the app). Example: balance $100, two $80 withdrawals both succeed; the entries show −$160 but the
balance shows $20.

## Steps to reproduce
1. Wallet with $100.00.
2. Two `POST /withdrawals` of $80.00 hit two API instances at the same time.
3. Both return 200.

## Acceptance criteria
- With concurrent withdrawals, a wallet's balance never goes below zero and the over-limit withdrawal is rejected (insufficient funds).
- Balance always equals the sum of entries.

## Out of scope
- The app's double-tap UX.
