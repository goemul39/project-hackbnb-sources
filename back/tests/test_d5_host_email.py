"""
Tests D5: host emails must not be returned by public routes.
"""
import unittest

from app import app


class D5HostEmailTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_rooms_api_does_not_leak_host_email(self):
        response = self.client.get("/rooms/")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload)
        for room in payload:
            self.assertNotIn("email", room.get("host", {}))


if __name__ == "__main__":
    unittest.main()
