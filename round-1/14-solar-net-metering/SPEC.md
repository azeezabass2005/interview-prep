# Solar Net Metering

A utility bills homes with rooftop solar. Each meter has two **cumulative** registers: kWh imported from the grid and kWh exported to
it. Each meter reading produces a bill. `netmeter.py` does the billing.

## Readings

- The first reading of a customer is the baseline (no bill).
- Usage for a period = current register − previous register. Registers are 5 digits and **roll over from 99,999 to 0**.

## Bill

1. **Net** = imported − exported.
2. If net is negative, the excess kWh are **banked** (kWh credit) and there's no energy charge.
3. If net is positive, banked kWh are used first (reducing the bank), then the rest is charged:
   - the first **500 kWh** at **$0.15**, the rest at **$0.20**.
   - The 500 kWh tier is for a 30-day period; for other lengths it's **prorated**: 500 × days ÷ 30, rounded to a whole kWh.
4. Every bill has a **$10.00** fixed charge.

## True-up

Once a year the bank is settled: banked kWh are paid out at **$0.05/kWh** and the bank goes back to **zero**.

## Reports

- `history(customer)`: the customer's bills in order. `summary(customer)`: number of bills, kWh imported and exported, total
  charged and the current bank.
- `estimate(customer, days)`: estimated net kWh for a period, from the average daily net usage of the last 3 bills (never negative).

## Example

30-day period, imported 650, exported 100 → net 550 → 500 × 0.15 + 50 × 0.20 = 85.00, + 10.00 = **$95.00**.
