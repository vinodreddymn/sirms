-- Assign ADMIN role to users 'vinod' and 'reegan' if not already assigned.
-- Run this as a database superuser or a role that can INSERT into security.user_roles.
-- Example:
-- psql -d sirms -f backend/scripts/make_vinod_reegan_admins.sql

BEGIN;

-- Ensure ADMIN role exists
WITH admin_role AS (
  SELECT id FROM security.roles WHERE role_code = 'ADMIN' LIMIT 1
),
vinod_user AS (
  SELECT id FROM security.users WHERE username = 'vinod' LIMIT 1
),
reegan_user AS (
  SELECT id FROM security.users WHERE username = 'reegan' LIMIT 1
)
-- insert for vinod
INSERT INTO security.user_roles (user_id, role_id)
SELECT v.id, a.id
FROM vinod_user v, admin_role a
WHERE NOT EXISTS (
  SELECT 1 FROM security.user_roles ur WHERE ur.user_id = v.id AND ur.role_id = a.id
);

-- insert for reegan
INSERT INTO security.user_roles (user_id, role_id)
SELECT r.id, a.id
FROM reegan_user r, admin_role a
WHERE NOT EXISTS (
  SELECT 1 FROM security.user_roles ur WHERE ur.user_id = r.id AND ur.role_id = a.id
);

COMMIT;

-- Check results:
-- select u.username, r.role_code from security.user_roles ur
-- join security.users u on ur.user_id = u.id
-- join security.roles r on ur.role_id = r.id
-- where u.username in ('vinod','reegan');
