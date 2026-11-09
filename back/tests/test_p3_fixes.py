"""
Non-regression tests for the P3 fixes (D4, D5, D8).

Run from the back/ directory:
    python3 -m unittest discover -s tests -v
"""
import hashlib
import time
import unittest
from unittest.mock import patch

from app import app
from api.bookings.bookings_models import Booking
from database.init import db


class FakeCheckoutSession:
    id = "cs_test_fake_session"
    url = "https://checkout.stripe.com/c/pay/cs_test_fake_session"


class P3FixesTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def _create_booking(self):
        with patch("api.bookings.bookings_api.create_checkout", return_value=FakeCheckoutSession()):
            response = self.client.post("/bookings/", json={
                "roomId": 2,
                "arrivalDate": "2026-12-01",
                "departureDate": "2026-12-03",
                "guestsCount": 1,
            })
        self.assertEqual(response.status_code, 200)
        return response.get_json()

    def test_d4_predictable_timestamp_secret_is_rejected(self):
        booking = self._create_booking()

        # The old implementation used sha512(str(int(time.time()))).
        predictable = hashlib.sha512(str(int(time.time())).encode()).hexdigest()
        response = self.client.post(
            f"/bookings/{booking['reference']}/confirm-checkout",
            json={"confirmationSecret": predictable},
        )
        self.assertEqual(response.status_code, 422)

    def test_d4_valid_secret_but_unpaid_session_is_rejected(self):
        booking = self._create_booking()
        with app.app_context():
            stored = Booking.query.filter_by(reference=booking["reference"]).first()
            secret = stored.checkout_confirmation_secret

        self.assertGreaterEqual(len(secret), 32)
        with patch("api.bookings.bookings_api.is_checkout_paid", return_value=False):
            response = self.client.post(
                f"/bookings/{booking['reference']}/confirm-checkout",
                json={"confirmationSecret": secret},
            )
        self.assertEqual(response.status_code, 402)

    def test_d4_paid_session_with_valid_secret_is_accepted(self):
        booking = self._create_booking()
        with app.app_context():
            secret = Booking.query.filter_by(reference=booking["reference"]).first().checkout_confirmation_secret

        with patch("api.bookings.bookings_api.is_checkout_paid", return_value=True):
            response = self.client.post(
                f"/bookings/{booking['reference']}/confirm-checkout",
                json={"confirmationSecret": secret},
            )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["success"])

    def test_d5_rooms_api_does_not_leak_host_email(self):
        response = self.client.get("/rooms/")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload)
        for room in payload:
            self.assertNotIn("email", room.get("host", {}))

if __name__ == "__main__":
    unittest.main()
