/*
===============================================================================
Seed Data   : Locations
Description : Dynamically generates and loads location hierarchy seed data.
===============================================================================
*/

BEGIN;

-- 1. Ensure location types used by this seed exist
INSERT INTO master.location_types (code, name, description, display_order)
VALUES
    ('LOCATION_GROUP', 'Location Group', 'Grouping node for related project locations', 14),
    ('LTE_TOWER', 'LTE Tower', 'Long-Term Evolution cellular tower', 15)
ON CONFLICT (code) DO NOTHING;

-- 2. Ensure base customer exists
INSERT INTO common.customers (id, customer_code, customer_name, contact_person, remarks)
VALUES ('11111111-1111-1111-1111-111111111111', 'CUST001', 'Demo Customer', 'Operations Head', 'Reference customer')
ON CONFLICT (customer_code) DO NOTHING;

-- 3. Ensure the target project NAISS-INS-RAJALI exists
INSERT INTO common.projects (id, customer_id, project_type_id, project_code, project_name, start_date, remarks)
SELECT
    '99999999-9999-9999-9999-999999999999'::UUID,
    c.id,
    pt.id,
    'NAISS-INS-RAJALI',
    'NAISS INS RAJALI Airport Project',
    DATE '2026-01-01',
    'Project for location seeding framework'
FROM common.customers c
JOIN master.project_types pt ON pt.code = 'AIRPORT'
WHERE c.customer_code = 'CUST001'
ON CONFLICT (project_code) DO NOTHING;

-- 4. Clear the staging table to ensure a fresh seed
TRUNCATE TABLE master.location_seed;

-- 5. Seed static hierarchy (Root, Building, Floor, Room)
INSERT INTO master.location_seed (parent_code, location_type_code, code, name, remarks) VALUES
(NULL, 'PROJECT', 'NAISS-INS-RAJALI', 'NAISS INS RAJALI', 'Project root location'),
('NAISS-INS-RAJALI', 'BUILDING', 'BLD-C2', 'C2 Building', 'Main control building'),
('BLD-C2', 'FLOOR', 'GF', 'Ground Floor', 'Ground floor'),
('GF', 'ROOM', 'CONFERENCE', 'Conference Room', 'Main conference room');

-- 6. Seed infrastructure groups and their child locations
INSERT INTO master.location_seed (parent_code, location_type_code, code, name, remarks) VALUES
('NAISS-INS-RAJALI', 'LOCATION_GROUP', 'POWER-STATIONS', 'Power Stations', 'Group containing all power stations'),
('NAISS-INS-RAJALI', 'LOCATION_GROUP', 'WATCH-TOWERS', 'Watch Towers', 'Group containing all perimeter watch towers'),
('NAISS-INS-RAJALI', 'LOCATION_GROUP', 'PERIMETER-POLES', 'Perimeter Poles', 'Group containing all perimeter poles'),
('NAISS-INS-RAJALI', 'LOCATION_GROUP', 'LTE-TOWERS', 'LTE Towers', 'Group containing all LTE cellular towers');

-- Power Stations (PS-01 to PS-09)
INSERT INTO master.location_seed (parent_code, location_type_code, code, name, remarks)
SELECT 
    'POWER-STATIONS',
    'POWER_STATION',
    format('PS-%02s', i),
    format('Power Station %02s', i),
    format('Power station number %s', i)
FROM generate_series(1, 9) i;

-- Watch Towers (WT-01 to WT-40)
INSERT INTO master.location_seed (parent_code, location_type_code, code, name, remarks)
SELECT 
    'WATCH-TOWERS',
    'WATCH_TOWER',
    format('WT-%02s', i),
    format('Watch Tower %02s', i),
    format('Perimeter watch tower %s', i)
FROM generate_series(1, 40) i;

-- Perimeter Poles (P-001 to P-180)
INSERT INTO master.location_seed (parent_code, location_type_code, code, name, remarks)
SELECT 
    'PERIMETER-POLES',
    'POLE',
    format('P-%03s', i),
    format('Pole %03s', i),
    format('Perimeter pole number %s', i)
FROM generate_series(1, 180) i;

-- LTE Towers (LTE-01 to LTE-05)
INSERT INTO master.location_seed (parent_code, location_type_code, code, name, remarks)
SELECT 
    'LTE-TOWERS',
    'LTE_TOWER',
    format('LTE-%02s', i),
    format('LTE Tower %02s', i),
    format('LTE cellular tower %s', i)
FROM generate_series(1, 5) i;

-- 7. Execute the dynamic import procedure to populate infrastructure.locations
CALL infrastructure.import_locations();

-- 8. Re-parent existing assets when this seed is rerun against an existing project
UPDATE infrastructure.locations asset
SET parent_location_id = parent.id
FROM infrastructure.locations parent
WHERE asset.project_id = (SELECT id FROM common.projects WHERE project_code = 'NAISS-INS-RAJALI')
  AND parent.project_id = asset.project_id
  AND (
      (asset.code LIKE 'PS-%' AND parent.code = 'POWER-STATIONS')
      OR (asset.code LIKE 'WT-%' AND parent.code = 'WATCH-TOWERS')
      OR (asset.code LIKE 'P-%' AND parent.code = 'PERIMETER-POLES')
      OR (asset.code LIKE 'LTE-[0-9]%' AND parent.code = 'LTE-TOWERS')
  );

COMMIT;
