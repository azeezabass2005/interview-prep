from ..config import INTERNAL_DOMAIN, SENDER_WEIGHTS, URGENCY_WEIGHTS, VIP_SENDERS


class ScoringService:
    """Priority score for a meeting request. Higher is more important."""

    def sender_class(self, sender: str) -> str:
        if sender in VIP_SENDERS:
            return "vip"
        if sender.endswith(INTERNAL_DOMAIN):
            return "internal"
        return "external"

    def score(self, sender: str, urgency: str) -> int:
        return SENDER_WEIGHTS[self.sender_class(sender)] + URGENCY_WEIGHTS[urgency]
