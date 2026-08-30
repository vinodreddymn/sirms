/*
===============================================================================
Seed Data   : Sample
Description : Loads sample customers, projects, assets, incidents, and work.
===============================================================================
*/

INSERT INTO common.customers
(id, customer_code, customer_name, contact_person, contact_email, contact_phone, remarks)
VALUES
('11111111-1111-1111-1111-111111111111', 'CUST001', 'Demo Customer', 'Operations Head', 'ops@demo.example', '+91-9000000001', 'Reference customer')
ON CONFLICT (customer_code) DO NOTHING;

INSERT INTO common.projects
(id, customer_id, project_type_id, project_code, project_name, start_date, remarks)
SELECT
    '22222222-2222-2222-2222-222222222222',
    c.id,
    pt.id,
    'PRJ001',
    'Demo Airport Security Upgrade',
    DATE '2026-01-01',
    'Primary sample project'
FROM common.customers c
JOIN master.project_types pt ON pt.code = 'AIRPORT'
WHERE c.customer_code = 'CUST001'
ON CONFLICT (project_code) DO NOTHING;

INSERT INTO common.vendors
(id, vendor_code, vendor_name, vendor_type, contact_person, contact_email, remarks)
VALUES
('12121212-1212-1212-1212-121212121212', 'VEND001', 'Demo OEM Services', 'OEM', 'OEM Coordinator', 'oem@demo.example', 'Reference OEM vendor')
ON CONFLICT (vendor_code) DO NOTHING;

INSERT INTO security.users
(id, username, full_name, email, mobile_number, password_hash, default_project_id)
VALUES
('33333333-3333-3333-3333-333333333331', 'admin', 'System Admin', 'admin@demo.example', '+91-9000000002', 'demo_hash_admin', '22222222-2222-2222-2222-222222222222'),
('33333333-3333-3333-3333-333333333332', 'supervisor', 'Site Supervisor', 'supervisor@demo.example', '+91-9000000003', 'demo_hash_supervisor', '22222222-2222-2222-2222-222222222222'),
('33333333-3333-3333-3333-333333333333', 'tech01', 'Field Technician', 'tech01@demo.example', '+91-9000000004', 'demo_hash_tech01', '22222222-2222-2222-2222-222222222222')
ON CONFLICT (username) DO NOTHING;

INSERT INTO security.roles
(id, role_template_id, role_code, role_name, description, is_system_role)
SELECT
    v.id,
    urt.id,
    v.role_code,
    v.role_name,
    v.description,
    v.is_system_role
FROM (
    VALUES
        ('44444444-4444-4444-4444-444444444441'::UUID, 'ADMIN', 'ADMIN', 'Administrator', 'System administrators', TRUE),
        ('44444444-4444-4444-4444-444444444442'::UUID, 'SUPERVISOR', 'SUPERVISOR', 'Supervisor', 'Project supervisors', FALSE),
        ('44444444-4444-4444-4444-444444444443'::UUID, 'TECHNICIAN', 'TECHNICIAN', 'Technician', 'Maintenance technicians', FALSE)
) AS v(id, role_template_code, role_code, role_name, description, is_system_role)
JOIN master.user_role_templates urt ON urt.code = v.role_template_code
ON CONFLICT (role_code) DO NOTHING;

INSERT INTO security.role_permissions (role_id, permission_id)
VALUES
('44444444-4444-4444-4444-444444444441', '55555555-5555-5555-5555-555555555551'),
('44444444-4444-4444-4444-444444444441', '55555555-5555-5555-5555-555555555552'),
('44444444-4444-4444-4444-444444444441', '55555555-5555-5555-5555-555555555553'),
('44444444-4444-4444-4444-444444444441', '55555555-5555-5555-5555-555555555554'),
('44444444-4444-4444-4444-444444444441', '55555555-5555-5555-5555-555555555555'),
('44444444-4444-4444-4444-444444444441', '55555555-5555-5555-5555-555555555556'),
('44444444-4444-4444-4444-444444444442', '55555555-5555-5555-5555-555555555551'),
('44444444-4444-4444-4444-444444444442', '55555555-5555-5555-5555-555555555553'),
('44444444-4444-4444-4444-444444444443', '55555555-5555-5555-5555-555555555551'),
('44444444-4444-4444-4444-444444444443', '55555555-5555-5555-5555-555555555555')
ON CONFLICT (role_id, permission_id) DO NOTHING;

