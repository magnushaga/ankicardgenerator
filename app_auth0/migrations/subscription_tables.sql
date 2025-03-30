-- Add stripe_customer_id to users table
ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS stripe_customer_id TEXT UNIQUE;

-- Create subscriptions table
CREATE TABLE IF NOT EXISTS public.subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    tier VARCHAR(20) NOT NULL CHECK (tier IN ('free', 'basic', 'pro', 'enterprise')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'past_due', 'canceled', 'trialing', 'unpaid')),
    current_period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    current_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    stripe_customer_id TEXT NOT NULL,
    stripe_subscription_id TEXT NOT NULL UNIQUE,
    canceled_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

-- Create subscription_history table for tracking changes
CREATE TABLE IF NOT EXISTS public.subscription_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subscription_id UUID REFERENCES public.subscriptions(id) ON DELETE CASCADE,
    previous_tier VARCHAR(20),
    new_tier VARCHAR(20),
    previous_status VARCHAR(20),
    new_status VARCHAR(20),
    change_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

-- Create subscription_usage table for tracking feature usage
CREATE TABLE IF NOT EXISTS public.subscription_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    feature VARCHAR(50) NOT NULL,
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
    UNIQUE(user_id, feature)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON public.subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON public.subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscription_history_subscription_id ON public.subscription_history(subscription_id);
CREATE INDEX IF NOT EXISTS idx_subscription_usage_user_id ON public.subscription_usage(user_id);

-- Create function to automatically set updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updating updated_at timestamp
CREATE TRIGGER update_subscriptions_updated_at
    BEFORE UPDATE ON public.subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscription_usage_updated_at
    BEFORE UPDATE ON public.subscription_usage
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create function to track subscription changes
CREATE OR REPLACE FUNCTION track_subscription_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'UPDATE') THEN
        IF (OLD.tier != NEW.tier OR OLD.status != NEW.status) THEN
            INSERT INTO public.subscription_history (
                subscription_id,
                previous_tier,
                new_tier,
                previous_status,
                new_status,
                change_reason
            ) VALUES (
                NEW.id,
                OLD.tier,
                NEW.tier,
                OLD.status,
                NEW.status,
                'Subscription updated'
            );
        END IF;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for tracking subscription changes
CREATE TRIGGER track_subscription_changes_trigger
    AFTER UPDATE ON public.subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION track_subscription_changes();

-- Create function to check subscription limits
CREATE OR REPLACE FUNCTION check_subscription_limits()
RETURNS TRIGGER AS $$
DECLARE
    user_tier VARCHAR;
    max_decks INTEGER;
    current_deck_count INTEGER;
BEGIN
    -- Get user's subscription tier
    SELECT tier INTO user_tier
    FROM public.subscriptions
    WHERE user_id = NEW.user_id
    AND status = 'active';

    -- If no active subscription, use free tier
    IF user_tier IS NULL THEN
        user_tier := 'free';
    END IF;

    -- Get max decks for tier
    CASE user_tier
        WHEN 'free' THEN max_decks := 3;
        WHEN 'basic' THEN max_decks := 10;
        WHEN 'pro' THEN max_decks := 50;
        WHEN 'enterprise' THEN max_decks := 999999;
    END CASE;

    -- Count user's current decks
    SELECT COUNT(*) INTO current_deck_count
    FROM public.decks
    WHERE user_id = NEW.user_id;

    -- Check if user has reached their limit
    IF current_deck_count >= max_decks THEN
        RAISE EXCEPTION 'User has reached their deck limit for their subscription tier';
    END IF;

    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for checking deck limits
CREATE TRIGGER check_deck_limits_trigger
    BEFORE INSERT ON public.decks
    FOR EACH ROW
    EXECUTE FUNCTION check_subscription_limits(); 