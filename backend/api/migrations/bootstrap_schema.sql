CREATE EXTENSION IF NOT EXISTS pgcrypto;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'workflow_status') THEN
        CREATE TYPE workflow_status AS ENUM ('draft', 'running', 'completed', 'failed', 'paused', 'queued', 'success');
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'workflow_role') THEN
        CREATE TYPE workflow_role AS ENUM ('owner', 'editor', 'viewer');
    END IF;
END
$$;

CREATE TABLE IF NOT EXISTS public.profiles (
    id uuid NOT NULL,
    email text NOT NULL UNIQUE,
    full_name text NOT NULL,
    avatar_url text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    CONSTRAINT profiles_pkey PRIMARY KEY (id),
    CONSTRAINT profiles_id_fkey FOREIGN KEY (id) REFERENCES auth.users(id)
);

CREATE TABLE IF NOT EXISTS public.organizations (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    name varchar NOT NULL,
    description text,
    owner_id uuid NOT NULL,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    CONSTRAINT organizations_pkey PRIMARY KEY (id),
    CONSTRAINT organizations_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.profiles(id)
);

CREATE TABLE IF NOT EXISTS public.organization_members (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL,
    organization_id uuid NOT NULL,
    role varchar NOT NULL CHECK (role IN ('owner', 'admin', 'manager', 'member', 'viewer')),
    invited_at timestamptz DEFAULT now(),
    invited_by uuid NOT NULL,
    CONSTRAINT organization_members_pkey PRIMARY KEY (id),
    CONSTRAINT organization_members_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE,
    CONSTRAINT organization_members_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.profiles(id),
    CONSTRAINT organization_members_invited_by_fkey FOREIGN KEY (invited_by) REFERENCES public.profiles(id)
);

CREATE TABLE IF NOT EXISTS public.workflows (
    id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    name text NOT NULL,
    last_edit timestamp NOT NULL DEFAULT now(),
    last_run timestamp,
    status workflow_status NOT NULL DEFAULT 'draft',
    collaborators text[] DEFAULT '{}',
    user_id uuid NOT NULL,
    organization_id uuid,
    CONSTRAINT workflows_pkey PRIMARY KEY (id),
    CONSTRAINT workflows_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id),
    CONSTRAINT workflows_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.profiles(id)
);

CREATE TABLE IF NOT EXISTS public.tasks (
    id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
    tasks json DEFAULT '{}'::json,
    workflow_id bigint NOT NULL,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    CONSTRAINT tasks_pkey PRIMARY KEY (id),
    CONSTRAINT tasks_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflows(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS public.workflow_collaborators (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    workflow_id bigint NOT NULL,
    user_id uuid NOT NULL,
    role workflow_role NOT NULL DEFAULT 'viewer',
    invited_at timestamptz DEFAULT now(),
    invited_by uuid NOT NULL,
    CONSTRAINT workflow_collaborators_pkey PRIMARY KEY (id),
    CONSTRAINT workflow_collaborators_invited_by_fkey FOREIGN KEY (invited_by) REFERENCES public.profiles(id),
    CONSTRAINT workflow_collaborators_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.profiles(id),
    CONSTRAINT workflow_collaborators_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflows(id) ON DELETE CASCADE
);

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name, avatar_url)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email),
        NEW.raw_user_meta_data->>'avatar_url'
    )
    ON CONFLICT (id) DO NOTHING;
    RETURN NEW;
END;
$$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'auth' AND c.relname = 'users'
    )
    AND NOT EXISTS (
        SELECT 1
        FROM pg_trigger
        WHERE tgname = 'on_auth_user_created'
    ) THEN
        CREATE TRIGGER on_auth_user_created
        AFTER INSERT ON auth.users
        FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
    END IF;
END
$$;