from ..adapters.channels import DeliveryError
from ..clock import iso
from ..models import Delivery
from ..privacy import mask


class AlertEngine:
    """Turns price ticks into deliveries, and sends deliveries from the worker."""

    def __init__(self, rules, users, deliveries, queue, sms, email, clock, ids, logger, metrics):
        self._rules = rules
        self._users = users
        self._deliveries = deliveries
        self._queue = queue
        self._sms = sms
        self._email = email
        self._clock = clock
        self._ids = ids
        self._logger = logger
        self._metrics = metrics

    def on_price(self, symbol: str, price: float) -> int:
        fired = 0
        now = iso(self._clock.now())
        for rule in self._rules.active_for_symbol(symbol.upper()):
            if not rule.fires_at(price) or not self._rules.mark_triggered(rule.id, now):
                continue
            user = self._users.get(rule.user_id)
            recipient = user.phone if rule.channel == "sms" else user.email
            message = f"{rule.symbol} is {rule.direction} {rule.threshold:g}: now {price:g}"
            delivery = Delivery(self._ids.new("dlv"), rule.id, user.id, rule.channel, recipient, message, "queued", None, None,
                                now, None)
            self._deliveries.add(delivery)
            self._queue.enqueue("deliver", {"delivery_id": delivery.id}, max_attempts=5)
            fired += 1
        return fired

    def deliver(self, payload: dict) -> None:
        d = self._deliveries.get(payload["delivery_id"])
        if d is None or d.status != "queued":
            return
        try:
            if d.channel == "sms":
                provider_id = self._sms.send(d.recipient, d.message)
            else:
                provider_id = self._email.send(d.recipient, "Price alert", d.message)
        except DeliveryError as e:
            self._logger.warning("delivery_failed", delivery_id=d.id, channel=d.channel, to=mask(d.recipient),
                                 retryable=e.retryable, error=str(e))
            if e.retryable:
                raise
            self._deliveries.mark(d.id, "failed", error=str(e))
            self._metrics.increment("deliveries_total", channel=d.channel, outcome="failed")
            return
        self._deliveries.mark(d.id, "sent", provider_id=provider_id, sent_at=iso(self._clock.now()))
        self._metrics.increment("deliveries_total", channel=d.channel, outcome="sent")
        self._logger.info("delivery_sent", delivery_id=d.id, channel=d.channel, to=mask(d.recipient))
