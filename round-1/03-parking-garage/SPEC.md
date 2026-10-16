# Garage Operations

A city-centre parking garage runs automated entry and exit gates. Drivers take a ticket on entry and pay on exit; monthly pass holders
are recognised by their licence plate. The repository contains the gate and billing service.

## Capacity

The garage has **200 public spaces** and **20 reserved spaces** for pass holders.
- A driver **without** a pass can enter only while fewer than 200 non-pass vehicles are inside.
- A pass holder can always enter while the garage as a whole has fewer than 220 vehicles inside.
- A vehicle can't enter if it's already inside.

## Pricing (non-pass vehicles, and pass holders on weekends)

Applied in this order (the first rule that applies wins):
1. **Lost ticket:** $50 flat.
2. **Grace period:** stays of **15 minutes or less** are free.
3. **Hourly:** $4 per hour or part thereof, counted from entry, with a **daily maximum of $24 per 24-hour period**
   (a 26-hour stay is one capped 24-hour period plus 2 hours).
   A **merchant validation** (stamped by a shop in the building) removes **2 hours** from the parked time before hours are counted.
4. **Early bird:** entering between **06:00 and 09:00** (09:00 itself is too late) and leaving the same day before **19:00** costs a flat
   **$12**. The driver pays whichever is cheaper, early bird or hourly.

## Monthly passes

Pass holders park free when they **enter** on a weekday (Mon–Fri). Weekend entries are charged like anyone else.

## Data model

| Entity | Fields |
|---|---|
| Pass | plate, holder name, valid from, valid to |
| Ticket | ticket id, plate, entered at, pass holder?, exited at, charge, validated? |
| Occupancy | public vehicles inside, pass vehicles inside |

## Examples

| Entry | Exit | Notes | Charge |
|---|---|---|---|
| Tue 10:00 | Tue 10:12 | | $0 |
| Tue 10:00 | Tue 12:31 | | $12 |
| Tue 10:00 | Tue 13:10 | validated | $8 (1 h 10 m → 2 h) |
| Tue 07:15 | Tue 17:30 | early bird | $12 |
| Mon 10:00 | Tue 12:00 | | $32 |
