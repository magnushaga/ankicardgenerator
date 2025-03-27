import stripe
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

stripe.api_key = "sk_test_51R7KRb6tFPfonozFxxReAMni7aBKmRmm7aqtSW0CG0vqentnpuCoj9m5o7vakTDDbsIMnvgG6lHXpf4zhfkkf9Cy006zusyuql"
STRIPE_PUBLISHABLE_KEY = "pk_test_51R7KRb6tFPfonozFgVdCwxy9Txk9iTjQYljXpMb8ppTQCIPLnMZl1SiUtrEYem4ENJkKvDuwlE32EDfrQaxxJHOc00d9rJ6evM"

def create_checkout_session(email):
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=email,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'StudyQuant Subscription',
                        'description': 'Monthly subscription to StudyQuant'
                    },
                    'unit_amount': 100,  # $1.00 in cents
                    'recurring': {
                        'interval': 'month'
                    }
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url='http://localhost:5173/profile?payment=success',
            cancel_url='http://localhost:5173/profile?payment=cancelled',
        )
        logger.debug(f"Created checkout session: {checkout_session.id}")
        return checkout_session
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        raise

def create_customer_portal_session(customer_id):
    try:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url='http://localhost:5173/account'
        )
        return session
    except Exception as e:
        logger.error(f"Error creating customer portal session: {str(e)}")
        raise 