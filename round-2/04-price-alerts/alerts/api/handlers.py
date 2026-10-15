from dataclasses import dataclass, field

from ..errors import AlertsError
from ..services.alert_service import AlertService


@dataclass
class Response:
    status: int
    body: dict = field(default_factory=dict)


class AlertsApi:
    def __init__(self, service: AlertService):
        self._service = service

    def post_alert(self, user_id: str, body: dict) -> Response:
        try:
            a = self._service.create_alert(user_id, body)
        except AlertsError as e:
            return Response(e.status, {"error": str(e)})
        return Response(201, {"alert_id": a.alert_id, "symbol": a.symbol, "direction": a.direction,
                              "threshold": str(a.threshold)})

    def delete_alert(self, user_id: str, alert_id: int) -> Response:
        try:
            self._service.delete_alert(user_id, alert_id)
        except AlertsError as e:
            return Response(e.status, {"error": str(e)})
        return Response(204)

    def get_alerts(self, user_id: str) -> Response:
        return Response(200, {"alerts": [{"alert_id": a.alert_id, "symbol": a.symbol, "direction": a.direction,
                                          "threshold": str(a.threshold)} for a in self._service.list_alerts(user_id)]})
