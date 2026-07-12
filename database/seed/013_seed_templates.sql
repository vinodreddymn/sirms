/*
===============================================================================
Seed Data   : Templates
Description : Loads reusable location and position templates.
===============================================================================
*/

INSERT INTO master.position_templates (code, name, description, display_order) VALUES
('POLE_STD', 'Standard Pole Template', 'Default pole equipment positions', 1),
('POWER_STATION_STD', 'Standard Power Station Template', 'Default power station positions', 2),
('WATCH_TOWER_STD', 'Standard Watch Tower Template', 'Default watch tower equipment positions', 3),
('GATE_STD', 'Standard Gate Template', 'Default gate equipment positions', 4),
('STORE_STD', 'Standard Store Template', 'Default store equipment positions', 5)
ON CONFLICT (code) DO NOTHING;

INSERT INTO master.position_template_nodes (position_template_id, position_type_id, position_number, maximum_capacity, node_order, remarks)
SELECT pt.id, pty.id, v.position_number, v.maximum_capacity, v.node_order, v.remarks
FROM (
    VALUES
        ('POLE_STD', 'PTZ_MOUNT', 'PTZ-01', 1, 1, 'PTZ mount'),
        ('POLE_STD', 'CAMERA_MOUNT_1', 'CAM-01', 1, 2, 'Fixed camera 1'),
        ('POLE_STD', 'CAMERA_MOUNT_2', 'CAM-02', 1, 3, 'Fixed camera 2'),
        ('POLE_STD', 'SWITCH_ENCLOSURE', 'SW-01', 1, 4, 'Switch enclosure'),
        ('POLE_STD', 'MASTER_CONTROLLER', 'CTRL-01', 1, 5, 'Master controller'),
        ('POLE_STD', 'JUNCTION_BOX', 'JB-01', 1, 6, 'Junction box'),
        ('POLE_STD', 'LV_MODULE', 'LV-01', 1, 7, 'LV module'),
        ('POWER_STATION_STD', 'TRANSFORMER_POSITION', 'TR-01', 1, 1, 'Transformer'),
        ('POWER_STATION_STD', 'HT_PANEL', 'HT-01', 1, 2, 'HT panel'),
        ('POWER_STATION_STD', 'LT_PANEL', 'LT-01', 1, 3, 'LT panel'),
        ('POWER_STATION_STD', 'UPS_POSITION', 'UPS-01', 1, 4, 'UPS 1'),
        ('POWER_STATION_STD', 'BATTERY_POSITION', 'BAT-01', 1, 5, 'Battery bank 1'),
        ('POWER_STATION_STD', 'UPS_POSITION', 'UPS-02', 1, 6, 'UPS 2'),
        ('POWER_STATION_STD', 'BATTERY_POSITION', 'BAT-02', 1, 7, 'Battery bank 2'),
        ('POWER_STATION_STD', 'DG_POSITION', 'DG-01', 1, 8, 'Diesel generator'),
        ('POWER_STATION_STD', 'FUEL_TANK_POSITION', 'FT-01', 1, 9, 'Fuel tank'),
        ('WATCH_TOWER_STD', 'PTZ_MOUNT', 'PTZ-01', 1, 1, 'Tower PTZ mount'),
        ('WATCH_TOWER_STD', 'CAMERA_MOUNT_1', 'CAM-01', 1, 2, 'Tower camera mount'),
        ('WATCH_TOWER_STD', 'SWITCH_ENCLOSURE', 'SW-01', 1, 3, 'Tower switch enclosure'),
        ('GATE_STD', 'CAMERA_MOUNT_1', 'CAM-01', 1, 1, 'Gate camera mount'),
        ('GATE_STD', 'SWITCH_ENCLOSURE', 'SW-01', 1, 2, 'Gate switch enclosure'),
        ('STORE_STD', 'SWITCH_ENCLOSURE', 'SW-01', 1, 1, 'Store switch enclosure'),
        ('STORE_STD', 'UPS_POSITION', 'UPS-01', 1, 2, 'Store UPS position')
) AS v(template_code, position_type_code, position_number, maximum_capacity, node_order, remarks)
JOIN master.position_templates pt ON pt.code = v.template_code
JOIN master.position_types pty ON pty.code = v.position_type_code
ON CONFLICT (position_template_id, position_number) DO NOTHING;

