from dataclasses import dataclass, field
from datetime import datetime

from ..errors import NotFound, ValidationError
from ..services.scheduling import SchedulingService
from .serializers import commitment_to_json, meeting_to_json, request_to_json


@dataclass
class Response:
    status: int
    body: dict = field(default_factory=dict)


class CalendarApi:
    def __init__(self, service: SchedulingService):
        self._service = service

    def post_meeting_request(self, headers: dict, body: dict) -> Response:
        requester = headers.get("X-Requester")
        key = headers.get("Idempotency-Key")
        if not requester or not key:
            return Response(400, {"error": "X-Requester and Idempotency-Key headers are required"})
        try:
            req = self._service.submit_request(requester, key, body)
        except ValidationError as e:
            return Response(400, {"error": str(e)})
        return Response(201, request_to_json(req))

    def get_meeting_request(self, request_id: str) -> Response:
        req = self._service.get_request(request_id)
        if req is None:
            return Response(404, {"error": "not found"})
        return Response(200, request_to_json(req))

    def post_run_batch(self, body: dict) -> Response:
        try:
            day = datetime.fromisoformat(body["day"])
        except (KeyError, ValueError):
            return Response(400, {"error": "day must be an ISO date"})
        result = self._service.run_batch(day)
        return Response(200, {"day": result.day, "scheduled": result.scheduled,
                              "unschedulable": result.unschedulable})

    def get_schedule(self, day: str) -> Response:
        commitments, meetings = self._service.schedule_for(datetime.fromisoformat(day))
        return Response(200, {"commitments": [commitment_to_json(c) for c in commitments],
                              "meetings": [meeting_to_json(m) for m in meetings]})