INSERT INTO security.user_roles (user_id, role_id, project_id)
VALUES
('33333333-3333-3333-3333-333333333331', '44444444-4444-4444-4444-444444444441', '22222222-2222-2222-2222-222222222222'),
('33333333-3333-3333-3333-333333333332', '44444444-4444-4444-4444-444444444442', '22222222-2222-2222-2222-222222222222'),
('33333333-3333-3333-3333-333333333333', '44444444-4444-4444-4444-444444444443', '22222222-2222-2222-2222-222222222222')
ON CONFLICT (user_id, role_id, project_id) DO NOTHING;

INSERT INTO common.number_sequences
(id, entity_name, prefix, current_value, number_length, reset_policy)
VALUES
('abababab-abab-abab-abab-ababababab01', 'ASSET_CAMERA', 'CAM', 1, 6, 'NEVER'),
('abababab-abab-abab-abab-ababababab02', 'ASSET_UPS', 'UPS', 20, 6, 'NEVER'),
('abababab-abab-abab-abab-ababababab03', 'LOCATION_POLE', 'POL', 855, 6, 'NEVER'),
('abababab-abab-abab-abab-ababababab06', 'PREVENTIVE_MAINTENANCE', 'PM', 0, 6, 'NEVER'),
('abababab-abab-abab-abab-ababababab04', 'INCIDENT', 'INC', 152, 6, 'NEVER'),
('abababab-abab-abab-abab-ababababab05', 'WORK_ORDER', 'WO', 74, 6, 'NEVER')
ON CONFLICT (entity_name) DO NOTHING;

INSERT INTO infrastructure.locations
(id, project_id, parent_location_id, location_type_id, code, name, latitude, longitude, remarks)
SELECT
    v.id,
    '22222222-2222-2222-2222-222222222222',
    v.parent_location_id,
    lt.id,
    v.code,
    v.name,
    v.latitude,
    v.longitude,
    v.remarks
FROM (
    VALUES
        ('66666666-6666-6666-6666-666666666661'::UUID, NULL::UUID, 'PROJECT', 'PRJ001-ROOT', 'Demo Project Root', 12.9500000, 80.1800000, 'Logical root node'),
        ('66666666-6666-6666-6666-666666666662'::UUID, '66666666-6666-6666-6666-666666666661'::UUID, 'BUILDING', 'BLD-A', 'Building A', 12.9501000, 80.1801000, 'Operations building'),
        ('66666666-6666-6666-6666-666666666663'::UUID, '66666666-6666-6666-6666-666666666662'::UUID, 'FLOOR', 'BLD-A-F1', 'Building A - Floor 1', NULL, NULL, 'First floor'),
        ('66666666-6666-6666-6666-666666666664'::UUID, '66666666-6666-6666-6666-666666666663'::UUID, 'ROOM', 'CTRL-101', 'Control Room 101', NULL, NULL, 'Control room'),
        ('66666666-6666-6666-6666-666666666665'::UUID, '66666666-6666-6666-6666-666666666661'::UUID, 'POWER_STATION', 'PS-01', 'Power Station 01', 12.9510000, 80.1810000, 'Primary power station'),
        ('66666666-6666-6666-6666-666666666666'::UUID, '66666666-6666-6666-6666-666666666661'::UUID, 'POLE', 'P-01', 'Pole 01', 12.9520000, 80.1820000, 'Perimeter pole')
) AS v(id, parent_location_id, location_type_code, code, name, latitude, longitude, remarks)
JOIN master.location_types lt ON lt.code = v.location_type_code
ON CONFLICT (project_id, code) DO NOTHING;