INSERT INTO master.location_templates (code, name, description, display_order) VALUES
('POLE_SITE', 'Pole Location Template', 'Creates a pole with standard positions', 1),
('POWER_STATION_SITE', 'Power Station Template', 'Creates a power station with standard positions', 2),
('BUILDING_SITE', 'Building Template', 'Creates a building with floor and room nodes', 3),
('WATCH_TOWER_SITE', 'Watch Tower Template', 'Creates a watch tower structure', 4),
('GATE_SITE', 'Gate Template', 'Creates a gate structure', 5),
('STORE_SITE', 'Store Template', 'Creates a store structure', 6)
ON CONFLICT (code) DO NOTHING;

INSERT INTO master.location_template_nodes
(location_template_id, parent_node_id, location_type_id, code, name, node_order, create_positions_from_template, position_template_id, remarks)
SELECT
    lt.id,
    NULL,
    lty.id,
    v.code,
    v.name,
    v.node_order,
    v.create_positions_from_template,
    pt.id,
    v.remarks
FROM (
    VALUES
        ('POLE_SITE', 'POLE', 'POLE', 'Pole', 1, TRUE, 'POLE_STD', 'Standard field pole'),
        ('POWER_STATION_SITE', 'POWER_STATION', 'POWER_STATION', 'Power Station', 1, TRUE, 'POWER_STATION_STD', 'Standard power station'),
        ('BUILDING_SITE', 'BUILDING', 'BUILDING', 'Building', 1, FALSE, NULL, 'Building root'),
        ('WATCH_TOWER_SITE', 'WATCH_TOWER', 'WATCH_TOWER', 'Watch Tower', 1, TRUE, 'WATCH_TOWER_STD', 'Watch tower root'),
        ('GATE_SITE', 'GATE', 'GATE', 'Gate', 1, TRUE, 'GATE_STD', 'Gate root'),
        ('STORE_SITE', 'STORE', 'STORE', 'Store', 1, TRUE, 'STORE_STD', 'Store root')
) AS v(template_code, location_type_code, code, name, node_order, create_positions_from_template, position_template_code, remarks)
JOIN master.location_templates lt ON lt.code = v.template_code
JOIN master.location_types lty ON lty.code = v.location_type_code
LEFT JOIN master.position_templates pt ON pt.code = v.position_template_code
ON CONFLICT (location_template_id, code) DO NOTHING;

INSERT INTO master.location_template_nodes
(location_template_id, parent_node_id, location_type_id, code, name, node_order, create_positions_from_template, position_template_id, remarks)
SELECT
    lt.id,
    parent_node.id,
    lty.id,
    v.code,
    v.name,
    v.node_order,
    FALSE,
    NULL,
    v.remarks
FROM (
    VALUES
        ('BUILDING_SITE', 'BUILDING', 'FLOOR', 'FLOOR-01', 'Floor 1', 1, 'Default floor'),
        ('BUILDING_SITE', 'FLOOR-01', 'ROOM', 'ROOM-01', 'Control Room', 1, 'Default control room')
) AS v(template_code, parent_code, location_type_code, code, name, node_order, remarks)
JOIN master.location_templates lt ON lt.code = v.template_code
JOIN master.location_template_nodes parent_node ON parent_node.location_template_id = lt.id AND parent_node.code = v.parent_code
JOIN master.location_types lty ON lty.code = v.location_type_code
ON CONFLICT (location_template_id, code) DO NOTHING;
