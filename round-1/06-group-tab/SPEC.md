# Group Tab

An app for friends who share costs (trips, flat bills, dinners). A group records **expenses** (who paid, how it's split) and **payments**
(one member paying another back). The app shows each member's **balance** and suggests the fewest transfers to settle up. The repository
contains the backend.

## Money

All amounts are in cents. **No cent may be lost or invented:** the shares of an expense always add up to the expense amount exactly, and
the group's balances always add up to zero.

## Splitting an expense

| Split | Input | Rule |
|---|---|---|
| EQUAL | participants | Total ÷ number of participants, rounded down; leftover cents go one each to participants in **alphabetical** order. |
| EXACT | amount per participant | Amounts must add up to the total, otherwise the expense is rejected. |
| PERCENT | percentage per participant | Percentages must add up to 100. Each share is rounded down; leftover cents go one each to the participants with the **largest fractional remainder** (ties: alphabetical). |
| SHARES | integer weight per participant | Like PERCENT, using weight ÷ total weight. Same leftover rule. |

Only group members can pay or participate.

## Balances

A member's balance = what they paid for others − what others paid for them:
- for each expense: the payer is credited the full amount; each participant is debited their share;
- for each payment *A pays B*: A's balance goes **up**, B's goes **down**.

Expenses can be **edited** (replaced) or **deleted**; deleted expenses no longer affect balances.

## Settling up

Suggested transfers are produced greedily: repeatedly take the member who owes the most and the member who is owed the most, and transfer
the smaller of the two amounts. Ties are broken alphabetically. Members with a zero balance are left out.

## Data model

| Entity | Fields |
|---|---|
| Group | group id, name, members |
| Expense | expense id, payer, amount, description, split type, split details, shares, deleted? |
| Payment | payment id, from member, to member, amount |

## Examples

- $10.00 split EQUAL between ann, bob, cy → ann 334, bob 333, cy 333.
- $1.00 split PERCENT ann 33⅓ / bob 33⅓ / cy 33⅓ is invalid (doesn't add up to exactly 100); ann 50 / bob 25 / cy 25 → 50, 25, 25.
- Balances ann +50.00, bob +30.00, cy −50.00, dan −30.00 → suggested: **cy → ann 50.00**, **dan → bob 30.00**.