INSERT INTO infrastructure.location_positions
(id, location_id, position_type_id, position_number, maximum_capacity, remarks)
SELECT
    v.id,
    v.location_id,
    pt.id,
    v.position_number,
    v.maximum_capacity,
    v.remarks
FROM (
    VALUES
        ('77777777-7777-7777-7777-777777777771'::UUID, '66666666-6666-6666-6666-666666666664'::UUID, 'SWITCH_ENCLOSURE', 'SE-01', 1, 'Core switch enclosure'),
        ('77777777-7777-7777-7777-777777777772'::UUID, '66666666-6666-6666-6666-666666666665'::UUID, 'UPS_POSITION', 'UPS-01', 1, 'UPS bay'),
        ('77777777-7777-7777-7777-777777777773'::UUID, '66666666-6666-6666-6666-666666666666'::UUID, 'CAMERA_MOUNT_1', 'CAM-01', 1, 'Pole mounted camera position')
) AS v(id, location_id, position_type_code, position_number, maximum_capacity, remarks)
JOIN master.position_types pt ON pt.code = v.position_type_code
ON CONFLICT (location_id, position_type_id, position_number) DO NOTHING;

INSERT INTO asset.assets
(id, project_id, asset_number, asset_category_id, asset_subcategory_id, manufacturer_id, asset_model_id, asset_status_id, asset_condition_id, asset_lifecycle_id, serial_number, barcode, qr_code, purchase_date, warranty_expiry, remarks)
SELECT
    v.id,
    '22222222-2222-2222-2222-222222222222',
    v.asset_number,
    c.id,
    s.id,
    m.id,
    am.id,
    ast.id,
    ac.id,
    al.id,
    v.serial_number,
    v.barcode,
    v.qr_code,
    v.purchase_date,
    v.warranty_expiry,
    v.remarks
FROM (
    VALUES
        ('88888888-8888-8888-8888-888888888881'::UUID, 'CAM000001', 'SURVEILLANCE', 'FIXED_CAMERA', 'HIK', 'DS-2CD2047G2', 'INSTALLED', 'GOOD', 'IN_SERVICE', 'SN-CAM-0001', 'BAR-CAM-0001', 'QR-CAM-0001', DATE '2026-02-01', DATE '2028-02-01', 'Installed pole camera'),
        ('88888888-8888-8888-8888-888888888882'::UUID, 'UPS000021', 'POWER', 'UPS', 'APC', 'SMT3000I', 'INSTALLED', 'GOOD', 'COMMISSIONED', 'SN-UPS-0001', 'BAR-UPS-0001', 'QR-UPS-0001', DATE '2026-02-10', DATE '2028-02-10', 'Installed UPS')
) AS v(id, asset_number, category_code, subcategory_code, manufacturer_code, model_code, status_code, condition_code, lifecycle_code, serial_number, barcode, qr_code, purchase_date, warranty_expiry, remarks)
JOIN master.asset_categories c ON c.code = v.category_code
JOIN master.asset_subcategories s ON s.code = v.subcategory_code
JOIN master.manufacturers m ON m.code = v.manufacturer_code
JOIN master.asset_models am ON am.code = v.model_code
JOIN master.asset_status ast ON ast.code = v.status_code
JOIN master.asset_condition ac ON ac.code = v.condition_code
JOIN master.asset_lifecycle al ON al.code = v.lifecycle_code
ON CONFLICT (asset_number) DO NOTHING;

INSERT INTO asset.asset_specifications
(asset_id, specification_definition_id, value_text, value_number, value_boolean)
SELECT '88888888-8888-8888-8888-888888888881', sd.id,
       CASE WHEN sd.code IN ('RESOLUTION', 'LENS') THEN CASE sd.code WHEN 'RESOLUTION' THEN '4MP' ELSE '2.8mm' END END,
       CASE WHEN sd.code = 'IR_DISTANCE' THEN 60 END,
       CASE WHEN sd.code = 'ONVIF' THEN TRUE END
FROM master.specification_definitions sd
WHERE sd.code IN ('RESOLUTION', 'LENS', 'IR_DISTANCE')
ON CONFLICT (asset_id, specification_definition_id) DO NOTHING;

