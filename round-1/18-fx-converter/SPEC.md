# FX Payments Converter

A payments app lets customers send money in one currency and have it arrive in another. The code in `fx/` produces
conversion quotes. Finance has flagged quotes that don't reconcile.

## Rules

- **Rates** are mid-market quotes for currency pairs against USD, written `BASEQUOTE` = units of QUOTE per 1 BASE.
  Examples: `EURUSD 1.0850` (1 EUR = 1.0850 USD), `USDJPY 151.20` (1 USD = 151.20 JPY).
- **Cross rates:** converting between two non-USD currencies goes **through USD**.
- **Stale rates:** a rate older than **60 seconds** must not be used. Quoting with one is an error.
- **Spread:** the customer gets the mid rate minus a spread based on the amount's **USD equivalent**:

| USD equivalent of the amount | Spread |
|---|---|
| under $10,000 | 1.00% |
| $10,000 – under $100,000 | 0.50% |
| $100,000 and above | 0.25% |

- **Target amount** = source amount × cross mid rate × (1 − spread), **rounded down** to the target currency's minor unit
  (the customer never receives more than they're owed).
- **Minor units:** USD, EUR, GBP, CHF have 2 decimals; **JPY has 0**; KWD has 3.

## Example

1,000 EUR → JPY: 1,000 × 1.0850 = 1,085.00 USD → × 151.20 = 164,052 JPY mid. USD equivalent $1,085 → 1% spread →
162,411.48 → **¥162,411**.

## Candidate questions

1. Identify anything in the rules that must be clarified before implementation.
2. Explain how you would model rates, currencies and quotes.
3. Outline the conversion and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
