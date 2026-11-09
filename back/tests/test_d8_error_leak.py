"""
Tests D8: internal errors must not leak stack traces.
"""
import unittest

from app import app


class D8ErrorLeakTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_internal_errors_are_generic(self):
        response = self.client.get("/rooms/?category=%27")
        self.assertEqual(response.status_code, 500)
        body = response.get_data(as_text=True)
        self.assertEqual(response.get_json(), {"error": "Internal server error"})
        self.assertNotIn("Traceback", body)
        self.assertNotIn("sqlalchemy", body.lower())


if __name__ == "__main__":
    unittest.main()
