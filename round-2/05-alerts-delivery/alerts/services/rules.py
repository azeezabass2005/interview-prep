from ..auth import Principal
from ..clock import iso
from ..errors import NotFound, ValidationError
from ..models import Rule

MAX_RULES_PER_USER = 50


class RuleService:
    def __init__(self, rules, users, clock, ids):
        self._rules = rules
        self._users = users
        self._clock = clock
        self._ids = ids

    def list(self, principal: Principal, user_id: str | None = None) -> list[Rule]:
        return self._rules.for_user(user_id or principal.user_id)

    def create(self, principal: Principal, data: dict) -> Rule:
        direction, channel = data.get("direction"), data.get("channel", "email")
        if direction not in ("above", "below"):
            raise ValidationError("direction must be above or below")
        if channel not in ("sms", "email"):
            raise ValidationError("channel must be sms or email")
        try:
            threshold = float(data["threshold"])
        except (KeyError, TypeError, ValueError) as e:
            raise ValidationError("threshold must be a number") from e
        symbol = str(data.get("symbol", "")).strip().upper()
        if not symbol or threshold <= 0:
            raise ValidationError("symbol and a positive threshold are required")
        user = self._users.get(principal.user_id)
        if channel == "sms" and not (user and user.phone):
            raise ValidationError("add a phone number before creating SMS alerts")
        if len(self._rules.for_user(principal.user_id)) >= MAX_RULES_PER_USER:
            raise ValidationError(f"at most {MAX_RULES_PER_USER} alerts per user")
        rule = Rule(self._ids.new("rule"), principal.user_id, symbol, direction, threshold, channel, True,
                    iso(self._clock.now()), None)
        self._rules.add(rule)
        return rule

    def delete(self, principal: Principal, rule_id: str) -> None:
        rule = self._rules.get(rule_id)
        if rule is None or rule.user_id != principal.user_id:
            raise NotFound("alert not found")
        self._rules.delete(rule_id)
