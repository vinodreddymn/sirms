/*
===============================================================================
Seed Data   : Master
Description : Loads reference data and runtime security configuration.
===============================================================================
*/

INSERT INTO master.location_types (code, name, description, display_order) VALUES
('PROJECT', 'Project', 'Top-level project node', 1),
('BUILDING', 'Building', 'Permanent building', 2),
('FLOOR', 'Floor', 'Building floor', 3),
('ROOM', 'Room', 'Room or chamber inside a building', 4),
('POWER_STATION', 'Power Station', 'Electrical power station', 5),
('EQUIPMENT_ROOM', 'Equipment Room', 'Dedicated equipment room', 6),
('POLE', 'Pole', 'Field pole', 7),
('WATCH_TOWER', 'Watch Tower', 'Watch tower', 8),
('GATE', 'Gate', 'Entry or exit gate', 9),
('STORE', 'Store', 'Store or warehouse', 10),
('PORTABLE_OFFICE', 'Portable Office', 'Portable office unit', 11),
('CAMP', 'Camp', 'Camp location', 12),
('VOLTAGE_REGULATOR', 'Voltage Regulator', 'Voltage regulator node', 13)
ON CONFLICT (code) DO NOTHING;

INSERT INTO master.position_types (code, name, description, display_order) VALUES
('PTZ_MOUNT', 'PTZ Mount', 'PTZ camera mount', 1),
('CAMERA_MOUNT_1', 'Camera Mount 1', 'Fixed camera mount', 2),
('CAMERA_MOUNT_2', 'Camera Mount 2', 'Second fixed camera mount', 3),
('SWITCH_ENCLOSURE', 'Switch Enclosure', 'Switch enclosure', 4),
('MASTER_CONTROLLER', 'Master Controller', 'Master controller position', 5),
('JUNCTION_BOX', 'Junction Box', 'Junction box position', 6),
('LV_MODULE', 'LV Module', 'Low voltage module position', 7),
('UPS_POSITION', 'UPS Position', 'UPS installation position', 8),
('BATTERY_POSITION', 'Battery Position', 'Battery bank position', 9),
('HT_PANEL', 'HT Panel', 'High tension panel position', 10),
('LT_PANEL', 'LT Panel', 'Low tension panel position', 11),
('TRANSFORMER_POSITION', 'Transformer Position', 'Transformer position', 12),
('DG_POSITION', 'DG Position', 'Diesel generator position', 13),
('FUEL_TANK_POSITION', 'Fuel Tank Position', 'Fuel tank position', 14)
ON CONFLICT (code) DO NOTHING;

INSERT INTO master.asset_categories (code, name, description, display_order) VALUES
('SURVEILLANCE', 'Surveillance', 'Video surveillance equipment', 1),
('NETWORK', 'Network', 'Network devices', 2),
('POWER', 'Power', 'Power and backup systems', 3),
('ACCESS', 'Access Control', 'Access control equipment', 4),
('PERIMETER', 'Perimeter Security', 'Perimeter security devices', 5)
ON CONFLICT (code) DO NOTHING;

INSERT INTO master.asset_subcategories (asset_category_id, code, name, description, display_order)
SELECT c.id, v.code, v.name, v.description, v.display_order
FROM master.asset_categories c
JOIN (
    VALUES
        ('SURVEILLANCE', 'FIXED_CAMERA', 'Fixed Camera', 'Static surveillance camera', 1),
        ('SURVEILLANCE', 'PTZ_CAMERA', 'PTZ Camera', 'Pan tilt zoom camera', 2),
        ('NETWORK', 'SWITCH', 'Network Switch', 'Managed network switch', 3),
        ('NETWORK', 'CONTROLLER', 'Controller', 'Control system controller', 4),
        ('POWER', 'UPS', 'UPS', 'Uninterruptible power supply', 5),
        ('POWER', 'BATTERY_BANK', 'Battery Bank', 'Battery bank', 6),
        ('POWER', 'TRANSFORMER', 'Transformer', 'Power transformer', 7),
        ('POWER', 'DG', 'Diesel Generator', 'Diesel generator', 8),
        ('PERIMETER', 'JUNCTION_BOX_ASSET', 'Junction Box', 'Field junction box', 9)
) AS v(category_code, code, name, description, display_order)
    ON c.code = v.category_code
