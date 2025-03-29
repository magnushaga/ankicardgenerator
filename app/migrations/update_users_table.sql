-- Drop existing users table and its dependencies
DROP TABLE IF EXISTS deck_shares CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create new users table with Auth0 integration
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    auth0_id VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    preferred_study_time VARCHAR(50),
    notification_preferences JSONB,
    study_goals JSONB
);

-- Create indexes for better query performance
CREATE INDEX idx_users_auth0_id ON users(auth0_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Recreate deck_shares table
CREATE TABLE deck_shares (
    deck_id UUID REFERENCES decks(id),
    user_id VARCHAR(36) REFERENCES users(id),
    shared_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (deck_id, user_id)
);

-- Add RLS policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy to allow users to read their own data
CREATE POLICY "Users can read own data" ON users
    FOR SELECT
    USING (auth0_id = current_user);

-- Policy to allow users to update their own data
CREATE POLICY "Users can update own data" ON users
    FOR UPDATE
    USING (auth0_id = current_user);

-- Policy to allow service role to manage all users
CREATE POLICY "Service role can manage all users" ON users
    FOR ALL
    USING (auth.role() = 'service_role'); 