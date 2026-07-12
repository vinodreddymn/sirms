/*
===============================================================================
Project     : SIRMS
Version     : 1.0
Module      : Security
Description : Creates users, roles, permissions, sessions, and token tables.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS security.users
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username                VARCHAR(50) NOT NULL UNIQUE,
    full_name               VARCHAR(150) NOT NULL,
    email                   VARCHAR(150) NOT NULL UNIQUE,
    mobile_number           VARCHAR(30),
    password_hash           TEXT NOT NULL,
    default_project_id      UUID,
    last_login_at           TIMESTAMP,
    password_changed_at     TIMESTAMP,
    is_locked               BOOLEAN NOT NULL DEFAULT FALSE,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID
);

CREATE TABLE IF NOT EXISTS security.roles
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_template_id        BIGINT REFERENCES master.user_role_templates(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    role_code               VARCHAR(30) NOT NULL UNIQUE,
    role_name               VARCHAR(100) NOT NULL UNIQUE,
    description             TEXT,
    is_system_role          BOOLEAN NOT NULL DEFAULT FALSE,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID
);

CREATE TABLE IF NOT EXISTS security.permissions
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    permission_code         VARCHAR(60) NOT NULL UNIQUE,
    permission_name         VARCHAR(120) NOT NULL UNIQUE,
    module_name             VARCHAR(50) NOT NULL,
    description             TEXT,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID
);

CREATE TABLE IF NOT EXISTS security.role_permissions
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id                 UUID NOT NULL REFERENCES security.roles(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    permission_id           UUID NOT NULL REFERENCES security.permissions(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID,
    CONSTRAINT uq_role_permissions UNIQUE(role_id, permission_id)
);

CREATE TABLE IF NOT EXISTS security.user_roles
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    role_id                 UUID NOT NULL REFERENCES security.roles(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    project_id              UUID,
    assigned_from           DATE NOT NULL DEFAULT CURRENT_DATE,
    assigned_to             DATE,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID,
    CONSTRAINT uq_security_user_roles UNIQUE(user_id, role_id, project_id),
    CONSTRAINT chk_security_user_roles_dates CHECK (assigned_to IS NULL OR assigned_to >= assigned_from)
);

CREATE TABLE IF NOT EXISTS security.login_history
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    login_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    logout_at               TIMESTAMP,
    login_status            VARCHAR(20) NOT NULL,
    ip_address              VARCHAR(64),
    device_info             VARCHAR(255),
    remarks                 TEXT,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID,
    CONSTRAINT chk_login_history_status CHECK (login_status IN ('SUCCESS', 'FAILED', 'LOCKED'))
);

CREATE TABLE IF NOT EXISTS security.password_reset_tokens
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    token_hash              TEXT NOT NULL UNIQUE,
    expires_at              TIMESTAMP NOT NULL,
    used_at                 TIMESTAMP,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID
);

CREATE TABLE IF NOT EXISTS security.refresh_tokens
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    token_hash              TEXT NOT NULL UNIQUE,
    issued_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at              TIMESTAMP NOT NULL,
    revoked_at              TIMESTAMP,
    device_info             VARCHAR(255),
    ip_address              VARCHAR(64),
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID
);

CREATE TABLE IF NOT EXISTS security.api_tokens
(
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    token_name              VARCHAR(100) NOT NULL,
    token_hash              TEXT NOT NULL UNIQUE,
    scope_json              JSONB,
    last_used_at            TIMESTAMP,
    expires_at              TIMESTAMP,
    revoked_at              TIMESTAMP,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID,
    CONSTRAINT uq_api_token_name UNIQUE(user_id, token_name)
);

COMMENT ON TABLE security.users IS 'Application users.';
COMMENT ON TABLE security.roles IS 'Runtime roles assigned to users.';
COMMENT ON TABLE security.permissions IS 'Permission catalog.';
COMMENT ON TABLE security.role_permissions IS 'Bridge between roles and permissions.';
COMMENT ON TABLE security.user_roles IS 'User-to-role assignments, optionally project scoped.';
COMMENT ON TABLE security.login_history IS 'Authentication session history.';
COMMENT ON TABLE security.password_reset_tokens IS 'Password reset token history.';
COMMENT ON TABLE security.refresh_tokens IS 'JWT refresh token store.';
COMMENT ON TABLE security.api_tokens IS 'Future-ready API token store.';
