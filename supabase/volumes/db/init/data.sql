-- Auto-confirm user accounts on creation
-- This trigger automatically confirms users when they sign up

BEGIN;

-- Create the function in the auth schema with superuser privileges
CREATE OR REPLACE FUNCTION auth.auto_confirm_account()
RETURNS TRIGGER 
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = auth, pg_temp
AS $$
BEGIN
  -- Set email confirmation timestamp
  NEW.email_confirmed_at = NOW();
  NEW.confirmed_at = NOW();
  
  -- Update metadata to mark email as verified
  NEW.raw_user_meta_data = jsonb_set(
    COALESCE(NEW.raw_user_meta_data, '{}'::jsonb),
    '{email_verified}',
    'true'::jsonb
  );
  
  RETURN NEW;
END;
$$;

-- Drop existing trigger if it exists
DROP TRIGGER IF EXISTS on_auth_user_created_auto_confirm ON auth.users;

-- Create trigger that runs before insert
CREATE TRIGGER on_auth_user_created_auto_confirm
  BEFORE INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION auth.auto_confirm_account();

COMMIT;
