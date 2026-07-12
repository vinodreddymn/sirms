/*
===============================================================================
Project     : SIRMS
Version     : 1.0
Module      : Foundation
Description : Creates required PostgreSQL extensions and application schemas.
===============================================================================
*/

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE SCHEMA IF NOT EXISTS common;
CREATE SCHEMA IF NOT EXISTS master;
CREATE SCHEMA IF NOT EXISTS security;
CREATE SCHEMA IF NOT EXISTS infrastructure;
CREATE SCHEMA IF NOT EXISTS asset;
CREATE SCHEMA IF NOT EXISTS incident;

COMMENT ON SCHEMA common IS 'Shared application tables and utilities.';
COMMENT ON SCHEMA master IS 'Reference and lookup data.';
COMMENT ON SCHEMA security IS 'Authentication, authorization, and token management.';
COMMENT ON SCHEMA infrastructure IS 'Projects, locations, templates, and positions.';
COMMENT ON SCHEMA asset IS 'Asset register, movement, stock, and maintenance.';
COMMENT ON SCHEMA incident IS 'Incidents, updates, work orders, and related tracking.';