ON CONFLICT (code) DO NOTHING;

INSERT INTO master.manufacturers (code, name, description, display_order) VALUES
('HIK', 'Hikvision', 'Surveillance manufacturer', 1),
('CISCO', 'Cisco', 'Network manufacturer', 2),
('APC', 'APC', 'Power manufacturer', 3),
('SCHNEIDER', 'Schneider Electric', 'Electrical manufacturer', 4)
ON CONFLICT (code) DO NOTHING;

INSERT INTO master.asset_models (manufacturer_id, asset_subcategory_id, code, name, description, display_order)
SELECT m.id, s.id, v.code, v.name, v.description, v.display_order
FROM (
    VALUES
        ('HIK', 'FIXED_CAMERA', 'DS-2CD2047G2', 'Hikvision Bullet Camera', '4MP bullet camera', 1),
        ('HIK', 'PTZ_CAMERA', 'DS-2DE7A432IW', 'Hikvision PTZ Camera', 'PTZ surveillance camera', 2),
        ('CISCO', 'SWITCH', 'CBS350-24P', 'Cisco CBS350 24P', '24-port managed switch', 3),
        ('APC', 'UPS', 'SMT3000I', 'APC Smart UPS 3000', '3KVA UPS', 4),
        ('SCHNEIDER', 'TRANSFORMER', 'TR-11KV', 'Schneider Transformer', '11KV transformer', 5)
) AS v(manufacturer_code, subcategory_code, code, name, description, display_order)
JOIN master.manufacturers m ON m.code = v.manufacturer_code
JOIN master.asset_subcategories s ON s.code = v.subcategory_code
ON CONFLICT (code) DO NOTHING;

INSERT INTO master.asset_status (code, name, description, display_order) VALUES
('IN_STOCK', 'In Stock', 'Available in store', 1),
('INSTALLED', 'Installed', 'Installed and active', 2),
('UNDER_REPAIR', 'Under Repair', 'Under repair', 3),
('SCRAPPED', 'Scrapped', 'Disposed asset', 4)
ON CONFLICT (code) DO NOTHING;

INSERT INTO master.asset_condition (code, name, description, display_order) VALUES
('NEW', 'New', 'Brand new', 1),
('GOOD', 'Good', 'Good condition', 2),
('FAIR', 'Fair', 'Fair condition', 3),
('DAMAGED', 'Damaged', 'Damaged condition', 4)
ON CONFLICT (code) DO NOTHING;

INSERT INTO master.asset_lifecycle (code, name, description, display_order) VALUES
('PROCURED', 'Procured', 'Procured but not yet installed', 1),
('COMMISSIONED', 'Commissioned', 'Commissioned and active', 2),
('IN_SERVICE', 'In Service', 'Operational in field', 3),
('REPAIR', 'Repair', 'Under repair lifecycle stage', 4),
('RETIRED', 'Retired', 'Retired from service', 5)
ON CONFLICT (code) DO NOTHING;

INSERT INTO master.maintenance_types (code, name, description, display_order) VALUES
('PREVENTIVE', 'Preventive', 'Preventive maintenance', 1),
('CORRECTIVE', 'Corrective', 'Corrective maintenance', 2),
('BREAKDOWN', 'Breakdown', 'Breakdown response', 3)
ON CONFLICT (code) DO NOTHING;

INSERT INTO master.failure_categories (code, name, description, display_order) VALUES
('POWER_FAILURE', 'Power Failure', 'Power-related failure', 1),
('NETWORK_FAILURE', 'Network Failure', 'Network-related failure', 2),
('DEVICE_FAILURE', 'Device Failure', 'Device hardware failure', 3)
ON CONFLICT (code) DO NOTHING;

