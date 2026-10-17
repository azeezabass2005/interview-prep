# Payments Ledger

A digital wallet keeps a **double-entry ledger**: every movement of money is recorded as entries that add up to zero. Balances are
derived from the entries. `ledger.py` holds accounts, transfers, holds and reversals.

## Accounts

Each account has a currency. **Balance** = sum of its entries. **Available** = balance − active holds. Customer accounts can't go
below zero available. Deposits come from an external `WORLD` account (which may be negative), and fees go to a `FEES` account.

## Transfers

- From one customer account to another, same currency, amount > 0, and the sender must have enough **available** funds (amount + fee).
- Every transfer has a client **idempotency key**: repeating a key returns the original transfer and moves no money.
- **Fee:** transfers **above $1,000** pay **0.05% of the amount, minimum $1.00**, rounded to the cent, charged to the sender.

## Holds

A hold reserves money (e.g. a card authorisation): it reduces available but not balance. It can be **captured** (becomes a transfer of
that amount) or **released**.

## Reversals

A transfer can be reversed **once**. The reversal moves the amount back **and refunds the fee**.

## Example

Ana deposits $2,000 and sends Ben $1,200 → fee 0.05% = $0.60 → **minimum $1.00**. Ana's balance **$799.00**, Ben **$1,200.00**, FEES **$1.00**.
