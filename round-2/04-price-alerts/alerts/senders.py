import threading


class PushSender:
    def send(self, user_id: str, message: str) -> None:
        raise NotImplementedError("push gateway not available in the sandbox")


class RecordingSender:

    def __init__(self):
        self.sent = []
        self._lock = threading.Lock()

    def send(self, user_id: str, message: str) -> None:
        with self._lock:
            self.sent.append((user_id, message))