INSERT INTO asset.asset_installations
(asset_id, location_position_id, installed_on, current_flag, installed_by, remarks)
VALUES
('88888888-8888-8888-8888-888888888881', '77777777-7777-7777-7777-777777777773', DATE '2026-03-01', TRUE, '33333333-3333-3333-3333-333333333333', 'Camera installed on pole'),
('88888888-8888-8888-8888-888888888882', '77777777-7777-7777-7777-777777777772', DATE '2026-03-02', TRUE, '33333333-3333-3333-3333-333333333333', 'UPS installed in power station');

INSERT INTO asset.asset_movements
(asset_id, movement_type_id, from_location_id, to_location_id, movement_date, reference_document, remarks)
SELECT
    v.asset_id,
    mt.id,
    v.from_location_id,
    v.to_location_id,
    v.movement_date,
    v.reference_document,
    v.remarks
FROM (
    VALUES
        ('88888888-8888-8888-8888-888888888881'::UUID, 'RECEIVE', NULL::UUID, '66666666-6666-6666-6666-666666666666'::UUID, TIMESTAMP '2026-03-01 09:00:00', 'WO-INST-001', 'Initial camera installation'),
        ('88888888-8888-8888-8888-888888888882'::UUID, 'RECEIVE', NULL::UUID, '66666666-6666-6666-6666-666666666665'::UUID, TIMESTAMP '2026-03-02 10:00:00', 'WO-INST-002', 'Initial UPS installation')
) AS v(asset_id, movement_type_code, from_location_id, to_location_id, movement_date, reference_document, remarks)
JOIN master.movement_types mt ON mt.code = v.movement_type_code;

INSERT INTO asset.stock_transactions
(project_id, asset_id, stock_transaction_type_id, location_id, quantity, transaction_date, reference_number, remarks)
SELECT
    '22222222-2222-2222-2222-222222222222',
    v.asset_id,
    stt.id,
    v.location_id,
    1,
    v.transaction_date,
    v.reference_number,
    v.remarks
FROM (
    VALUES
        ('88888888-8888-8888-8888-888888888881'::UUID, 'ISSUE', '66666666-6666-6666-6666-666666666666'::UUID, TIMESTAMP '2026-03-01 09:00:00', 'STK-001', 'Issued to pole'),
        ('88888888-8888-8888-8888-888888888882'::UUID, 'ISSUE', '66666666-6666-6666-6666-666666666665'::UUID, TIMESTAMP '2026-03-02 10:00:00', 'STK-002', 'Issued to power station')
) AS v(asset_id, stock_transaction_type_code, location_id, transaction_date, reference_number, remarks)
JOIN master.stock_transaction_types stt ON stt.code = v.stock_transaction_type_code;

INSERT INTO asset.asset_relationships
(asset_id, related_asset_id, relationship_type_id, remarks)
SELECT
    '88888888-8888-8888-8888-888888888881',
    '88888888-8888-8888-8888-888888888882',
    rt.id,
    'Camera backed up by UPS infrastructure'
FROM master.relationship_types rt
WHERE rt.code = 'POWERED_BY'
ON CONFLICT (asset_id, related_asset_id, relationship_type_id) DO NOTHING;

INSERT INTO asset.maintenance_checklists
(id, asset_subcategory_id, maintenance_type_id, checklist_code, checklist_name, remarks)
SELECT
    '99999999-9999-9999-9999-999999999991',
    s.id,
    mt.id,
    'CHK-CAM-PM',
    'Camera Preventive Checklist',
    'Monthly camera check'
FROM master.asset_subcategories s
JOIN master.maintenance_types mt ON mt.code = 'PREVENTIVE'
WHERE s.code = 'FIXED_CAMERA'
ON CONFLICT (checklist_code) DO NOTHING;

