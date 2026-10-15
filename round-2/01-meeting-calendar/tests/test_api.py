import unittest

from tests.helpers import TempDb, headers, make_api, payload


class TestMeetingRequestApi(unittest.TestCase):
    def setUp(self):
        self.tmp = TempDb()
        self.api = make_api(self.tmp)

    def tearDown(self):
        self.tmp.cleanup()

    def test_create_request(self):
        resp = self.api.post_meeting_request(headers(), payload())
        self.assertEqual(resp.status, 201)
        self.assertEqual(resp.body["status"], "PENDING")

    def test_headers_required(self):
        resp = self.api.post_meeting_request({}, payload())
        self.assertEqual(resp.status, 400)

    def test_validation(self):
        resp = self.api.post_meeting_request(headers(), payload(duration=17))
        self.assertEqual(resp.status, 400)

    def test_sequential_retry_returns_same_request(self):
        first = self.api.post_meeting_request(headers(key="abc"), payload())
        second = self.api.post_meeting_request(headers(key="abc"), payload())
        self.assertEqual(first.body["request_id"], second.body["request_id"])

    def test_get_unknown(self):
        self.assertEqual(self.api.get_meeting_request("req_nope").status, 404)


if __name__ == "__main__":
    unittest.main()
