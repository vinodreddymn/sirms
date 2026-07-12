-- ============================================================================
-- ARIMS / SIRMS
-- Database Deployment Script
-- Version : 1.0
-- PostgreSQL : 17+
--
-- Execute from the PROJECT ROOT:
--
--   psql -U svr_user -d sirms -h localhost -f database/deploy.sql
--
-- Directory Structure
--
-- sirms/
-- ├── database/
-- │   ├── deploy.sql
-- │   ├── ddl/
-- │   ├── seed/
-- │   └── validation/
-- │
-- ============================================================================
-- IMPORTANT
-- ============================================================================
-- This script assumes it is executed from the PROJECT ROOT.
--
-- Example:
--
--   C:\Users\DELL\Documents\AI_Projects\sirms>
--
--   psql -U svr_user -d sirms -h localhost -f database/deploy.sql
--
-- ============================================================================

\set ON_ERROR_STOP on
\timing on

\echo
\echo ===========================================================================
\echo                ARIMS / SIRMS DATABASE DEPLOYMENT
\echo ===========================================================================
\echo

-- ============================================================================
-- PREFLIGHT CHECK
-- ============================================================================

\echo Checking that target database is empty for application schemas...

SELECT CASE
           WHEN EXISTS (
               SELECT 1
               FROM pg_class c
               JOIN pg_namespace n ON n.oid = c.relnamespace
               WHERE n.nspname IN ('common', 'master', 'security', 'infrastructure', 'asset', 'incident')
                 AND c.relkind IN ('r', 'p', 'v', 'm', 'S', 'f')
           )
           THEN 'true'
           ELSE 'false'
       END AS deployment_blocked
\gset

\if :deployment_blocked
\echo
\echo ERROR: Target database is not empty for ARIMS / SIRMS schemas.
\echo This deployment script only supports a brand-new empty database.
\echo Drop and recreate the target database, then rerun `database/deploy.sql`.
\echo
\quit 1
\endif

-- ============================================================================
-- DDL SCRIPTS
-- ============================================================================

\echo
\echo [1/14] Creating Extensions and Schemas...
\i database/ddl/001_create_extensions.sql

\echo
\echo [2/14] Creating Master Tables...
\i database/ddl/002_master_tables.sql

\echo
\echo [3/14] Creating Security Schema...
\i database/ddl/003_security.sql

\echo
\echo [4/14] Creating Common Schema...
\i database/ddl/004_common.sql

\echo
\echo [5/14] Creating Infrastructure Schema...
\i database/ddl/005_infrastructure.sql

\echo
\echo [6/14] Creating Asset Schema...
\i database/ddl/006_asset.sql

\echo
\echo [7/14] Creating Incident Schema...
\i database/ddl/007_incident.sql

\echo
\echo [8/14] Creating Indexes...
\i database/ddl/008_indexes.sql

\echo
\echo [9/14] Creating Database Views...
\i database/ddl/009_views.sql

\echo
\echo [10/14] Creating Functions...
\i database/ddl/010_functions.sql

\echo
\echo [11/14] Creating Triggers...
\i database/ddl/011_triggers.sql

-- ============================================================================
-- SEED DATA
-- ============================================================================

\echo
\echo ===========================================================================
\echo Loading Master Data...
\echo ===========================================================================

\i database/seed/012_seed_master.sql

\echo
\echo Loading Templates...
\i database/seed/013_seed_templates.sql

\echo
\echo Loading Sample Data...
\i database/seed/014_seed_sample.sql

-- ============================================================================
-- VALIDATION
-- ============================================================================

\echo
\echo ===========================================================================
\echo Running Database Validation...
\echo ===========================================================================

\i database/validation/001_verify_database.sql

-- ============================================================================
-- COMPLETION
-- ============================================================================

\echo
\echo ===========================================================================
\echo                    DATABASE DEPLOYMENT SUCCESSFUL
\echo ===========================================================================
\echo
\echo Database  : sirms
\echo Version   : 1.0
\echo Status    : READY FOR FASTAPI DEVELOPMENT
\echo
\echo Next Steps:
\echo   1. Verify validation output
\echo   2. Connect using pgAdmin/DBeaver
\echo   3. Review schemas and sample data
\echo   4. Generate SQLAlchemy models
\echo   5. Begin FastAPI backend development
\echo
\echo ===========================================================================
