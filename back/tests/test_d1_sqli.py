"""
Tests D1: the room category filter must not be injectable.
"""
import unittest

from app import app


class D1SqlInjectionTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_sqli_in_category_returns_no_room(self):
        payloads = [
            "hut' OR 1=1 -- ",
            "test' UNION SELECT bookings.id, bookings.reference, "
            "bookings.checkout_confirmation_secret, bookings.stripe_checkout_session_id, "
            "0, 0, 0, 0 FROM bookings -- ",
        ]
        for payload in payloads:
            response = self.client.get("/rooms/", query_string={"category": payload})
            # The payload is treated as plain text: no room has this category
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json(), [])

    def test_valid_category_still_works(self):
        response = self.client.get("/rooms/", query_string={"category": "hut"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(room["category"] == "hut" for room in response.get_json()))

    def test_front_categories_without_rooms_return_empty_list(self):
        # "camping" and "desert" are filter buttons in the front but have no room
        for category in ["camping", "desert"]:
            response = self.client.get("/rooms/", query_string={"category": category})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json(), [])


if __name__ == "__main__":
    unittest.main()
