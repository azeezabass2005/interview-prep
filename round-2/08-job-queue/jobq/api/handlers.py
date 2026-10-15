from dataclasses import dataclass, field

from ..errors import QueueError
from ..models import Job
from ..services.queue import JobQueue


@dataclass
class Response:
    status: int
    body: dict = field(default_factory=dict)


def job_json(j: Job) -> dict:
    return {"job_id": j.job_id, "kind": j.kind, "status": j.status, "attempts": j.attempts,
            "max_attempts": j.max_attempts, "run_at": j.run_at.isoformat() + "Z", "last_error": j.last_error}


class QueueApi:
    def __init__(self, queue: JobQueue):
        self._queue = queue

    def post_job(self, body: dict) -> Response:
        try:
            job_id = self._queue.submit(body.get("kind"), body.get("payload", {}), body.get("run_at"),
                                        body.get("max_attempts", 5))
        except QueueError as e:
            return Response(e.status, {"error": str(e)})
        return Response(201, {"job_id": job_id})

    def get_job(self, job_id: int) -> Response:
        try:
            return Response(200, job_json(self._queue.get(job_id)))
        except QueueError as e:
            return Response(e.status, {"error": str(e)})

    def get_dead_letters(self) -> Response:
        return Response(200, {"jobs": [job_json(j) for j in self._queue.dead_letters()]})
