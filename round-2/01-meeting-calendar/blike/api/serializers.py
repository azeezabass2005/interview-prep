from ..models import Commitment, Meeting, MeetingRequest


def request_to_json(req: MeetingRequest) -> dict:
    return {
        "request_id": req.request_id,
        "title": req.title,
        "sender": req.sender,
        "duration_minutes": req.duration_minutes,
        "urgency": req.urgency,
        "earliest": req.earliest.isoformat(),
        "latest": req.latest.isoformat(),
        "score": req.score,
        "status": req.status,
    }


def meeting_to_json(m: Meeting) -> dict:
    return {"meeting_id": m.meeting_id, "request_id": m.request_id, "title": m.title,
            "start": m.start.isoformat(), "end": m.end.isoformat()}


def commitment_to_json(c: Commitment) -> dict:
    return {"commitment_id": c.commitment_id, "title": c.title, "start": c.start.isoformat(),
            "end": c.end.isoformat(), "protected": c.protected}
