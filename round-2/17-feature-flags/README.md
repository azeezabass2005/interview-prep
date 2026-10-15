# Feature Flag Service

Product teams gate features behind flags. Every API instance embeds an evaluator that answers "is flag X on for user U?" thousands of times
a second, so each instance **caches** flag definitions for up to 30 seconds. Admins change flags through the admin API on any instance.

Pick one ticket from `tickets/`, make a bounded change and prove it. One ticket done properly is a full pass.

## Running

```
python -m unittest discover -s tests -v
```

## Layout

```
flags/app.py                    Instance: wires repo, cache, evaluator and admin for one process
flags/api/handlers.py           FlagsApi: evaluate, admin updates
flags/services/evaluator.py     Evaluator.is_enabled(flag, user, default)
flags/services/admin.py         FlagAdmin: create / update / override / archive
flags/services/bucketing.py     percentage-rollout buckets
flags/cache.py                  FlagCache (per process, TTL 30 s)
flags/repositories/flags.py     flags, overrides, rules
flags/db.py, clock.py, models.py, config.py
```

## Evaluation order (first match wins)

1. Flag unknown or **archived** → the caller's `default`.
2. Flag **disabled** → off.
3. **User override** (explicit per-user on/off).
4. **Segment rules**, in position order (e.g. `country == "GB"` → on).
5. **Percentage rollout**: the user is in a bucket 0–99. **The same user always lands in the same bucket for a given flag, on every instance,
   forever.** Users in buckets below `rollout_percent` are on.
6. Otherwise off.

**Freshness:** a change is visible **immediately** on the instance that made it, and within **30 s** everywhere else.
