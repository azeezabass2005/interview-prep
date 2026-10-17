# Solar Net-Metering Billing

An electric utility bills homes with rooftop solar. Each home has a meter with two **cumulative registers**: kWh **imported** from the grid
and kWh **exported** to it. A meter reader records both registers roughly once a month; each new reading closes a **billing period** that
starts at the previous reading. The repository contains the billing service.

## Usage for a period

- Usage is the difference between this reading and the previous one, per register.
- Registers are 5-digit and **roll over**: after 99,999 they continue from 00,000. A smaller reading than last time means the register rolled over.
- **Net usage** = imported − exported.

## Banking

If net usage is negative, the surplus kWh are **banked**. Banked kWh are used to offset future net usage **before** tiered pricing.
Banked kWh that are used are removed from the bank.

## Energy charge

Tiered on the billable kWh (net usage after banked credit). Tier sizes are given **per 30 days** and scaled to the period's length
(number of days between readings), rounded down to whole kWh:

| Tier | Size per 30 days | Rate |
|---|---|---|
| 1 | first 500 kWh | $0.12 |
| 2 | next 500 kWh | $0.15 |
| 3 | everything above | $0.20 |

## Other charges

- **Daily service charge:** **$0.40 per day** in the period. Not taxed.
- **Tax:** **5% of the energy charge only**, rounded half-up to the cent.

## Annual true-up

On the bill whose period **ends** in **December**, any kWh still banked (after this bill) are **paid out at $0.04/kWh** as a separate line,
and the bank is reset to zero.

## Data model

| Entity | Fields |
|---|---|
| Account | account id, address |
| Reading | read on (date), import register, export register |
| Bill | period start/end, days, imported, exported, billable kWh, energy, tax, service, total, true-up payout |

## Example

Previous reading 2026-01-01 (import 10,000, export 2,000); reading 2026-01-31 (import 10,700, export 2,100). 30 days, net 600 kWh:
energy 500 × 0.12 + 100 × 0.15 = $75.00, tax $3.75, service $12.00 → **$90.75**.
