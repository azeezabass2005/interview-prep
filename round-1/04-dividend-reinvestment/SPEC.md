# Dividend Reinvestment Plan (DRIP)

A transfer agent pays cash dividends to shareholders. Shareholders enrolled in the DRIP have their
dividend reinvested in more (fractional) shares instead of receiving cash. The code in `drip/`
processes one dividend event at a time.

## Rules

- **Entitlement:** a dividend is paid on the shares an account held at the **end of the record date**.
  Trades after the record date don't change the entitlement.
- **Gross dividend** = shares × dividend per share, **rounded down** to the cent.
- **Withholding tax:** **non-resident** accounts have **15%** of the **gross** withheld (rounded half-up
  to the cent). Residents have no withholding.
- **Cash holders** (not enrolled) receive gross minus withholding.
- **DRIP holders**:
  1. Net cash = gross − withholding.
  2. A reinvestment fee of **$0.50** is charged, capped at **5% of the net cash** (rounded half-up to the cent).
  3. The remaining cash buys shares at the event's **reinvestment price**. Shares are bought to
     **4 decimal places and never round up** (you can't spend cash you don't have).
  4. Any cash left over (a fraction of a cent, typically) is **kept for the account and added to its next reinvestment**.
- Reinvested shares are credited to the account on the **pay date**.

## Example

Resident, DRIP-enrolled, 100 shares on the record date. Dividend $0.82 per share, reinvestment price $40.00:

gross $82.00 → no withholding → fee $0.50 → $81.50 invested → **2.0375 shares** bought, $0 left over.

Same, but 10 shares: gross $8.20 → fee is 5% × 8.20 = **$0.41** → $7.79 / $40 = 0.19475 → **0.1947 shares**,
$0.002 left over for next time.

## Candidate questions

1. Identify anything in the rules that must be clarified before implementation.
2. Explain how you would model holdings, a dividend event, and per-account results.
3. Outline the payment calculation and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
