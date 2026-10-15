# PNL-1603: P&L explodes after a stock split

**Type:** Bug · **Reporter:** Risk · **Priority:** Critical

## Description
After XYZ's 4-for-1 split, the dashboard shows a huge loss on positions held before the split, and positions bought after the split look wrong too.

## Steps to reproduce
1. BUY 100 XYZ @ 400 on 3 March.
2. 4:1 split effective 10 March.
3. BUY 50 XYZ @ 101 on 12 March.
4. Close on 13 March = 102. Expected unrealized = (102 − 100) × 400 + (102 − 101) × 50 = **850**.

## Acceptance criteria
- Splits adjust lots opened before the effective date, and only those.

## Out of scope
- Cash dividends.
