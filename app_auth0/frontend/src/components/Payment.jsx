import React, { useState, useEffect } from 'react';
import { loadStripe } from '@stripe/stripe-js';

const Payment = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stripe, setStripe] = useState(null);

  useEffect(() => {
    // Fetch the Stripe publishable key from the backend
    const initializeStripe = async () => {
      try {
        const response = await fetch('http://localhost:5001/config');
        const { publishableKey } = await response.json();
        const stripeInstance = await loadStripe(publishableKey);
        setStripe(stripeInstance);
      } catch (err) {
        setError('Failed to initialize Stripe');
        console.error('Stripe initialization error:', err);
      }
    };

    initializeStripe();
  }, []);

  const handleSubscribe = async (priceId) => {
    setLoading(true);
    setError(null);

    try {
      // Get user email from Auth0
      const token = sessionStorage.getItem('access_token');
      const userResponse = await fetch('http://localhost:5001/userinfo', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const userData = await userResponse.json();

      // Create checkout session
      const response = await fetch('http://localhost:5001/create-checkout-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          priceId,
          email: userData.email,
        }),
      });

      const { sessionId } = await response.json();
      
      // Redirect to Stripe Checkout
      const result = await stripe.redirectToCheckout({
        sessionId,
      });

      if (result.error) {
        throw new Error(result.error.message);
      }
    } catch (err) {
      setError(err.message);
      console.error('Payment error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="payment-container">
      <h2>Choose Your Plan</h2>
      {error && <div className="error-message">{error}</div>}
      
      <div className="pricing-plans">
        <div className="plan">
          <h3>Basic Plan</h3>
          <p>$9.99/month</p>
          <button 
            onClick={() => handleSubscribe('price_XXXXX')} // Replace with your actual price ID
            disabled={loading || !stripe}
          >
            {loading ? 'Processing...' : 'Subscribe'}
          </button>
        </div>

        <div className="plan">
          <h3>Pro Plan</h3>
          <p>$19.99/month</p>
          <button 
            onClick={() => handleSubscribe('price_YYYYY')} // Replace with your actual price ID
            disabled={loading || !stripe}
          >
            {loading ? 'Processing...' : 'Subscribe'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Payment; 