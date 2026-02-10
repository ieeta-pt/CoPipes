-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

-- Custom Types
CREATE TYPE workflow_status AS ENUM ('draft', 'running', 'completed', 'failed', 'paused', 'queued', 'success');
CREATE TYPE workflow_role AS ENUM ('owner', 'editor', 'viewer');

-- Trigger function for auto-creating profiles on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name, avatar_url)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email),
    NEW.raw_user_meta_data->>'avatar_url'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

CREATE TABLE public.organization_members (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  organization_id uuid NOT NULL,
  role character varying NOT NULL CHECK (role::text = ANY (ARRAY['owner'::character varying, 'admin'::character varying, 'manager'::character varying, 'member'::character varying, 'viewer'::character varying]::text[])),
  invited_at timestamp with time zone DEFAULT now(),
  invited_by uuid NOT NULL,
  CONSTRAINT organization_members_pkey PRIMARY KEY (id),
  CONSTRAINT organization_members_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE,
  CONSTRAINT organization_members_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.profiles(id),
  CONSTRAINT organization_members_invited_by_fkey FOREIGN KEY (invited_by) REFERENCES public.profiles(id)
);
CREATE TABLE public.organizations (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  name character varying NOT NULL,
  description text,
  owner_id uuid NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT organizations_pkey PRIMARY KEY (id),
  CONSTRAINT organizations_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.profiles(id)
);
CREATE TABLE public.profiles (
  id uuid NOT NULL,
  email text NOT NULL UNIQUE,
  full_name text NOT NULL,
  avatar_url text,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT profiles_pkey PRIMARY KEY (id),
  CONSTRAINT profiles_id_fkey FOREIGN KEY (id) REFERENCES auth.users(id)
);
CREATE TABLE public.tasks (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  tasks json DEFAULT '{}'::json,
  workflow_id bigint NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT tasks_pkey PRIMARY KEY (id),
  CONSTRAINT tasks_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflows(id) ON DELETE CASCADE
);
CREATE TABLE public.workflow_collaborators (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  workflow_id bigint NOT NULL,
  user_id uuid NOT NULL,
  role workflow_role NOT NULL DEFAULT 'viewer'::workflow_role,
  invited_at timestamp with time zone DEFAULT now(),
  invited_by uuid NOT NULL,
  CONSTRAINT workflow_collaborators_pkey PRIMARY KEY (id),
  CONSTRAINT workflow_collaborators_invited_by_fkey FOREIGN KEY (invited_by) REFERENCES public.profiles(id),
  CONSTRAINT workflow_collaborators_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.profiles(id),
  CONSTRAINT workflow_collaborators_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflows(id) ON DELETE CASCADE
);
CREATE TABLE public.workflows (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  name text NOT NULL,
  last_edit timestamp without time zone NOT NULL DEFAULT now(),
  last_run timestamp without time zone,
  status workflow_status NOT NULL DEFAULT 'draft'::workflow_status,
  collaborators text[] DEFAULT '{}'::text[],
  user_id uuid NOT NULL,
  organization_id uuid,
  CONSTRAINT workflows_pkey PRIMARY KEY (id),
  CONSTRAINT workflows_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id),
  CONSTRAINT workflows_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.profiles(id)
);