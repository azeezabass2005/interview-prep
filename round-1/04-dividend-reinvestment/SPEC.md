# Dividend Reinvestment Plan (DRIP)

A transfer agent keeps the share register for several listed companies and pays their cash dividends. Shareholders can enrol in the
**DRIP** for a security, in which case their dividend buys more (fractional) shares instead of being paid as cash. The repository contains
the register and the dividend processor.

## Register

Every share movement (purchase, sale, transfer, reinvestment) is recorded with the date it takes effect. An account's holding of a
security on a date is the sum of its movements on or before that date.

## Processing a dividend event

A dividend event has a security, a **record date**, a **pay date**, an amount per share and a **reinvestment price**.

1. **Entitlement:** each account is paid on the shares it held at the **end of the record date**. Movements after the record date don't
   change the entitlement. Accounts holding zero shares are skipped.
2. **Gross dividend** = shares × amount per share, **rounded down** to the cent.
3. **Withholding tax** depends on the account's country of tax residence, applied to the gross and rounded half-up to the cent:

| Residence | Rate |
|---|---|
| US | 0% |
| GB | 15% |
| JP | 10% |
| any other country | 30% |

4. **Cash or reinvest:** an account reinvests if it was **enrolled in the DRIP for that security on the record date**. Enrolment can be
   switched on or off; each change takes effect from its effective date.
5. **Reinvestment:**
   - net cash = gross − withholding;
   - a fee of **$0.50**, but never more than **5% of the net cash** (fee rounded half-up to the cent);
   - the rest, **plus any cash left over from this account's previous reinvestment in the same security**, buys shares at the
     reinvestment price, to **4 decimal places, never rounding up**;
   - what's left (a fraction of a cent) is kept for the next reinvestment in that security;
   - bought shares are added to the register **on the pay date**.

## Data model

| Entity | Fields |
|---|---|
| Account | account id, name, residence country |
| Movement | account, security, date, shares (+/−), reason |
| Enrolment | account, security, effective from, enrolled? |
| Dividend event | security, record date, pay date, per share, reinvestment price |
| Payment | account, gross, withholding, fee, cash paid, shares bought, leftover cash |

## Examples

US resident, enrolled, 100 BBG shares on the record date; dividend $0.82, reinvestment price $40.00:
gross $82.00 → no withholding → fee $0.50 → $81.50 invested → **2.0375 shares**.

Same with 10 shares: gross $8.20 → fee 5% × 8.20 = **$0.41** → $7.79 / $40 = 0.19475 → **0.1947 shares**, $0.002 kept for next time.
