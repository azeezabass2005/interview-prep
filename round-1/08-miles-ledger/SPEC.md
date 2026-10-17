# Miles Ledger

An airline's frequent-flyer programme. Members earn miles on flights, reach status tiers, redeem miles, transfer them to other members,
and lose them after a period of inactivity. `miles.py` is the ledger.

## Earning

- **Base miles** = distance × fare-class multiplier (Y 1.0 · J 1.5 · F 2.0), rounded down.
- **Status bonus** on top of base miles: SILVER +25%, GOLD +50% of the **base miles**, rounded down. The bonus uses the member's status
  at the time of the flight.

## Status

- **Qualifying miles** = **base** miles earned in a calendar year (bonus miles don't qualify).
- SILVER at 25,000 qualifying miles, GOLD at 50,000. Status applies from the next flight after reaching it, and **lasts until the end of
  the following calendar year**.

## Redeeming, transferring, expiry

- Redeem any amount up to the balance.
- Transfer miles to another member: at most **50,000 miles sent per calendar year** in total. Transfers don't count as activity.
- **Expiry:** if a member has no activity (a flight or a redemption) for **18 months**, their whole balance expires. Activity on a day
  keeps miles alive until the same day 18 months later.

## Example

A SILVER member flies 2,000 miles in J → base 3,000, bonus 750 → **3,750 miles**.
