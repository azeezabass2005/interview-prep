# Crowdfunding

A crowdfunding platform runs all-or-nothing campaigns. Backers pledge money, optionally for a reward tier; cards are charged only if the
campaign reaches its goal. `crowd.py` manages pledges and settles campaigns.

## Pledges

- A campaign has a goal, a deadline, and reward tiers (minimum pledge and a limited number of slots).
- Pledges can be made, changed or cancelled **before the deadline** (at the deadline it's closed).
- A backer has at most one pledge per campaign. Changing a pledge can change the amount and/or tier.
- A tier needs a pledge of at least its minimum, and a free slot. **Cancelling or changing tier frees the slot.**

## Settlement (after the deadline)

- The campaign is **funded** if total pledges are **at least** the goal. Otherwise nobody is charged.
- If funded, every pledge is charged. A declined charge is **retried once**; if it fails again the pledge is dropped (listed as failed).
- **Collected** = successful charges.
- Fees: platform **5% of collected**; payment processing **3% + $0.20 per successful charge**. Every fee is rounded to the cent.
- **Creator payout** = collected − fees.

## Example

Goal $5,000. Pledges $3,000 and $2,500, both charged → collected $5,500; platform $275.00; processing 165.00 + 0.40 = $165.40;
payout **$5,059.60**.