INSERT INTO master.root_cause_categories (code, name, description, display_order) VALUES
('AGING', 'Aging', 'Wear and aging', 1),
('SURGE', 'Power Surge', 'Power surge issue', 2),
('MISCONFIG', 'Misconfiguration', 'Configuration issue', 3)
ON CONFLICT (code) DO NOTHING;

INSERT INTO master.incident_status (code, name, description, display_order) VALUES
('OPEN', 'Open', 'New incident', 1),
('ASSIGNED', 'Assigned', 'Assigned to technician', 2),
('IN_PROGRESS', 'In Progress', 'Work in progress', 3),
('RESOLVED', 'Resolved', 'Resolved incident', 4),
('CLOSED', 'Closed', 'Closed incident', 5)
ON CONFLICT (code) DO NOTHING;

INSERT INTO master.incident_priority (code, name, description, display_order) VALUES
('LOW', 'Low', 'Low priority', 1),
('MEDIUM', 'Medium', 'Normal priority', 2),
('HIGH', 'High', 'High priority', 3),
('CRITICAL', 'Critical', 'Critical priority', 4)
ON CONFLICT (code) DO NOTHING;

INSERT INTO master.incident_categories (code, name, description, display_order) VALUES
('ASSET_FAILURE', 'Asset Failure', 'Asset-related issue', 1),
('SITE_OUTAGE', 'Site Outage', 'Site-level issue', 2),
('SECURITY_ALERT', 'Security Alert', 'Security event or alert', 3)
ON CONFLICT (code) DO NOTHING;

INSERT INTO master.work_order_status (code, name, description, display_order) VALUES
('PLANNED', 'Planned', 'Created work order', 1),
('RELEASED', 'Released', 'Released for execution', 2),
('IN_PROGRESS', 'In Progress', 'Being executed', 3),
('COMPLETED', 'Completed', 'Completed work order', 4),
('CANCELLED', 'Cancelled', 'Cancelled work order', 5)
ON CONFLICT (code) DO NOTHING;

INSERT INTO master.relationship_types (code, name, description, display_order) VALUES
('CONNECTED_TO', 'Connected To', 'Connected to related asset', 1),
('POWERED_BY', 'Powered By', 'Receives power from related asset', 2),
('MOUNTED_ON', 'Mounted On', 'Mounted on related asset', 3)
ON CONFLICT (code) DO NOTHING;

INSERT INTO master.document_types (code, name, description, display_order) VALUES
('WARRANTY', 'Warranty', 'Warranty document', 1),
('INVOICE', 'Invoice', 'Purchase invoice', 2),
('MANUAL', 'Manual', 'User or service manual', 3),
('REPORT', 'Report', 'Inspection report', 4)
ON CONFLICT (code) DO NOTHING;

INSERT INTO master.photo_types (code, name, description, display_order) VALUES
('ASSET', 'Asset Photo', 'Asset photograph', 1),
('INSTALLATION', 'Installation Photo', 'Installation photograph', 2),
('INCIDENT', 'Incident Photo', 'Incident photograph', 3)
ON CONFLICT (code) DO NOTHING;

INSERT INTO master.project_types (code, name, description, display_order) VALUES
('AIRPORT', 'Airport', 'Airport security project', 1),
('POWER', 'Power Utility', 'Power utility project', 2),
('CAMPUS', 'Campus', 'Campus project', 3)
ON CONFLICT (code) DO NOTHING;

INSERT INTO master.user_role_templates (code, name, description, display_order) VALUES
('ADMIN', 'Administrator', 'Full access role template', 1),
('SUPERVISOR', 'Supervisor', 'Supervisory role template', 2),
('TECHNICIAN', 'Technician', 'Technician role template', 3),
('VIEWER', 'Viewer', 'Read-only role template', 4)
ON CONFLICT (code) DO NOTHING;

