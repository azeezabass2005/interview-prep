FIXES = [
    ("gateway.py", "        for route in self.routes:\n            if path.startswith(route.prefix):\n                return route\n        return None",
     "        matches = [r for r in self.routes if path.startswith(r.prefix)]\n        return max(matches, key=lambda r: len(r.prefix)) if matches else None"),
    ("gateway.py", "        if used + 1 > PLAN_LIMITS[self.keys[key]]:", "        if used + route.cost > PLAN_LIMITS[self.keys[key]]:"),
    ("gateway.py", "            retry = int((now - window).total_seconds())", "            retry = int((window + timedelta(minutes=1) - now).total_seconds())"),
    ("gateway.py", "        self.usage[(key, window)] = used + 1", "        self.usage[(key, window)] = used + route.cost"),
    ("gateway.py", "        if key not in self.keys:\n            return 401, {}\n        if ip in self.blocked:\n            return 403, {}",
     "        if ip in self.blocked:\n            return 403, {}\n        if key not in self.keys:\n            return 401, {}"),
    ("gateway.py", "                breaker.failures = 0\n        return status, {}",
     "                breaker.failures = 0\n        else:\n            breaker.failures = 0\n        return status, {}"),
]
