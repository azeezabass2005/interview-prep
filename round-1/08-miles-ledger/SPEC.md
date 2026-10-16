# Frequent Flyer Program

An airline's loyalty program awards miles for flights, gives members **status** based on how much they fly, lets them **redeem** miles
for award tickets and **transfer** miles to other members. The repository contains the loyalty service.

## Earning

- **5 miles per whole dollar** of base fare (cents don't earn). These are **base miles**.
- **Status bonus** on top of base miles: Silver **+25%**, Gold **+50%**, Platinum **+100%** (bonus rounded down). Base members get no bonus.
  The member's status **at the time of the flight** applies.
- Each flight's miles (base + bonus) form one **lot** dated the flight date.
- Cancelling a flight removes that flight's miles: whatever is still unspent in its lot is removed and the flight no longer counts for status.

## Status

Status depends on **qualifying miles** earned in the current calendar year. **Only base miles from flights qualify** (no bonuses, no
transfers).

| Qualifying miles this year | Status |
|---|---|
| 0 – 24,999 | Base |
| 25,000 – 49,999 | Silver |
| 50,000 – 74,999 | Gold |
| 75,000+ | Platinum |

Status changes immediately when a threshold is crossed, so it applies to the next flight.

## Expiry

Miles expire on the **2-year anniversary** of their lot date; from that day on they can't be used.
**Platinum members' miles don't expire** while they are Platinum.

## Redemption

Spends the **oldest usable miles first**. If the member doesn't have enough usable miles, nothing is spent.

## Transfers

A member can transfer **1,000 miles or more** to another member. The sender's miles are taken oldest-first; the receiver gets one new lot
dated the **transfer date**. Transferred miles never count as qualifying miles.

## Data model

| Entity | Fields |
|---|---|
| Member | member id, name |
| Flight | flight id, member, date, base fare, cancelled? |
| Lot | member, date, miles, remaining, source (FLIGHT / TRANSFER), flight id |

## Example

A Gold member flies a $412.80 fare on 2026-01-10: base 412 × 5 = 2,060 miles, bonus 1,030 → **3,090 miles**, usable until 2028-01-09.
