-- Drop existing RLS policies
ALTER TABLE IF EXISTS public.decks DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.live_decks DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.parts DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.chapters DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.topics DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.cards DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.study_sessions DISABLE ROW LEVEL SECURITY;

-- Drop existing collaboration tables
DROP TABLE IF EXISTS public.deck_collaborations CASCADE;

-- Create new deck_collaborations table with role-based access
CREATE TABLE public.deck_collaborations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    deck_id UUID REFERENCES public.decks(id) ON DELETE CASCADE,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('owner', 'editor', 'viewer', 'admin')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
    UNIQUE(deck_id, user_id)
);

-- Create indexes for better query performance
CREATE INDEX idx_deck_collaborations_deck_id ON public.deck_collaborations(deck_id);
CREATE INDEX idx_deck_collaborations_user_id ON public.deck_collaborations(user_id);
CREATE INDEX idx_deck_collaborations_role ON public.deck_collaborations(role);

-- Create function to automatically set updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updating updated_at timestamp
CREATE TRIGGER update_deck_collaborations_updated_at
    BEFORE UPDATE ON public.deck_collaborations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert default owner collaborations for existing decks
INSERT INTO public.deck_collaborations (deck_id, user_id, role)
SELECT id, user_id, 'owner'
FROM public.decks
WHERE NOT EXISTS (
    SELECT 1 FROM public.deck_collaborations
    WHERE deck_collaborations.deck_id = decks.id
    AND deck_collaborations.user_id = decks.user_id
); 