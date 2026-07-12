-- ============================================================================
-- ARIMS / SIRMS
-- Database Reset and Deployment Script
-- Version : 1.0
-- PostgreSQL : 17+
--
-- Execute from the PROJECT ROOT:
--
--   psql -U svr_user -d sirms -h localhost -f database/redeploy.sql
-- ============================================================================

\set ON_ERROR_STOP on
\timing on

\echo
\echo ===========================================================================
\echo            ARIMS / SIRMS DATABASE RESET AND DEPLOYMENT
\echo ===========================================================================
\echo
\echo WARNING: This script permanently drops all ARIMS / SIRMS schemas
\echo          (`common`, `master`, `security`, `infrastructure`, `asset`, `incident`)
\echo          from the current database before redeploying Version 1.0.
\echo

\i database/reset.sql

\echo
\echo Existing ARIMS / SIRMS schemas cleared.
\echo Starting fresh deployment...
\echo

\i database/deploy.sql
