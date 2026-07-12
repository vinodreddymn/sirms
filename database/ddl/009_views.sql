/*
===============================================================================
Project     : SIRMS
Version     : 1.0
Module      : Views
Description : Creates convenience reporting and lookup views.
===============================================================================
*/

CREATE OR REPLACE VIEW infrastructure.vw_location_hierarchy AS
SELECT
    l.id,
    l.project_id,
    p.project_code,
    l.parent_location_id,
    l.code,
    l.name,
    lt.code AS location_type_code,
    lt.name AS location_type_name,
    l.latitude,
    l.longitude,
    l.elevation_meters,
    l.is_active
FROM infrastructure.locations l
JOIN common.projects p ON p.id = l.project_id
JOIN master.location_types lt ON lt.id = l.location_type_id;

CREATE OR REPLACE VIEW asset.vw_asset_register AS
SELECT
    a.id AS asset_id,
    a.project_id,
    p.project_code,
    a.asset_number,
    ac.code AS asset_category_code,
    ac.name AS asset_category_name,
    ascg.code AS asset_subcategory_code,
    ascg.name AS asset_subcategory_name,
    m.name AS manufacturer_name,
    am.name AS model_name,
    ast.code AS asset_status_code,
    ast.name AS asset_status_name,
    acond.code AS asset_condition_code,
    acond.name AS asset_condition_name,
    al.code AS asset_lifecycle_code,
    al.name AS asset_lifecycle_name,
    a.serial_number,
    a.barcode,
    a.qr_code,
    a.purchase_date,
    a.warranty_expiry,
    a.current_location_id,
    a.is_active
FROM asset.assets a
JOIN common.projects p ON p.id = a.project_id
JOIN master.asset_categories ac ON ac.id = a.asset_category_id
LEFT JOIN master.asset_subcategories ascg ON ascg.id = a.asset_subcategory_id
LEFT JOIN master.manufacturers m ON m.id = a.manufacturer_id
LEFT JOIN master.asset_models am ON am.id = a.asset_model_id
JOIN master.asset_status ast ON ast.id = a.asset_status_id
LEFT JOIN master.asset_condition acond ON acond.id = a.asset_condition_id
LEFT JOIN master.asset_lifecycle al ON al.id = a.asset_lifecycle_id;

CREATE OR REPLACE VIEW asset.vw_asset_current_location AS
SELECT
    ai.asset_id,
    a.asset_number,
    lp.id AS location_position_id,
    lp.position_number,
    pt.code AS position_type_code,
    pt.name AS position_type_name,
    l.id AS location_id,
    l.code AS location_code,
    l.name AS location_name,
    ai.installed_on,
    ai.remarks
FROM asset.asset_installations ai
JOIN asset.assets a ON a.id = ai.asset_id
JOIN infrastructure.location_positions lp ON lp.id = ai.location_position_id
JOIN master.position_types pt ON pt.id = lp.position_type_id
JOIN infrastructure.locations l ON l.id = lp.location_id
WHERE ai.current_flag = TRUE
  AND ai.is_active = TRUE;

CREATE OR REPLACE VIEW asset.vw_asset_history AS
SELECT
    a.id AS asset_id,
    a.asset_number,
    'INSTALLATION'::VARCHAR(20) AS history_type,
    ai.installed_on::TIMESTAMP AS event_at,
    NULL::VARCHAR(30) AS reference_code,
    l.code AS location_code,
    l.name AS location_name,
    ai.remarks
FROM asset.assets a
JOIN asset.asset_installations ai ON ai.asset_id = a.id
JOIN infrastructure.location_positions lp ON lp.id = ai.location_position_id
JOIN infrastructure.locations l ON l.id = lp.location_id
UNION ALL
SELECT
    a.id AS asset_id,
    a.asset_number,
    'MOVEMENT'::VARCHAR(20) AS history_type,
    amv.movement_date AS event_at,
    mt.code AS reference_code,
    COALESCE(tl.code, fl.code) AS location_code,
    COALESCE(tl.name, fl.name) AS location_name,
    amv.remarks
