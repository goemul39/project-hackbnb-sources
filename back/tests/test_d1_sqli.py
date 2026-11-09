"""
Tests D1: the room category filter must not be injectable.
"""
import unittest

from app import app


class D1SqlInjectionTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_sqli_in_category_is_rejected(self):
        payloads = [
            "hut' OR 1=1 -- ",
            "test' UNION SELECT bookings.id, bookings.reference, "
            "bookings.checkout_confirmation_secret, bookings.stripe_checkout_session_id, "
            "0, 0, 0, 0 FROM bookings -- ",
        ]
        for payload in payloads:
            response = self.client.get("/rooms/", query_string={"category": payload})
            self.assertEqual(response.status_code, 400)

    def test_valid_category_still_works(self):
        response = self.client.get("/rooms/", query_string={"category": "hut"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(room["category"] == "hut" for room in response.get_json()))


if __name__ == "__main__":
    unittest.main()
