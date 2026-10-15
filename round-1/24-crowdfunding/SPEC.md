# All-or-Nothing Crowdfunding

A crowdfunding platform runs campaigns that are **all-or-nothing**: backers are only charged if the goal is reached by the deadline.
The code in `crowd/` implements the rules below. A creator says their payout is wrong, and a backer says they were charged for a failed campaign.

## Rules

- A campaign has a **goal**, a **deadline**, and **reward tiers**. Each tier has a **minimum pledge** and an optional **quantity limit**.
- **Pledging** is allowed only **before the deadline**. The amount must be at least the tier's minimum. A tier that has reached its
  limit is **sold out** and rejects new pledges.
- **Cancelling** a pledge before the deadline removes it from the campaign entirely, including its claim on a limited tier.
- **Closing** at the deadline:
  - **Funded** if the total of active pledges is **at least** the goal. Otherwise **not funded**: nobody is charged and **no fees** apply.
  - If funded, fees are:
    - **platform fee:** 5% of the total
    - **processing fee:** 3% of the total **+ $0.20 per charged pledge**
  - **Creator payout** = total − platform fee − processing fee.
- Fees are rounded half-up to the cent.

## Example

Goal $1,000. Tiers: STANDARD (min $35, unlimited), DELUXE (min $100, limit 50).
20 × $35 STANDARD + 5 × $100 DELUXE = **$1,200** → funded.
Platform fee $60.00 · processing $36.00 + 25 × $0.20 = $41.00 → **payout $1,099.00**.

## Candidate questions

1. Identify anything in the rules that must be clarified before implementation.
2. Explain how you would model campaigns, tiers, pledges and the outcome.
3. Outline the close-out calculation and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
