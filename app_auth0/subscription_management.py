from enum import Enum
from datetime import datetime, timedelta
import stripe
from supabase import create_client
import os
from dotenv import load_dotenv
import logging
from typing import Optional, Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Initialize Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

class SubscriptionTier(Enum):
    FREE = 'free'
    BASIC = 'basic'
    PRO = 'pro'
    ENTERPRISE = 'enterprise'

class SubscriptionStatus(Enum):
    ACTIVE = 'active'
    PAST_DUE = 'past_due'
    CANCELED = 'canceled'
    TRIALING = 'trialing'
    UNPAID = 'unpaid'

# Define features for each tier
TIER_FEATURES = {
    SubscriptionTier.FREE: {
        'max_decks': 3,
        'max_cards_per_deck': 50,
        'can_create_live_decks': False,
        'can_edit_live_decks': False,
        'can_share_decks': False,
        'can_use_ai_features': False,
        'can_use_media': False,
        'can_use_analytics': False,
        'can_use_export': False,
        'can_use_import': False,
        'can_use_api': False,
        'can_use_priority_support': False
    },
    SubscriptionTier.BASIC: {
        'max_decks': 10,
        'max_cards_per_deck': 200,
        'can_create_live_decks': True,
        'can_edit_live_decks': False,
        'can_share_decks': True,
        'can_use_ai_features': False,
        'can_use_media': True,
        'can_use_analytics': True,
        'can_use_export': True,
        'can_use_import': True,
        'can_use_api': False,
        'can_use_priority_support': False
    },
    SubscriptionTier.PRO: {
        'max_decks': 50,
        'max_cards_per_deck': 1000,
        'can_create_live_decks': True,
        'can_edit_live_decks': True,
        'can_share_decks': True,
        'can_use_ai_features': True,
        'can_use_media': True,
        'can_use_analytics': True,
        'can_use_export': True,
        'can_use_import': True,
        'can_use_api': True,
        'can_use_priority_support': True
    },
    SubscriptionTier.ENTERPRISE: {
        'max_decks': float('inf'),
        'max_cards_per_deck': float('inf'),
        'can_create_live_decks': True,
        'can_edit_live_decks': True,
        'can_share_decks': True,
        'can_use_ai_features': True,
        'can_use_media': True,
        'can_use_analytics': True,
        'can_use_export': True,
        'can_use_import': True,
        'can_use_api': True,
        'can_use_priority_support': True
    }
}

# Stripe product IDs for each tier
STRIPE_PRODUCTS = {
    SubscriptionTier.BASIC: os.getenv('STRIPE_BASIC_PRODUCT_ID'),
    SubscriptionTier.PRO: os.getenv('STRIPE_PRO_PRODUCT_ID'),
    SubscriptionTier.ENTERPRISE: os.getenv('STRIPE_ENTERPRISE_PRODUCT_ID')
}

