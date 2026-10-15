# STL-1504: Custodian rejected netted instruction

**Type:** Bug · **Reporter:** Operations · **Priority:** High

## Description
Monday's job didn't run, so Tuesday's run picked up two days of trades. The custodian rejected an instruction that netted a Monday buy (settles
Tuesday) with a Tuesday sell (settles Wednesday) into a single quantity.

## Acceptance criteria
- Trades are only netted together when they share account, security **and** settlement date.

## Out of scope
- Partial settlement.
