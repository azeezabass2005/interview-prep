# Group Tab

Friends track shared expenses in a group. Anyone can record an expense they paid and how it's split; members record payments to each
other; the app shows balances and suggests how to settle up. `tab.py` holds the logic.

## Expenses

An expense has a payer, an amount (> 0), the participants (all group members) and a split mode:

| Mode | Values | Each participant owes |
|---|---|---|
| EQUAL | none | amount ÷ number of participants |
| EXACT | an amount per participant | that amount; amounts **must add up to the expense** |
| PERCENT | a percentage per participant | that % of the amount; percentages **must add up to 100** |
| SHARES | a number of shares per participant | amount × their shares ÷ **total shares** |

Shares are rounded **down** to the cent; leftover cents go **one cent each to the participants in the order they were listed**, so the
shares always add up to the expense amount exactly.

Expenses can be deleted; a deleted expense no longer affects anything.

## Balances

A member's balance = what they paid for others − what they owe. Positive means the group owes them. A **payment** from A to B (A paying
back B) moves A's balance up and B's down by the amount. Balances always add up to zero.

## Settle up

Suggest payments: repeatedly the member who owes the most pays the member owed the most, the smaller of the two amounts.

## Example

Ana pays $90.00 dinner, EQUAL among Ana, Ben, Cai. Ben pays $45.00 taxi, EXACT: Ben $15, Cai $30.
Balances: Ana **+60.00**, Ben **0.00**, Cai **−60.00**. Settle up: **Cai pays Ana $60.00**.
