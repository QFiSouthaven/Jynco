-- Migration: Row-Level Security (RLS) Policies
-- Purpose: Implement data isolation between users for multi-tenant security
-- Execution Mode: Required for production, recommended for self-hosted-production
--
-- This migration enables Row-Level Security on all user-scoped tables to ensure
-- that users can only access their own data, even if application-level authorization
-- is bypassed.

-- =============================================================================
-- STEP 1: Add user context functions
-- =============================================================================

-- Function to get current user ID from session variable
CREATE OR REPLACE FUNCTION current_user_id()
RETURNS UUID AS $$
BEGIN
    RETURN NULLIF(current_setting('app.current_user_id', true), '')::UUID;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to get current user role from session variable
CREATE OR REPLACE FUNCTION current_user_role()
RETURNS TEXT AS $$
BEGIN
    RETURN NULLIF(current_setting('app.current_user_role', true), '');
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to check if current user is admin
CREATE OR REPLACE FUNCTION is_current_user_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN current_user_role() = 'admin';
END;
$$ LANGUAGE plpgsql STABLE;

-- =============================================================================
-- STEP 2: Enable RLS on user-scoped tables
-- =============================================================================

-- Enable RLS on projects table
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- Enable RLS on workflows table
ALTER TABLE workflows ENABLE ROW LEVEL SECURITY;

-- Enable RLS on segments table
ALTER TABLE segments ENABLE ROW LEVEL SECURITY;

-- Enable RLS on render_jobs table (if exists)
-- ALTER TABLE render_jobs ENABLE ROW LEVEL SECURITY;

-- =============================================================================
-- STEP 3: Create RLS policies for projects
-- =============================================================================

-- Policy: Users can view their own projects
CREATE POLICY projects_select_own ON projects
    FOR SELECT
    USING (owner_id = current_user_id());

-- Policy: Admins can view all projects
CREATE POLICY projects_select_admin ON projects
    FOR SELECT
    USING (is_current_user_admin());

-- Policy: Users can insert projects (they become the owner)
CREATE POLICY projects_insert_own ON projects
    FOR INSERT
    WITH CHECK (owner_id = current_user_id());

-- Policy: Users can update their own projects
CREATE POLICY projects_update_own ON projects
    FOR UPDATE
    USING (owner_id = current_user_id())
    WITH CHECK (owner_id = current_user_id());

-- Policy: Users can delete their own projects
CREATE POLICY projects_delete_own ON projects
    FOR DELETE
    USING (owner_id = current_user_id());

-- Policy: Admins can perform any operation on projects
CREATE POLICY projects_admin_all ON projects
    FOR ALL
    USING (is_current_user_admin())
    WITH CHECK (is_current_user_admin());

-- =============================================================================
-- STEP 4: Create RLS policies for workflows
-- =============================================================================

-- Policy: Users can view their own workflows
CREATE POLICY workflows_select_own ON workflows
    FOR SELECT
    USING (owner_id = current_user_id());

-- Policy: Admins can view all workflows
CREATE POLICY workflows_select_admin ON workflows
    FOR SELECT
    USING (is_current_user_admin());

-- Policy: Users can create workflows
CREATE POLICY workflows_insert_own ON workflows
    FOR INSERT
    WITH CHECK (owner_id = current_user_id());

-- Policy: Users can update their own workflows
CREATE POLICY workflows_update_own ON workflows
    FOR UPDATE
    USING (owner_id = current_user_id())
    WITH CHECK (owner_id = current_user_id());

-- Policy: Users can delete their own workflows
CREATE POLICY workflows_delete_own ON workflows
    FOR DELETE
    USING (owner_id = current_user_id());

-- Policy: Admins have full access
CREATE POLICY workflows_admin_all ON workflows
    FOR ALL
    USING (is_current_user_admin())
    WITH CHECK (is_current_user_admin());

-- =============================================================================
-- STEP 5: Create RLS policies for segments
-- =============================================================================

-- Segments are owned via their project, so we need to join
CREATE POLICY segments_select_own ON segments
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = segments.project_id
            AND projects.owner_id = current_user_id()
        )
    );

CREATE POLICY segments_select_admin ON segments
    FOR SELECT
    USING (is_current_user_admin());

CREATE POLICY segments_insert_own ON segments
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = segments.project_id
            AND projects.owner_id = current_user_id()
        )
    );

CREATE POLICY segments_update_own ON segments
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = segments.project_id
            AND projects.owner_id = current_user_id()
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = segments.project_id
            AND projects.owner_id = current_user_id()
        )
    );

CREATE POLICY segments_delete_own ON segments
    FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = segments.project_id
            AND projects.owner_id = current_user_id()
        )
    );

CREATE POLICY segments_admin_all ON segments
    FOR ALL
    USING (is_current_user_admin())
    WITH CHECK (is_current_user_admin());

-- =============================================================================
-- STEP 6: Create audit log table (for security events)
-- =============================================================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    user_id UUID REFERENCES users(id),
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    execution_mode TEXT,
    success BOOLEAN NOT NULL DEFAULT true
);

-- Index for efficient querying
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

-- No RLS on audit logs - only admins should access this table via admin API

-- =============================================================================
-- STEP 7: Create workflow allowlist table
-- =============================================================================

