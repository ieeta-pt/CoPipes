-- Migration to support enhanced organization role hierarchy
-- This migration adds the new roles: OWNER, MANAGER, VIEWER
-- and ensures existing data is properly migrated

-- First, add the new role enum values if they don't exist
-- Note: This assumes the organization_role enum already exists
DO $$
BEGIN
    -- Add new enum values if they don't exist
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'owner' AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'organization_role')) THEN
        ALTER TYPE organization_role ADD VALUE 'owner';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'manager' AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'organization_role')) THEN
        ALTER TYPE organization_role ADD VALUE 'manager';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'viewer' AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'organization_role')) THEN
        ALTER TYPE organization_role ADD VALUE 'viewer';
    END IF;
END $$;

-- Update existing organization owners to have the 'owner' role
-- This assumes the organizations table has an owner_id column
UPDATE organization_members 
SET role = 'owner'
WHERE user_id IN (
    SELECT owner_id 
    FROM organizations 
    WHERE organizations.id = organization_members.organization_id
) AND role = 'admin';

-- Add indexes for better performance on role-based queries
CREATE INDEX IF NOT EXISTS idx_organization_members_role ON organization_members(role);
CREATE INDEX IF NOT EXISTS idx_organization_members_org_role ON organization_members(organization_id, role);

-- Add a comment to track this migration
COMMENT ON TABLE organization_members IS 'Updated to support role hierarchy: owner > admin > manager > member > viewer';