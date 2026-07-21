/*
===============================================================================
Project     : SIRMS
Version     : 1.0
Module      : Infrastructure
Description : Creates the staging table for data-driven location seeding.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS master.location_seed
(
    parent_code         VARCHAR(50),
    location_type_code  VARCHAR(30) NOT NULL REFERENCES master.location_types(code) ON UPDATE RESTRICT ON DELETE RESTRICT,
    code                VARCHAR(50) NOT NULL PRIMARY KEY,
    name                VARCHAR(200) NOT NULL,
    remarks             TEXT,
    display_order       INTEGER DEFAULT 0
);

COMMENT ON TABLE master.location_seed IS 'Staging table for data-driven location seeding.';
