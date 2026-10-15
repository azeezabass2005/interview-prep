# Trade Settlement Service

After trades are executed, middle office must (1) **reconcile** our trade records against broker confirmations, (2) compute each
trade's **settlement date**, and (3) send **settlement instructions** to the custodian, **netted** per account, security and settlement date.
A nightly job generates instructions; ops can re-run it after failures.

Pick one ticket from `tickets/`, make a bounded change and prove it. One ticket done properly is a full pass.

## Running

```
python -m unittest discover -s tests -v
```

## Layout

```
settle/api/handlers.py                SettlementApi
settle/services/settlement_dates.py   settlement date per trade
settle/services/recon.py              trade vs broker-confirm matching
settle/services/netting.py            netting groups
settle/services/instructions.py       InstructionJob (nightly, re-runnable)
settle/calendars.py                   business-day calendar (weekends + market holidays)
settle/repositories/*.py              trades, confirms, instructions
settle/db.py, errors.py, models.py, config.py
```

## Rules

- **Settlement cycle** (in **business days** after trade date): equities T+1, government bonds T+1, corporate bonds T+2.
  Business days exclude weekends and the market holiday calendar.
- **Reconciliation:** a confirm matches a trade if the trade id, side and quantity match exactly and the price is within **0.0001**.
  Everything else is a **break**.
- **Netting:** one instruction per **(account, security, settlement date)**: net quantity (buys − sells) and net cash.
- **Re-runs:** running the instruction job again must **never** create a second instruction for a trade already instructed.