INSERT INTO asset.checklist_items
(checklist_id, item_sequence, item_description, is_mandatory, remarks)
VALUES
('99999999-9999-9999-9999-999999999991', 1, 'Verify camera focus and image quality', TRUE, NULL),
('99999999-9999-9999-9999-999999999991', 2, 'Inspect mount tightness', TRUE, NULL),
('99999999-9999-9999-9999-999999999991', 3, 'Clean lens housing', TRUE, NULL)
ON CONFLICT (checklist_id, item_sequence) DO NOTHING;

INSERT INTO asset.maintenance_schedules
(id, asset_id, maintenance_type_id, checklist_id, schedule_start_date, frequency_days, next_due_date, assigned_to, vendor_id, remarks)
SELECT
    '99999999-9999-9999-9999-999999999992',
    '88888888-8888-8888-8888-888888888881',
    mt.id,
    '99999999-9999-9999-9999-999999999991',
    DATE '2026-04-01',
    30,
    DATE '2026-05-01',
    '33333333-3333-3333-3333-333333333333',
    '12121212-1212-1212-1212-121212121212',
    'Monthly PM'
FROM master.maintenance_types mt
WHERE mt.code = 'PREVENTIVE'
ON CONFLICT (id) DO NOTHING;

INSERT INTO incident.incidents
(id, project_id, incident_number, incident_category_id, reported_date, asset_id, location_id, reported_by, incident_priority_id, description, incident_status_id, assigned_to)
SELECT
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1',
    '22222222-2222-2222-2222-222222222222',
    'INC000153',
    ic.id,
    TIMESTAMP '2026-06-10 08:30:00',
    '88888888-8888-8888-8888-888888888881',
    '66666666-6666-6666-6666-666666666666',
    '33333333-3333-3333-3333-333333333332',
    ip.id,
    'Camera feed intermittent during rain.',
    ist.id,
    '33333333-3333-3333-3333-333333333333'
FROM master.incident_priority ip
JOIN master.incident_status ist ON ist.code = 'ASSIGNED'
JOIN master.incident_categories ic ON ic.code = 'ASSET_FAILURE'
WHERE ip.code = 'HIGH'
ON CONFLICT (incident_number) DO NOTHING;

INSERT INTO incident.incident_updates
(incident_id, update_datetime, update_user_id, remarks, status_after_update_id)
SELECT
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1',
    TIMESTAMP '2026-06-10 09:15:00',
    '33333333-3333-3333-3333-333333333333',
    'Technician assigned and site visit started.',
    ist.id
FROM master.incident_status ist
WHERE ist.code = 'IN_PROGRESS';

INSERT INTO incident.work_orders
(id, work_order_number, incident_id, assigned_to, vendor_id, planned_start, actual_start, work_order_status_id)
SELECT
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb1',
    'WO000075',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1',
    '33333333-3333-3333-3333-333333333333',
    '12121212-1212-1212-1212-121212121212',
    TIMESTAMP '2026-06-10 09:00:00',
    TIMESTAMP '2026-06-10 09:20:00',
    wos.id
FROM master.work_order_status wos
WHERE wos.code = 'IN_PROGRESS'
ON CONFLICT (work_order_number) DO NOTHING;

INSERT INTO incident.work_order_tasks
(work_order_id, task_sequence, task_description, assigned_to)
VALUES
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb1', 1, 'Inspect camera enclosure and connectors', '33333333-3333-3333-3333-333333333333'),
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb1', 2, 'Test power stability and network connectivity', '33333333-3333-3333-3333-333333333333')
ON CONFLICT (work_order_id, task_sequence) DO NOTHING;

INSERT INTO common.watch_list (user_id, incident_id)
VALUES
('33333333-3333-3333-3333-333333333332', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1')
ON CONFLICT (user_id, incident_id) DO NOTHING;

INSERT INTO common.notification_preferences
(user_id, email_enabled, sms_enabled, push_enabled)
VALUES
('33333333-3333-3333-3333-333333333331', TRUE, FALSE, TRUE),
('33333333-3333-3333-3333-333333333332', TRUE, TRUE, TRUE),
('33333333-3333-3333-3333-333333333333', TRUE, TRUE, FALSE)
ON CONFLICT (user_id) DO NOTHING;
