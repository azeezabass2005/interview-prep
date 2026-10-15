# PAY-502: Money disappeared on a failed transfer

**Type:** Bug · **Reporter:** Customer support · **Priority:** High

## Description
A customer sent $50 to a friend whose wallet had just been closed. The app showed "Transfer failed", but $50 left the customer's wallet
and never arrived anywhere.

## Steps to reproduce
1. Wallet A $200, wallet B closed.
2. `POST /transfers` A → B $50 → error "account B is not open".
3. A's balance is $150 and there's a −$50 entry.

## Acceptance criteria
- A failed transfer leaves both wallets and the entries exactly as before.
- A successful transfer records both legs.

## Out of scope
- Refunding the affected customers (ops will handle it).
