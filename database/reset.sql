-- ============================================================================
-- ARIMS / SIRMS
-- Database Reset Script
-- Version : 1.0
-- PostgreSQL : 17+
--
-- Execute from the PROJECT ROOT:
--
--   psql -U svr_user -d sirms -h localhost -f database/reset.sql
-- ============================================================================

\set ON_ERROR_STOP on
\timing on

\echo
\echo ===========================================================================
\echo                    ARIMS / SIRMS DATABASE RESET
\echo ===========================================================================
\echo
\echo WARNING: This script permanently drops all ARIMS / SIRMS schemas
\echo          from the current database.
\echo

DROP SCHEMA IF EXISTS incident CASCADE;
DROP SCHEMA IF EXISTS asset CASCADE;
DROP SCHEMA IF EXISTS infrastructure CASCADE;
DROP SCHEMA IF EXISTS common CASCADE;
DROP SCHEMA IF EXISTS security CASCADE;
DROP SCHEMA IF EXISTS master CASCADE;

\echo
\echo ===========================================================================
\echo                    DATABASE RESET COMPLETED
\echo ===========================================================================
\echo
