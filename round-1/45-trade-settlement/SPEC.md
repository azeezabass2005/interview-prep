# Trade Settlement

After trades are executed, the back office settles them: shares and cash change hands on the settlement date. `settlement.py` computes
settlement dates, nets trades into instructions, handles failed deliveries and reconciles positions with the custodian.

## Settlement date

**T+1 business day**: the next day that's not a Saturday, Sunday or market holiday.

## Netting

On a settlement date, all **live** (not cancelled) trades settling that day are netted per **(account, symbol)**:
- net quantity = bought − sold;
- net cash = sold value − bought value.

Each (account, symbol) produces one instruction.

## Failed deliveries

An instruction with a **negative** net quantity needs the account to deliver shares. If the account's available holdings are less than
needed, the instruction **FAILS**. A failed instruction is **retried on the next settlement run** (with that day's holdings), until it settles.

## Reconciliation

Compare our positions with the custodian's statement. A **break** is any symbol where the quantities differ — including symbols that
appear on **only one side** (the missing side counts as 0).

## Example

Thursday 2 July 2026 (Friday 3 July is a holiday): Ana buys 100 AAPL @ $200 and sells 40 @ $201. Settles **Monday 6 July** as one
instruction: **+60 AAPL, −$11,960.00**.
