CREATE TABLE IF NOT EXISTS decks (
    id UUID NOT NULL,
    user_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS textbooks (
    id UUID NOT NULL,
    user_id UUID NULL,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    description TEXT NULL,
    file_path VARCHAR(500) NULL,
    uploaded_at TIMESTAMP NULL,
    is_public BOOLEAN NULL,
    tags JSON NULL,
    difficulty_level VARCHAR(20) NULL,
    language VARCHAR(10) NULL,
    total_cards INTEGER NULL,
    avg_rating DOUBLE PRECISION NULL,
    num_ratings INTEGER NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS deck_shares (
    deck_id UUID NOT NULL,
    user_id UUID NOT NULL,
    shared_at TIMESTAMP NULL,
    PRIMARY KEY (deck_id, user_id),
    FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS parts (
    id UUID NOT NULL,
    deck_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    order_index INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS study_sessions (
    id UUID NOT NULL,
    user_id UUID NOT NULL,
    deck_id UUID NOT NULL,
    started_at TIMESTAMP NULL,
    ended_at TIMESTAMP NULL,
    cards_studied INTEGER NULL,
    correct_answers INTEGER NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS textbook_reviews (
    id UUID NOT NULL,
    textbook_id UUID NOT NULL,
    user_id UUID NOT NULL,
    rating INTEGER NOT NULL,
    comment TEXT NULL,
    created_at TIMESTAMP NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (textbook_id) REFERENCES textbooks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chapters (
    id UUID NOT NULL,
    part_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    order_index INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (part_id) REFERENCES parts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS topics (
    id UUID NOT NULL,
    chapter_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    order_index INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS admin_roles (
    id VARCHAR(36) NOT NULL DEFAULT (uuid_generate_v4())::text,
    name VARCHAR(50) NOT NULL,
    description TEXT NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS idx_admin_roles_name ON admin_roles(name);

CREATE INDEX IF NOT EXISTS idx_admin_roles_name ON admin_roles(name);

CREATE TABLE IF NOT EXISTS cards (
    id UUID NOT NULL,
    topic_id UUID NOT NULL,
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    created_at TIMESTAMP NULL,
    media_urls JSONB NULL DEFAULT '[]'::jsonb,
    PRIMARY KEY (id),
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS admin_permissions (
    id VARCHAR(36) NOT NULL DEFAULT (uuid_generate_v4())::text,
    name VARCHAR(50) NOT NULL,
    description TEXT NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS idx_admin_permissions_name ON admin_permissions(name);

CREATE INDEX IF NOT EXISTS idx_admin_permissions_name ON admin_permissions(name);

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) NOT NULL,
    email VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    auth0_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN NULL,
    email_verified BOOLEAN NULL,
    preferred_study_time VARCHAR(50) NULL,
    notification_preferences JSON NULL,
    study_goals JSON NULL,
    stripe_customer_id TEXT NULL,
    picture VARCHAR(255) NULL,
    PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS idx_users_auth0_id ON users(auth0_id);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

CREATE INDEX IF NOT EXISTS idx_users_auth0_id ON users(auth0_id);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

CREATE INDEX IF NOT EXISTS idx_users_stripe_customer_id ON users(stripe_customer_id);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

CREATE TABLE IF NOT EXISTS media_files (
    id VARCHAR(36) NOT NULL DEFAULT (uuid_generate_v4())::text,
    user_id VARCHAR(36) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    storage_path VARCHAR(500) NOT NULL,
    thumbnail_path VARCHAR(500) NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_media_files_user_id ON media_files(user_id);

CREATE TABLE IF NOT EXISTS media_associations (
    id VARCHAR(36) NOT NULL DEFAULT (uuid_generate_v4())::text,
    media_file_id VARCHAR(36) NOT NULL,
    associated_type VARCHAR(50) NOT NULL,
    associated_id VARCHAR(36) NOT NULL,
    position INTEGER NULL,
    context VARCHAR(50) NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (media_file_id) REFERENCES media_files(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_media_associations_associated_type_associated_id ON media_associations(associated_type, associated_id);

CREATE TABLE IF NOT EXISTS user_decks (
    id UUID NOT NULL,
    user_id UUID NOT NULL,
    deck_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT NULL,
    created_at TIMESTAMP NULL,
    updated_at TIMESTAMP NULL,
    total_cards INTEGER NULL,
    active_cards INTEGER NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS course_materials (
    id VARCHAR(36) NOT NULL DEFAULT (uuid_generate_v4())::text,
    user_id VARCHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NULL,
    material_type VARCHAR(50) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    tags JSONB NULL DEFAULT '[]'::jsonb,
    metadata JSONB NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_course_materials_user_id ON course_materials(user_id);

CREATE TABLE IF NOT EXISTS study_resources (
    id VARCHAR(36) NOT NULL DEFAULT (uuid_generate_v4())::text,
    user_id VARCHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content JSONB NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    source_material_id VARCHAR(36) NULL,
    tags JSONB NULL DEFAULT '[]'::jsonb,
    metadata JSONB NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (source_material_id) REFERENCES course_materials(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_study_resources_source_material_id ON study_resources(source_material_id);

CREATE INDEX IF NOT EXISTS idx_study_resources_user_id ON study_resources(user_id);

CREATE TABLE IF NOT EXISTS resource_generations (
    id VARCHAR(36) NOT NULL DEFAULT (uuid_generate_v4())::text,
    user_id VARCHAR(36) NOT NULL,
    resource_id VARCHAR(36) NOT NULL,
    status VARCHAR(20) NOT NULL,
    generation_type VARCHAR(50) NOT NULL,
    prompt TEXT NOT NULL,
    result JSONB NULL,
    error TEXT NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (resource_id) REFERENCES study_resources(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_resource_generations_resource_id ON resource_generations(resource_id);

CREATE INDEX IF NOT EXISTS idx_resource_generations_status ON resource_generations(status);

CREATE TABLE IF NOT EXISTS live_decks (
    id UUID NOT NULL,
    user_id UUID NOT NULL,
    deck_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT NULL,
    created_at TIMESTAMP NULL,
    updated_at TIMESTAMP NULL,
    active_cards INTEGER NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS learning_analytics (
    id UUID NOT NULL,
    user_id UUID NOT NULL,
    live_deck_id UUID NOT NULL,
    created_at TIMESTAMP NULL,
    updated_at TIMESTAMP NULL,
    preferred_study_time VARCHAR(5) NULL,
    average_session_duration INTEGER NULL,
    cards_per_session INTEGER NULL,
    mastery_level DOUBLE PRECISION NULL,
    weak_areas JSON NULL,
    strong_areas JSON NULL,
    preferred_card_types JSON NULL,
    study_consistency DOUBLE PRECISION NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (live_deck_id) REFERENCES live_decks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS deck_collaborations (
    id UUID NOT NULL,
    deck_id UUID NOT NULL,
    user_id UUID NOT NULL,
    role VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NULL,
    can_edit BOOLEAN NULL,
    can_share BOOLEAN NULL,
    can_delete BOOLEAN NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS achievements (
    id UUID NOT NULL,
    user_id UUID NOT NULL,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT NULL,
    earned_at TIMESTAMP NULL,
    achievement_data JSON NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS study_reminders (
    id UUID NOT NULL,
    user_id UUID NOT NULL,
    live_deck_id UUID NOT NULL,
    reminder_time TIME NOT NULL,
    days_of_week JSON NOT NULL,
    notification_type VARCHAR(20) NULL,
    created_at TIMESTAMP NULL,
    is_active BOOLEAN NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (live_deck_id) REFERENCES live_decks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS deck_exports (
    id UUID NOT NULL,
    deck_id UUID NOT NULL,
    user_id UUID NOT NULL,
    format VARCHAR(20) NOT NULL,
    settings JSON NULL,
    file_url VARCHAR(500) NULL,
    created_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS content_reports (
    id UUID NOT NULL,
    reporter_id UUID NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    content_id UUID NOT NULL,
    reason VARCHAR(50) NOT NULL,
    description TEXT NULL,
    status VARCHAR(20) NULL,
    created_at TIMESTAMP NULL,
    resolved_at TIMESTAMP NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS api_logs (
    id UUID NOT NULL,
    user_id UUID NULL,
    endpoint VARCHAR(100) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    response_time INTEGER NULL,
    created_at TIMESTAMP NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    user_id VARCHAR(36) NULL,
    tier VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    current_period_start TIMESTAMP NOT NULL,
    current_period_end TIMESTAMP NOT NULL,
    stripe_customer_id TEXT NOT NULL,
    stripe_subscription_id TEXT NOT NULL,
    canceled_at TIMESTAMP NULL,
    created_at TIMESTAMP NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP NULL DEFAULT timezone('utc'::text, now()),
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);

CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);

CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_subscription_id ON subscriptions(stripe_subscription_id);

CREATE TABLE IF NOT EXISTS subscription_history (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    subscription_id UUID NULL,
    previous_tier VARCHAR(20) NULL,
    new_tier VARCHAR(20) NULL,
    previous_status VARCHAR(20) NULL,
    new_status VARCHAR(20) NULL,
    change_reason TEXT NULL,
    created_at TIMESTAMP NULL DEFAULT timezone('utc'::text, now()),
    PRIMARY KEY (id),
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_subscription_history_subscription_id ON subscription_history(subscription_id);

CREATE TABLE IF NOT EXISTS subscription_usage (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    user_id VARCHAR(36) NULL,
    feature VARCHAR(50) NOT NULL,
    usage_count INTEGER NULL DEFAULT 0,
    last_used_at TIMESTAMP NULL,
    created_at TIMESTAMP NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP NULL DEFAULT timezone('utc'::text, now()),
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_subscription_usage_user_id ON subscription_usage(user_id);

CREATE INDEX IF NOT EXISTS idx_subscription_usage_user_id_feature ON subscription_usage(user_id, feature);

CREATE TABLE IF NOT EXISTS user_card_states (
    id UUID NOT NULL,
    user_id UUID NOT NULL,
    card_id UUID NOT NULL,
    is_active BOOLEAN NULL,
    created_at TIMESTAMP NULL,
    updated_at TIMESTAMP NULL,
    easiness DOUBLE PRECISION NULL,
    interval INTEGER NULL,
    repetitions INTEGER NULL,
    next_review TIMESTAMP NULL,
    last_review TIMESTAMP NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS card_reviews (
    id UUID NOT NULL,
    session_id UUID NOT NULL,
    card_id UUID NOT NULL,
    quality INTEGER NOT NULL,
    reviewed_at TIMESTAMP NULL,
    time_taken INTEGER NULL,
    prev_easiness DOUBLE PRECISION NULL,
    prev_interval INTEGER NULL,
    prev_repetitions INTEGER NULL,
    new_easiness DOUBLE PRECISION NULL,
    new_interval INTEGER NULL,
    new_repetitions INTEGER NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES study_sessions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS admin_role_permissions (
    role_id VARCHAR(36) NOT NULL,
    permission_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (permission_id) REFERENCES admin_permissions(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES admin_roles(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_admin_roles (
    user_id VARCHAR(36) NOT NULL,
    role_id VARCHAR(36) NOT NULL,
    assigned_by VARCHAR(36) NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (assigned_by) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES admin_roles(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_user_admin_roles_user_id ON user_admin_roles(user_id);

CREATE TABLE IF NOT EXISTS admin_audit_logs (
    id VARCHAR(36) NOT NULL DEFAULT (uuid_generate_v4())::text,
    admin_id VARCHAR(36) NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(36) NULL,
    details JSONB NULL,
    ip_address VARCHAR(45) NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_admin_audit_logs_admin_id ON admin_audit_logs(admin_id);

CREATE INDEX IF NOT EXISTS idx_admin_audit_logs_created_at ON admin_audit_logs(created_at);