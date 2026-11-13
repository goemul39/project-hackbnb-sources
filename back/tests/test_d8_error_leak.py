"""
Tests D8: internal errors must not leak stack traces.
"""
import unittest
from unittest.mock import patch

from app import app


class D8ErrorLeakTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_internal_errors_are_generic(self):
        # Force an unexpected error, without relying on another vulnerability
        with patch("api.rooms.rooms_api.Room") as fake_room:
            fake_room.query.all.side_effect = RuntimeError("boom secret detail")
            response = self.client.get("/rooms/")

        self.assertEqual(response.status_code, 500)
        body = response.get_data(as_text=True)
        self.assertEqual(response.get_json(), {"error": "Internal server error"})
        self.assertNotIn("Traceback", body)
        self.assertNotIn("boom secret detail", body)

    def test_internal_errors_are_logged(self):
        with patch("api.rooms.rooms_api.Room") as fake_room:
            fake_room.query.all.side_effect = RuntimeError("boom secret detail")
            with self.assertLogs(app.logger, level="ERROR") as logs:
                self.client.get("/rooms/")

        self.assertIn("boom secret detail", "\n".join(logs.output))


if __name__ == "__main__":
    unittest.main()
