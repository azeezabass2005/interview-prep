# All-or-Nothing Crowdfunding

Creators run **all-or-nothing** campaigns: backers pledge during the campaign; only if the goal is reached by the deadline are their cards
charged. The repository contains the campaign, pledge and settlement service.

## Campaigns and tiers

- A campaign has a **goal**, a **deadline** and reward **tiers**, each with a **minimum pledge** and an optional **quantity limit**.
- A tier that has reached its limit is **sold out**.

## Pledges

- Pledging, **changing** a pledge (amount and/or tier) and **cancelling** are allowed only **before the deadline**.
- A pledge's amount must be at least its tier's minimum. Pledging into or changing to a sold-out tier is rejected.
- A cancelled pledge no longer counts for anything (total, tier limits, charges).

## Settlement (at the deadline)

- The campaign is **funded** if the total of active pledges is **at least** the goal. Otherwise nothing is charged and no fees apply.
- If funded, every active pledge's card is charged. Some charges **fail**; failed pledges are written off (not collected).
- **Fees** on a funded campaign: platform **5% of the collected amount**; processing **3% of the collected amount + $0.20 per
  successful charge**. Fees are rounded half-up to the cent.
- **Creator payout** = collected − platform fee − processing fee.
- **Stretch goal:** if active pledges at the deadline reach **150% of the goal**, every DELUXE backer gets a bonus reward.

## Example

Goal $1,000; STANDARD (min $35), DELUXE (min $100, limit 50). 20 × $35 STANDARD + 5 × $100 DELUXE = $1,200 → funded.
All charges succeed: platform $60.00; processing $36.00 + 25 × $0.20 = $41.00 → **payout $1,099.00**.
