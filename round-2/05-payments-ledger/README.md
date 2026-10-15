# Wallet Ledger Service

A stored-value wallet: customers deposit money, withdraw it, and transfer it to other wallets. Every balance change is also written as a
ledger **entry**, and finance reconciles balances against entries every night. Several API instances share one database.

Pick one ticket from `tickets/`, make a bounded change and prove it. One ticket done properly is a full pass.

## Running

```
python -m unittest discover -s tests -v
```

## Layout

```
ledger/api/handlers.py            WalletApi: deposits, withdrawals, transfers, statements
ledger/services/wallets.py        WalletService: business operations
ledger/services/money.py          parsing/formatting money
ledger/services/statements.py     paginated statements
ledger/services/fraud.py          velocity checks (flags only, never blocks)
ledger/repositories/accounts.py   accounts table
ledger/repositories/entries.py    entries table
ledger/db.py, clock.py, errors.py, models.py, config.py
```

## Rules (the "ledger invariants")

1. Money is stored as **integer cents**. Clients send decimal strings like `"10.10"`; more than 2 decimal places is invalid.
2. A balance can **never go negative**.
3. For every account, **balance == sum of its entries**, at all times.
4. A transfer moves money **all or nothing**: both legs are recorded, or neither.
5. Only `OPEN` accounts can send or receive money.
6. Statements list entries newest-last, in pages, with a cursor. Every entry appears **exactly once** across pages.