class SubscriptionManager:
    def __init__(self):
        self.stripe = stripe
        self.supabase = supabase

    def create_subscription(self, user_id: str, tier: SubscriptionTier, payment_method_id: str) -> Dict:
        """Create a new subscription for a user"""
        try:
            # Create or get Stripe customer
            customer = self._get_or_create_stripe_customer(user_id)
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{'price': STRIPE_PRODUCTS[tier]}],
                payment_behavior='default_incomplete',
                payment_settings={'save_default_payment_method': 'on_subscription'},
                expand=['latest_invoice.payment_intent'],
            )
            
            # Store subscription in database
            subscription_data = {
                'id': subscription.id,
                'user_id': user_id,
                'tier': tier.value,
                'status': subscription.status,
                'current_period_start': datetime.fromtimestamp(subscription.current_period_start).isoformat(),
                'current_period_end': datetime.fromtimestamp(subscription.current_period_end).isoformat(),
                'stripe_customer_id': customer.id,
                'stripe_subscription_id': subscription.id,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table('subscriptions').insert(subscription_data).execute()
            
            return {
                'subscription_id': subscription.id,
                'client_secret': subscription.latest_invoice.payment_intent.client_secret
            }
            
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            raise

    def update_subscription(self, subscription_id: str, tier: SubscriptionTier) -> Dict:
        """Update an existing subscription"""
        try:
            # Update Stripe subscription
            subscription = stripe.Subscription.modify(
                subscription_id,
                items=[{'price': STRIPE_PRODUCTS[tier]}],
                proration_behavior='always_invoice'
            )
            
            # Update database
            subscription_data = {
                'tier': tier.value,
                'status': subscription.status,
                'current_period_start': datetime.fromtimestamp(subscription.current_period_start).isoformat(),
                'current_period_end': datetime.fromtimestamp(subscription.current_period_end).isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table('subscriptions').update(subscription_data).eq('id', subscription_id).execute()
            
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Error updating subscription: {e}")
            raise

    def cancel_subscription(self, subscription_id: str) -> Dict:
        """Cancel a subscription"""
        try:
            # Cancel Stripe subscription
            subscription = stripe.Subscription.delete(subscription_id)
            
            # Update database
            subscription_data = {
                'status': SubscriptionStatus.CANCELED.value,
                'canceled_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table('subscriptions').update(subscription_data).eq('id', subscription_id).execute()
            
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Error canceling subscription: {e}")
            raise

    def get_subscription(self, user_id: str) -> Optional[Dict]:
        """Get user's current subscription"""
        try:
            result = self.supabase.table('subscriptions').select('*').eq('user_id', user_id).eq('status', SubscriptionStatus.ACTIVE.value).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting subscription: {e}")
            return None

    def get_subscription_tier(self, user_id: str) -> SubscriptionTier:
        """Get user's current subscription tier"""
        subscription = self.get_subscription(user_id)
        if subscription:
            return SubscriptionTier(subscription['tier'])
        return SubscriptionTier.FREE

    def has_feature_access(self, user_id: str, feature: str) -> bool:
        """Check if user has access to a specific feature"""
        tier = self.get_subscription_tier(user_id)
        return TIER_FEATURES[tier].get(feature, False)

    def _get_or_create_stripe_customer(self, user_id: str) -> stripe.Customer:
        """Get or create a Stripe customer for a user"""
        try:
            # Check if user already has a Stripe customer ID
            user_result = self.supabase.table('users').select('stripe_customer_id').eq('id', user_id).execute()
            
            if user_result.data and user_result.data[0].get('stripe_customer_id'):
                return stripe.Customer.retrieve(user_result.data[0]['stripe_customer_id'])
            
            # Create new Stripe customer
            user_data = self.supabase.table('users').select('email, name').eq('id', user_id).execute()
            if not user_data.data:
                raise ValueError("User not found")
                
            customer = stripe.Customer.create(
                email=user_data.data[0]['email'],
                name=user_data.data[0].get('name'),
                metadata={'user_id': user_id}
            )
            
            # Update user with Stripe customer ID
            self.supabase.table('users').update({
                'stripe_customer_id': customer.id,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', user_id).execute()
            
            return customer
            
        except Exception as e:
            logger.error(f"Error getting/creating Stripe customer: {e}")
            raise

    def handle_webhook(self, event: Dict) -> Dict:
        """Handle Stripe webhook events"""
        try:
            event_type = event['type']
            
            if event_type == 'customer.subscription.updated':
                subscription = event['data']['object']
                self._update_subscription_status(subscription)
            elif event_type == 'customer.subscription.deleted':
                subscription = event['data']['object']
                self._cancel_subscription(subscription)
            elif event_type == 'invoice.payment_succeeded':
                invoice = event['data']['object']
                self._handle_successful_payment(invoice)
            elif event_type == 'invoice.payment_failed':
                invoice = event['data']['object']
                self._handle_failed_payment(invoice)
            
            return {'status': 'success'}
            
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return {'status': 'error', 'message': str(e)}

    def _update_subscription_status(self, subscription: Dict):
        """Update subscription status in database"""
        try:
            subscription_data = {
                'status': subscription['status'],
                'current_period_start': datetime.fromtimestamp(subscription['current_period_start']).isoformat(),
                'current_period_end': datetime.fromtimestamp(subscription['current_period_end']).isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            self.supabase.table('subscriptions').update(subscription_data).eq('stripe_subscription_id', subscription['id']).execute()
            
        except Exception as e:
            logger.error(f"Error updating subscription status: {e}")
            raise

    def _cancel_subscription(self, subscription: Dict):
        """Handle subscription cancellation"""
        try:
            subscription_data = {
                'status': SubscriptionStatus.CANCELED.value,
                'canceled_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            self.supabase.table('subscriptions').update(subscription_data).eq('stripe_subscription_id', subscription['id']).execute()
            
        except Exception as e:
            logger.error(f"Error canceling subscription: {e}")
            raise

    def _handle_successful_payment(self, invoice: Dict):
        """Handle successful payment"""
        try:
            subscription_id = invoice['subscription']
            subscription_data = {
                'status': SubscriptionStatus.ACTIVE.value,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            self.supabase.table('subscriptions').update(subscription_data).eq('stripe_subscription_id', subscription_id).execute()
            
        except Exception as e:
            logger.error(f"Error handling successful payment: {e}")
            raise

    def _handle_failed_payment(self, invoice: Dict):
        """Handle failed payment"""
        try:
            subscription_id = invoice['subscription']
            subscription_data = {
                'status': SubscriptionStatus.PAST_DUE.value,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            self.supabase.table('subscriptions').update(subscription_data).eq('stripe_subscription_id', subscription_id).execute()
            
        except Exception as e:
            logger.error(f"Error handling failed payment: {e}")
            raise 