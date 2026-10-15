from dataclasses import dataclass, field

from ..app import Instance
from ..models import User


@dataclass
class Response:
    status: int
    body: dict = field(default_factory=dict)


class FlagsApi:
    def __init__(self, instance: Instance):
        self._i = instance

    def get_evaluation(self, flag_key: str, user_id: str, attributes=None, default=False) -> Response:
        on = self._i.evaluator.is_enabled(flag_key, User(user_id, attributes or {}), default)
        return Response(200, {"flag": flag_key, "user": user_id, "on": on})

    def put_flag(self, flag_key: str, body: dict) -> Response:
        try:
            self._i.admin.save_flag(flag_key, body.get("enabled", True), body.get("rollout_percent", 0))
        except ValueError as e:
            return Response(400, {"error": str(e)})
        return Response(200, {"flag": flag_key})
