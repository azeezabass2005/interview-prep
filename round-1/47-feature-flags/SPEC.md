# Feature Flags

Product teams roll out features gradually with feature flags. `flags.py` stores flag definitions and decides whether a flag is on for a user.

## Flags

A flag has a key and:
- `enabled` (the kill switch),
- an **allowlist** and a **denylist** of user ids,
- **country targeting**: a list of country codes (compared **case-insensitively**),
- a **rollout percentage** (0–100),
- optional **prerequisite** flags that must also be on for the user.

## Evaluation order (first match wins)

1. Unknown flag, or flag disabled → **off**.
2. Any prerequisite flag off for this user → **off**.
3. User on the denylist → **off** (even if also on the allowlist).
4. User on the allowlist → **on**.
5. User's country in the targeting list → **on**.
6. Rollout: **bucket** = first 8 hex digits of `sha256("<flag key>:<user id>")` as an integer, mod 100. **On** if bucket < percentage.
   (Including the flag key means each flag rolls out to a different set of users.) 0% is nobody, 100% is everybody.

## Admin and reporting

- `evaluate` works like `is_on` and also counts exposures (how many evaluations were on/off per flag); `evaluate_all` evaluates every flag
  for one user.
- `set_rollout` changes the percentage (0–100); `kill` disables a flag.
- A flag that is a prerequisite of another flag **can't be removed** until the dependent flags are removed.

## Example

`new-chart` enabled, allowlist [ana], rollout 0%. Ana → **on**. Ben (country GB, no targeting) → **off**.
