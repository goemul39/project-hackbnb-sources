import os
import re
import stripe
import requests

STRIPE_SESSION_ID = re.compile(r"cs_(test|live)_[A-Za-z0-9]+")

def create_checkout(reference, name, unit_price, quantity, confirmation_secret):
    """
        Create Stripe checkout
        Documentation: https://docs.stripe.com/checkout/quickstart?client=react&lang=python
    """
    
    stripe.api_key = os.getenv('STRIPE_API_KEY')
    origin_host = os.getenv('APP_ORIGIN_HOST')
    return stripe.checkout.Session.create(
        mode='payment',
        success_url=f"{origin_host}/booking/{reference}?checkout_confirmation_secret={confirmation_secret}",
        cancel_url=origin_host,
        line_items=[
            {
                'quantity': quantity,
                'price_data': {
                    'currency': 'EUR',
                    'unit_amount': round(unit_price * 100),
                    'product_data': {
                        'name': name,
                    },
                },
            },
        ],
    )

def get_checkout_lines(checkout_session_id):
    if not STRIPE_SESSION_ID.fullmatch(checkout_session_id or ""):
        raise ValueError("Invalid checkout session ID")

    url = f"https://api.stripe.com/v1/checkout/sessions/{checkout_session_id}/line_items"

    session = requests.Session()
    session.auth = (os.getenv('STRIPE_API_KEY'), "")
    return session.get(url).json()["data"]


def is_checkout_paid(checkout_session_id):
    """Ask Stripe if the checkout session is paid (False if anything fails)."""
    stripe.api_key = os.getenv('STRIPE_API_KEY')
    try:
        checkout_session = stripe.checkout.Session.retrieve(checkout_session_id)
        # StripeObject is not a dict in recent stripe versions: no .get()
        return checkout_session.payment_status == "paid"
    except Exception:
        return False
