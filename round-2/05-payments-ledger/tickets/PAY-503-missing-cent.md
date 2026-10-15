# PAY-503: Balances off by one cent

**Type:** Bug · **Reporter:** Customer support · **Priority:** Medium

## Description
Customers report losing a cent. One deposited $8.20 and their wallet shows $8.19. Another deposited $4.35 and sees $4.34.
Most amounts look fine.

## Acceptance criteria
- Round balances to the nearest cent in `format_cents` before displaying them, so the app shows $8.20.

## Out of scope
- Correcting historical balances (finance will run a script).
