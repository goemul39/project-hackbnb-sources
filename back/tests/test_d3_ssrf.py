"""
Tests D3: the checkout-lines route must not let the client choose the Stripe
URL. The session ID comes from the booking.
"""
import unittest
from unittest.mock import patch

from app import app
from database.init import db
from api.bookings.bookings_models import Booking


class D3SsrfTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()
        with app.app_context():
            Booking.query.filter_by(reference="D3TEST01").delete()
            db.session.add(Booking(
                reference="D3TEST01",
                arrival_date="2026-12-01",
                departure_date="2026-12-03",
                guests_count=1,
                total_price=340.0,
                checkout_confirmation_secret="secret",
                stripe_checkout_session_id="cs_test_VALID123",
                is_paid=True,
                room_id=1,
            ))
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            Booking.query.filter_by(reference="D3TEST01").delete()
            db.session.commit()

    def test_client_session_id_is_ignored(self):
        captured = {}

        def fake_get_checkout_lines(session_id):
            captured["session_id"] = session_id
            return [{"id": "li_test", "amount_total": 34000}]

        with patch("api.bookings.bookings_api.get_checkout_lines", fake_get_checkout_lines):
            response = self.client.get(
                "/bookings/D3TEST01/checkout-lines",
                query_string={"checkout_session_id": "../../customers#"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(captured["session_id"], "cs_test_VALID123")
        self.assertEqual(response.get_json(), [{"id": "li_test", "amount_total": 34000}])

    def test_invalid_stored_session_id_is_rejected(self):
        with app.app_context():
            booking = Booking.query.filter_by(reference="D3TEST01").first()
            booking.stripe_checkout_session_id = "../../customers#"
            db.session.commit()

        response = self.client.get("/bookings/D3TEST01/checkout-lines")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
