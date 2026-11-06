FIXES = [
    ("edge/breaker.py",
     '''    def record_success(self) -> None:
        if self.state == "half_open":
            self.state = "closed"''',
     '''    def record_success(self) -> None:
        self.failures = 0
        self.state = "closed"'''),
    ("edge/proxy.py",
     '''        if route.external:
            headers["X-Api-Key"] = self._partner_api_key''',
     '''        headers["X-Request-ID"] = request.context["request_id"]
        if route.external:
            headers["X-Api-Key"] = self._partner_api_key'''),
    ("edge/proxy.py",
     '''            headers["X-Api-Key"] = self._partner_api_key
        else:''',
     '''            headers["X-Api-Key"] = self._partner_api_key
            headers.pop("Authorization", None)
        else:'''),
    ("edge/limits.py",
     '''        log.append(now)
        if len(log) > self.limit:
            return Decision(False, 0, max(1, int(log[0] + self.window - now)))
        return Decision(True, self.limit - len(log), 0)''',
     '''        if len(log) >= self.limit:
            return Decision(False, 0, max(1, int(log[0] + self.window - now)))
        log.append(now)
        return Decision(True, self.limit - len(log), 0)'''),
    ("edge/proxy.py",
     '''        last_error = None
        for attempt in range(1, MAX_ATTEMPTS + 1):''',
     '''        last_error = None
        retry_safe = request.method in ("GET", "HEAD", "PUT", "DELETE") or "Idempotency-Key" in headers
        for attempt in range(1, (MAX_ATTEMPTS if retry_safe else 1) + 1):'''),
]
GROUPS = [[0], [1], [2], [3], [4]]
