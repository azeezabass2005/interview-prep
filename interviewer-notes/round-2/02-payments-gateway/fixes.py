FIXES = [
    ("gateway/adapters/paystream.py", "    def _post(self, path: str, payload: dict) -> dict:",
     "    def _post(self, path: str, payload: dict, idempotency_key: str) -> dict:"),
    ("gateway/adapters/paystream.py", '"Idempotency-Key": str(uuid.uuid4()),', '"Idempotency-Key": idempotency_key,'),
    ("gateway/adapters/paystream.py", '"description": description, "metadata": {"payment_id": payment_id}})',
     '"description": description, "metadata": {"payment_id": payment_id}}, f"charge-{payment_id}")'),
    ("gateway/adapters/paystream.py", '"metadata": {"refund_id": refund_id}})',
     '"metadata": {"refund_id": refund_id}}, f"refund-{refund_id}")'),
    ("gateway/adapters/paystream.py",
     "            if result.status >= 400:\n                last = result\n                continue\n",
     "            if result.status >= 500:\n                last = result\n                continue\n"
     "            if result.status >= 400:\n                last = result\n                break\n"),
    ("gateway/adapters/webhooks.py",
     '''    event = json.loads(body)
    canonical = json.dumps(event, separators=(",", ":")).encode()
    if not hmac.compare_digest(sign(secret, timestamp, canonical), signature):
        raise Unauthorized("bad webhook signature")
    return event''',
     '''    if not hmac.compare_digest(sign(secret, timestamp, body), signature):
        raise Unauthorized("bad webhook signature")
    return json.loads(body)'''),
    ("gateway/money.py", "    return int(value * 100)", "    return int(value * (Decimal(10) ** exponent))"),
    ("gateway/services/payments.py", "from ..adapters.paystream import PaystreamDeclined",
     "from ..adapters.paystream import PaystreamDeclined, PaystreamUnavailable"),
    ("gateway/services/payments.py", "from ..errors import Conflict, NotFound, ValidationError",
     "from ..errors import Conflict, NotFound, ServiceUnavailable, ValidationError"),
    ("gateway/services/payments.py",
     "            return self._payments.get(principal.org_id, payment.id), True\n        status =",
     "            return self._payments.get(principal.org_id, payment.id), True\n"
     "        except PaystreamUnavailable:\n"
     "            self._payments.update(payment.id, iso(self._clock.now()), status=\"failed\", failure_code=\"processor_unavailable\")\n"
     "            raise ServiceUnavailable(\"payment processor unavailable, retry later\", retry_after=30)\n"
     "        status ="),
]
GROUPS = [[0, 1, 2, 3], [4], [5], [6], [7, 8, 9]]