INSERT INTO master.specification_definitions (asset_subcategory_id, code, name, data_type, unit_of_measure, required_flag, display_order)
SELECT s.id, v.code, v.name, v.data_type, v.unit_of_measure, v.required_flag, v.display_order
FROM (
    VALUES
        ('FIXED_CAMERA', 'RESOLUTION', 'Resolution', 'TEXT', NULL, TRUE, 1),
        ('FIXED_CAMERA', 'LENS', 'Lens', 'TEXT', NULL, FALSE, 2),
        ('FIXED_CAMERA', 'IR_DISTANCE', 'IR Distance', 'NUMBER', 'METER', FALSE, 3),
        ('PTZ_CAMERA', 'ONVIF', 'ONVIF', 'BOOLEAN', NULL, FALSE, 4),
        ('SWITCH', 'PORTS', 'Ports', 'NUMBER', 'COUNT', TRUE, 5),
        ('SWITCH', 'POE', 'PoE', 'BOOLEAN', NULL, FALSE, 6),
        ('UPS', 'KVA', 'KVA', 'NUMBER', 'KVA', TRUE, 7),
        ('UPS', 'BATTERY_CAPACITY', 'Battery Capacity', 'NUMBER', 'AH', FALSE, 8),
        ('UPS', 'INPUT_VOLTAGE', 'Input Voltage', 'NUMBER', 'VOLT', FALSE, 9)
) AS v(subcategory_code, code, name, data_type, unit_of_measure, required_flag, display_order)
JOIN master.asset_subcategories s ON s.code = v.subcategory_code
ON CONFLICT (code) DO NOTHING;

INSERT INTO master.movement_types (code, name, description, display_order) VALUES
('RECEIVE', 'Receive', 'Received into stock', 1),
('ISSUE', 'Issue', 'Issued to field', 2),
('TRANSFER', 'Transfer', 'Transferred between locations', 3),
('REPAIR', 'Repair', 'Sent for repair', 4),
('OEM', 'OEM', 'Moved to OEM', 5),
('SCRAP', 'Scrap', 'Scrapped asset', 6),
('ADJUSTMENT', 'Adjustment', 'Stock adjustment', 7)
ON CONFLICT (code) DO NOTHING;

INSERT INTO master.stock_transaction_types (code, name, quantity_effect, description, display_order) VALUES
('RECEIVE', 'Receive', 1, 'Receipt into stock', 1),
('ISSUE', 'Issue', -1, 'Issue from stock', 2),
('TRANSFER_IN', 'Transfer In', 1, 'Transfer receipt', 3),
('TRANSFER_OUT', 'Transfer Out', -1, 'Transfer issue', 4),
('REPAIR_OUT', 'Repair Out', -1, 'Sent for repair', 5),
('REPAIR_IN', 'Repair In', 1, 'Returned from repair', 6),
('SCRAP', 'Scrap', -1, 'Scrap transaction', 7),
('ADJUSTMENT_IN', 'Adjustment In', 1, 'Positive adjustment', 8),
('ADJUSTMENT_OUT', 'Adjustment Out', -1, 'Negative adjustment', 9)
ON CONFLICT (code) DO NOTHING;

INSERT INTO security.permissions (id, permission_code, permission_name, module_name, description)
VALUES
('55555555-5555-5555-5555-555555555551', 'ASSET_VIEW', 'View Assets', 'ASSET', 'View asset records'),
('55555555-5555-5555-5555-555555555552', 'ASSET_EDIT', 'Edit Assets', 'ASSET', 'Create and update assets'),
('55555555-5555-5555-5555-555555555553', 'INCIDENT_VIEW', 'View Incidents', 'INCIDENT', 'View incidents'),
('55555555-5555-5555-5555-555555555554', 'INCIDENT_EDIT', 'Edit Incidents', 'INCIDENT', 'Create and update incidents'),
('55555555-5555-5555-5555-555555555555', 'MAINT_VIEW', 'View Maintenance', 'ASSET', 'View maintenance data'),
('55555555-5555-5555-5555-555555555556', 'MAINT_EDIT', 'Edit Maintenance', 'ASSET', 'Update maintenance data')
ON CONFLICT (permission_code) DO NOTHING;
