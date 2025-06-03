-- Create organizations table
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create organization_members table
CREATE TABLE IF NOT EXISTS organization_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'member')),
    invited_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    invited_by UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    UNIQUE(user_id, organization_id)
);

-- Add organization_id column to workflows table if it doesn't exist
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'workflows' AND column_name = 'organization_id'
    ) THEN
        ALTER TABLE workflows ADD COLUMN organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL;
    END IF;
END $$;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_organizations_owner_id ON organizations(owner_id);
CREATE INDEX IF NOT EXISTS idx_organization_members_user_id ON organization_members(user_id);
CREATE INDEX IF NOT EXISTS idx_organization_members_organization_id ON organization_members(organization_id);
CREATE INDEX IF NOT EXISTS idx_workflows_organization_id ON workflows(organization_id);

-- Enable Row Level Security (RLS) for organizations
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE organization_members ENABLE ROW LEVEL SECURITY;

-- Create policies for organizations table
CREATE POLICY "Users can view organizations they belong to" ON organizations
    FOR SELECT USING (
        id IN (
            SELECT organization_id FROM organization_members 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create organizations" ON organizations
    FOR INSERT WITH CHECK (owner_id = auth.uid());

CREATE POLICY "Organization owners can update their organizations" ON organizations
    FOR UPDATE USING (owner_id = auth.uid());

CREATE POLICY "Organization owners can delete their organizations" ON organizations
    FOR DELETE USING (owner_id = auth.uid());

-- Create policies for organization_members table
CREATE POLICY "Users can view organization members for organizations they belong to" ON organization_members
    FOR SELECT USING (
        organization_id IN (
            SELECT organization_id FROM organization_members 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Organization admins can manage members" ON organization_members
    FOR ALL USING (
        organization_id IN (
            SELECT organization_id FROM organization_members 
            WHERE user_id = auth.uid() AND role = 'admin'
        )
    );

-- Add workflows RLS policy for organization context
CREATE POLICY "Users can view organization workflows" ON workflows
    FOR SELECT USING (
        organization_id IS NULL OR
        organization_id IN (
            SELECT organization_id FROM organization_members 
            WHERE user_id = auth.uid()
        )
    );