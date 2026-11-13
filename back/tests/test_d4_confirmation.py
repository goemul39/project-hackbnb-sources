"""
Tests D4: the confirmation secret must be random.
"""
import hashlib
import time
import unittest
from unittest.mock import patch

from app import app
from api.bookings.bookings_models import Booking


class FakeCheckoutSession:
    id = "cs_test_fake_session"
    url = "https://checkout.stripe.com/c/pay/cs_test_fake_session"


class D4ConfirmationTestCase(unittest.TestCase):
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
    def test_d4_non_ascii_secret_is_rejected_cleanly(self):
        booking = self._create_booking()
        response = self.client.post(
            f"/bookings/{booking['reference']}/confirm-checkout",
            json={"confirmationSecret": "é"},
        )
        self.assertEqual(response.status_code, 422)


class D4IsCheckoutPaidTestCase(unittest.TestCase):
    """Run the real is_checkout_paid with a fake Stripe response."""

    def _session(self, payment_status):
        import stripe
        return stripe.checkout.Session.construct_from(
            {"id": "cs_test_fake_session", "payment_status": payment_status}, "sk_test"
        )

    def test_paid_session(self):
        from services.stripe import is_checkout_paid
        with patch("stripe.checkout.Session.retrieve", return_value=self._session("paid")):
            self.assertTrue(is_checkout_paid("cs_test_fake_session"))

    def test_unpaid_session(self):
        from services.stripe import is_checkout_paid
        with patch("stripe.checkout.Session.retrieve", return_value=self._session("unpaid")):
            self.assertFalse(is_checkout_paid("cs_test_fake_session"))

    def test_stripe_error(self):
        from services.stripe import is_checkout_paid
        with patch("stripe.checkout.Session.retrieve", side_effect=Exception("down")):
            self.assertFalse(is_checkout_paid("cs_test_fake_session"))


if __name__ == "__main__":
    unittest.main()