FROM asset.assets a
JOIN asset.asset_movements amv ON amv.asset_id = a.id
JOIN master.movement_types mt ON mt.id = amv.movement_type_id
LEFT JOIN infrastructure.locations fl ON fl.id = amv.from_location_id
LEFT JOIN infrastructure.locations tl ON tl.id = amv.to_location_id;

CREATE OR REPLACE VIEW incident.vw_incident_summary AS
SELECT
    i.id AS incident_id,
    i.project_id,
    p.project_code,
    i.incident_number,
    ic.name AS incident_category_name,
    i.reported_date,
    i.asset_id,
    a.asset_number,
    i.location_id,
    l.code AS location_code,
    l.name AS location_name,
    ip.name AS priority_name,
    ist.name AS status_name,
    i.assigned_to,
    i.closed_date,
    i.description
FROM incident.incidents i
JOIN common.projects p ON p.id = i.project_id
LEFT JOIN master.incident_categories ic ON ic.id = i.incident_category_id
LEFT JOIN asset.assets a ON a.id = i.asset_id
LEFT JOIN infrastructure.locations l ON l.id = i.location_id
JOIN master.incident_priority ip ON ip.id = i.incident_priority_id
JOIN master.incident_status ist ON ist.id = i.incident_status_id;

CREATE OR REPLACE VIEW incident.vw_open_work_orders AS
SELECT
    wo.id AS work_order_id,
    wo.work_order_number,
    wo.incident_id,
    i.incident_number,
    wos.name AS work_order_status_name,
    wo.assigned_to,
    wo.vendor_id,
    wo.planned_start,
    wo.actual_start,
    wo.actual_finish
FROM incident.work_orders wo
JOIN incident.incidents i ON i.id = wo.incident_id
JOIN master.work_order_status wos ON wos.id = wo.work_order_status_id
WHERE wos.code <> 'COMPLETED'
  AND wos.code <> 'CANCELLED'
  AND wo.is_active = TRUE;

CREATE OR REPLACE VIEW asset.vw_maintenance_due AS
SELECT
    ms.id AS maintenance_schedule_id,
    ms.asset_id,
    a.asset_number,
    mt.name AS maintenance_type_name,
    ms.next_due_date,
    ms.assigned_to,
    ms.vendor_id,
    (ms.next_due_date - CURRENT_DATE) AS days_until_due
FROM asset.maintenance_schedules ms
JOIN asset.assets a ON a.id = ms.asset_id
JOIN master.maintenance_types mt ON mt.id = ms.maintenance_type_id
WHERE ms.is_active = TRUE;

CREATE OR REPLACE VIEW common.vw_dashboard_summary AS
SELECT
    p.id AS project_id,
    p.project_code,
    COUNT(DISTINCT a.id) AS total_assets,
    COUNT(DISTINCT i.id) FILTER (WHERE i.closed_date IS NULL) AS open_incidents,
    COUNT(DISTINCT wo.id) FILTER (WHERE wos.code NOT IN ('COMPLETED', 'CANCELLED')) AS open_work_orders,
    COUNT(DISTINCT ms.id) FILTER (WHERE ms.next_due_date <= CURRENT_DATE + INTERVAL '7 days') AS maintenance_due_next_7_days
FROM common.projects p
LEFT JOIN asset.assets a ON a.project_id = p.id AND a.is_active = TRUE
LEFT JOIN incident.incidents i ON i.project_id = p.id AND i.is_active = TRUE
LEFT JOIN incident.work_orders wo ON wo.incident_id = i.id AND wo.is_active = TRUE
LEFT JOIN master.work_order_status wos ON wos.id = wo.work_order_status_id
LEFT JOIN asset.maintenance_schedules ms ON ms.asset_id = a.id AND ms.is_active = TRUE
GROUP BY p.id, p.project_code;
