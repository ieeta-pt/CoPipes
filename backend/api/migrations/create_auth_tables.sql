-- Create users table
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    full_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create refresh tokens table
CREATE TABLE IF NOT EXISTS public.refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    token TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create index on tokens for faster lookups
CREATE INDEX IF NOT EXISTS refresh_tokens_user_id_idx ON public.refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS refresh_tokens_token_idx ON public.refresh_tokens(token);

-- Set up Row Level Security (RLS)
-- Enable RLS on tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.refresh_tokens ENABLE ROW LEVEL SECURITY;

-- Create policies
-- Users can only see and update their own data
CREATE POLICY users_policy ON public.users
    USING (id = auth.uid())
    WITH CHECK (id = auth.uid());

-- Only the system can access refresh tokens (via service role)
CREATE POLICY refresh_tokens_policy ON public.refresh_tokens
    USING (false)
    WITH CHECK (false);

-- Create a trigger to clean up old refresh tokens (older than 30 days)
CREATE OR REPLACE FUNCTION public.clean_old_refresh_tokens()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM public.refresh_tokens
    WHERE created_at < NOW() - INTERVAL '30 days';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER clean_old_refresh_tokens_trigger
AFTER INSERT ON public.refresh_tokens
EXECUTE PROCEDURE public.clean_old_refresh_tokens(); 