CREATE TABLE IF NOT EXISTS workflow_allowlist (
    id SERIAL PRIMARY KEY,
    execution_mode VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,  -- 'node', 'model', 'repository'
    resource_identifier TEXT NOT NULL,
    approved_by VARCHAR(255),
    approved_at TIMESTAMP DEFAULT NOW(),
    notes TEXT,
    metadata JSONB,
    UNIQUE(execution_mode, resource_type, resource_identifier)
);

-- Index for fast lookups
CREATE INDEX idx_allowlist_lookup ON workflow_allowlist(execution_mode, resource_type, resource_identifier);

-- No RLS - this is a system configuration table

-- =============================================================================
-- STEP 8: Grant appropriate permissions
-- =============================================================================

-- Note: Adjust these grants based on your PostgreSQL user setup
-- These are examples for a typical setup

-- Grant usage on sequences
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO videofoundry_app;

-- Grant permissions on tables
GRANT SELECT, INSERT, UPDATE, DELETE ON projects TO videofoundry_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON workflows TO videofoundry_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON segments TO videofoundry_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON users TO videofoundry_app;

-- Audit logs - insert only for app, full access for admin
GRANT INSERT ON audit_logs TO videofoundry_app;

-- Workflow allowlist - read for app, write for admin
GRANT SELECT ON workflow_allowlist TO videofoundry_app;

-- =============================================================================
-- STEP 9: Create helper function to log audit events
-- =============================================================================

CREATE OR REPLACE FUNCTION log_audit_event(
    p_action TEXT,
    p_resource_type TEXT,
    p_resource_id TEXT DEFAULT NULL,
    p_details JSONB DEFAULT NULL,
    p_success BOOLEAN DEFAULT true
)
RETURNS void AS $$
BEGIN
    INSERT INTO audit_logs (
        user_id,
        action,
        resource_type,
        resource_id,
        details,
        execution_mode,
        success
    ) VALUES (
        current_user_id(),
        p_action,
        p_resource_type,
        p_resource_id,
        p_details,
        current_setting('app.execution_mode', true),
        p_success
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================================================
-- STEP 10: Create triggers to log changes (optional, for enhanced auditing)
-- =============================================================================

-- Trigger function to log project changes
CREATE OR REPLACE FUNCTION audit_project_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        PERFORM log_audit_event('project.created', 'project', NEW.id::TEXT,
            jsonb_build_object('project_name', NEW.name));
        RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') THEN
        PERFORM log_audit_event('project.updated', 'project', NEW.id::TEXT,
            jsonb_build_object('changes', jsonb_build_object('old', to_jsonb(OLD), 'new', to_jsonb(NEW))));
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        PERFORM log_audit_event('project.deleted', 'project', OLD.id::TEXT,
            jsonb_build_object('project_name', OLD.name));
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger (optional - uncomment if you want automatic audit logging)
-- CREATE TRIGGER trigger_audit_projects
--     AFTER INSERT OR UPDATE OR DELETE ON projects
--     FOR EACH ROW EXECUTE FUNCTION audit_project_changes();

-- =============================================================================
-- ROLLBACK SCRIPT (for testing or reverting)
-- =============================================================================

-- To disable RLS (for rollback):
-- ALTER TABLE projects DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE workflows DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE segments DISABLE ROW LEVEL SECURITY;
-- DROP POLICY IF EXISTS projects_select_own ON projects;
-- DROP POLICY IF EXISTS projects_select_admin ON projects;
-- ... (drop all policies)
-- DROP FUNCTION IF EXISTS current_user_id();
-- DROP FUNCTION IF EXISTS current_user_role();
-- DROP FUNCTION IF EXISTS is_current_user_admin();
-- DROP FUNCTION IF EXISTS log_audit_event(TEXT, TEXT, TEXT, JSONB, BOOLEAN);
-- DROP FUNCTION IF EXISTS audit_project_changes();

-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================

-- Verify RLS is enabled:
-- SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public' AND rowsecurity = true;

-- Verify policies exist:
-- SELECT schemaname, tablename, policyname FROM pg_policies WHERE schemaname = 'public';

-- Test policy enforcement (as application user):
-- SET app.current_user_id = '<user-uuid>';
-- SELECT * FROM projects;  -- Should only show projects owned by that user

-- =============================================================================
-- NOTES FOR ADMINISTRATORS
-- =============================================================================

-- 1. RLS is enforced at the database level, providing defense-in-depth even if
--    application-level authorization is bypassed.
--
-- 2. The session variables (app.current_user_id, app.current_user_role) MUST be
--    set by the application for every request. This is handled in the auth middleware.
--
-- 3. For production mode, ensure that:
--    - Database user has minimal privileges (no BYPASSRLS)
--    - Connection pooling is configured correctly
--    - Session variables are set for every transaction
--
-- 4. To add RLS to new tables:
--    a. ALTER TABLE <table> ENABLE ROW LEVEL SECURITY;
--    b. CREATE POLICY <policy_name> ON <table> FOR <operation> USING (<condition>);
--
-- 5. For shared resources (e.g., public workflows), add additional policies:
--    CREATE POLICY workflows_select_public ON workflows
--        FOR SELECT
--        USING (is_public = true);

-- =============================================================================
-- END OF MIGRATION
-- =============================================================================
