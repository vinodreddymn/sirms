/*
===============================================================================
Seed Data   : Replacement workflow sample
Description : Adds C2 store rooms, positions, and assets for workflow testing.
===============================================================================
*/

BEGIN;

-- Store rooms inside C2 Building
INSERT INTO infrastructure.locations (id, project_id, parent_location_id, location_type_id, code, name, remarks)
SELECT
    v.id,
    p.id,
    parent.id,
    lt.id,
    v.code,
    v.name,
    v.remarks
FROM (
    VALUES
        ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1'::UUID, 'STORE-C2-01', 'C2 Store Room 01', 'Primary equipment store'),
        ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2'::UUID, 'STORE-C2-02', 'C2 Store Room 02', 'Replacement equipment store')
) AS v(id, code, name, remarks)
JOIN common.projects p ON p.project_code = 'NAISS-INS-RAJALI'
JOIN infrastructure.locations parent ON parent.project_id = p.id AND parent.code = 'BLD-C2'
JOIN master.location_types lt ON lt.code = 'STORE'
ON CONFLICT (project_id, code) DO NOTHING;

-- Positions used by installed equipment in the store rooms
INSERT INTO infrastructure.location_positions (id, location_id, position_type_id, position_number, maximum_capacity, remarks)
SELECT v.id, l.id, pt.id, v.position_number, 1, v.remarks
FROM (
    VALUES
        ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb1'::UUID, 'STORE-C2-01', 'SWITCH_ENCLOSURE', 'SW-01', 'Switch position'),
        ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb2'::UUID, 'STORE-C2-01', 'CAMERA_MOUNT_1', 'CAM-01', 'Camera test position'),
        ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb3'::UUID, 'STORE-C2-02', 'CAMERA_MOUNT_1', 'CAM-01', 'Replacement camera position')
) AS v(id, location_code, position_type_code, position_number, remarks)
JOIN common.projects p ON p.project_code = 'NAISS-INS-RAJALI'
JOIN infrastructure.locations l ON l.project_id = p.id AND l.code = v.location_code
JOIN master.position_types pt ON pt.code = v.position_type_code
ON CONFLICT (location_id, position_type_id, position_number) DO NOTHING;

-- Installed camera and switch, plus spare camera and switch candidates
INSERT INTO asset.assets
(id, project_id, asset_number, asset_category_id, asset_subcategory_id, manufacturer_id, asset_model_id,
 asset_status_id, asset_condition_id, asset_lifecycle_id, serial_number, barcode, qr_code,
 current_location_id, asset_role, network_configuration, purchase_date, warranty_expiry, remarks)
SELECT
    v.id, p.id, v.asset_number, c.id, s.id, m.id, am.id, ast.id, ac.id, al.id,
    v.serial_number, v.barcode, v.qr_code, location.id, v.asset_role, v.network_configuration::JSONB,
    DATE '2026-04-01', DATE '2029-04-01', v.remarks
FROM (
    VALUES
        ('cccccccc-cccc-cccc-cccc-ccccccccccc1'::UUID, 'CAM-C2-001', 'SURVEILLANCE', 'FIXED_CAMERA', 'HIK', 'DS-2CD2047G2', 'INSTALLED', 'GOOD', 'IN_SERVICE', 'SN-C2-CAM-001', 'BAR-C2-CAM-001', 'QR-C2-CAM-001', 'STORE-C2-01', 'INSTALLED', '{"mac_address":"00:11:22:33:44:51"}', 'Installed camera for replacement test'),
        ('cccccccc-cccc-cccc-cccc-ccccccccccc2'::UUID, 'CAM-C2-SPARE-001', 'SURVEILLANCE', 'FIXED_CAMERA', 'HIK', 'DS-2CD2047G2', 'IN_STOCK', 'NEW', 'PROCURED', 'SN-C2-CAM-SPARE-001', 'BAR-C2-CAM-SPARE-001', 'QR-C2-CAM-SPARE-001', 'STORE-C2-02', 'SPARE', '{"mac_address":"00:11:22:33:44:52"}', 'Spare camera candidate'),
        ('cccccccc-cccc-cccc-cccc-ccccccccccc3'::UUID, 'SW-C2-001', 'NETWORK', 'SWITCH', 'CISCO', 'CBS350-24P', 'INSTALLED', 'GOOD', 'IN_SERVICE', 'SN-C2-SW-001', 'BAR-C2-SW-001', 'QR-C2-SW-001', 'STORE-C2-01', 'INSTALLED', '{"mac_address":"00:11:22:33:44:61"}', 'Installed switch'),
        ('cccccccc-cccc-cccc-cccc-ccccccccccc4'::UUID, 'SW-C2-SPARE-001', 'NETWORK', 'SWITCH', 'CISCO', 'CBS350-24P', 'IN_STOCK', 'NEW', 'PROCURED', 'SN-C2-SW-SPARE-001', 'BAR-C2-SW-SPARE-001', 'QR-C2-SW-SPARE-001', 'STORE-C2-02', 'SPARE', '{"mac_address":"00:11:22:33:44:62"}', 'Spare switch candidate')
) AS v(id, asset_number, category_code, subcategory_code, manufacturer_code, model_code, status_code, condition_code, lifecycle_code, serial_number, barcode, qr_code, location_code, asset_role, network_configuration, remarks)
JOIN common.projects p ON p.project_code = 'NAISS-INS-RAJALI'
JOIN master.asset_categories c ON c.code = v.category_code
JOIN master.asset_subcategories s ON s.code = v.subcategory_code
JOIN master.manufacturers m ON m.code = v.manufacturer_code
JOIN master.asset_models am ON am.code = v.model_code
JOIN master.asset_status ast ON ast.code = v.status_code
JOIN master.asset_condition ac ON ac.code = v.condition_code
JOIN master.asset_lifecycle al ON al.code = v.lifecycle_code
JOIN infrastructure.locations location ON location.project_id = p.id AND location.code = v.location_code
ON CONFLICT (asset_number) DO NOTHING;

-- Active installation for the faulty camera and installed switch
INSERT INTO asset.asset_installations (asset_id, location_position_id, installed_on, current_flag, remarks)
VALUES
('cccccccc-cccc-cccc-cccc-ccccccccccc1', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb2', DATE '2026-04-05', TRUE, 'Camera installed for replacement workflow test'),
('cccccccc-cccc-cccc-cccc-ccccccccccc3', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb1', DATE '2026-04-05', TRUE, 'Switch installed for sample data')
ON CONFLICT DO NOTHING;

COMMIT;
