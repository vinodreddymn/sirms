/*
===============================================================================
Project     : SIRMS
Version     : 1.0
Module      : Validation
Description : Verifies schemas, objects, views, functions, triggers, and sample
              data behavior for the frozen Version 1.0 database.
Execution   : Run after all DDL and seed scripts complete.
===============================================================================
*/

DO $$
DECLARE
    expected_schema TEXT;
    expected_table TEXT;
    expected_view TEXT;
    expected_function TEXT;
    v_template_location_id UUID;
    v_template_position_count INTEGER;
BEGIN
    FOREACH expected_schema IN ARRAY ARRAY['common', 'master', 'security', 'infrastructure', 'asset', 'incident']
    LOOP
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.schemata
            WHERE schema_name = expected_schema
        ) THEN
            RAISE EXCEPTION 'Missing schema: %', expected_schema;
        END IF;
    END LOOP;

    FOREACH expected_table IN ARRAY ARRAY[
        'common.customers','common.projects','common.vendors','common.attachments','common.audit_logs','common.activity_logs',
        'common.notifications','common.system_settings','common.dashboard_preferences','common.saved_searches','common.saved_filters',
        'common.report_definitions','common.saved_reports','common.qr_generation_history','common.qr_print_history',
        'common.barcode_history','common.import_jobs','common.import_errors','common.export_history','common.comments',
        'common.tags','common.entity_tags','common.favorite_assets','common.watch_list','common.notification_preferences',
        'common.number_sequences',
        'master.location_types','master.location_templates','master.location_template_nodes','master.position_types',
        'master.position_templates','master.position_template_nodes','master.asset_categories','master.asset_subcategories',
        'master.manufacturers','master.asset_models','master.asset_status','master.asset_condition','master.asset_lifecycle',
        'master.maintenance_types','master.failure_categories','master.root_cause_categories','master.incident_status',
        'master.incident_priority','master.incident_categories','master.work_order_status','master.relationship_types',
        'master.document_types','master.photo_types','master.project_types','master.user_role_templates',
        'master.specification_definitions','master.movement_types','master.stock_transaction_types',
        'security.users','security.roles','security.permissions','security.role_permissions','security.user_roles',
        'security.login_history','security.password_reset_tokens','security.refresh_tokens','security.api_tokens',
        'infrastructure.locations','infrastructure.location_positions',
        'asset.assets','asset.asset_specifications','asset.asset_installations','asset.asset_movements','asset.stock_transactions',
        'asset.asset_documents','asset.asset_photos','asset.asset_relationships','asset.maintenance_checklists',
        'asset.checklist_items','asset.maintenance_schedules','asset.maintenance_history',
        'incident.incidents','incident.incident_updates','incident.work_orders','incident.work_order_tasks',
        'incident.incident_attachments'
    ]
    LOOP
        IF to_regclass(expected_table) IS NULL THEN
            RAISE EXCEPTION 'Missing table: %', expected_table;
        END IF;
    END LOOP;

    FOREACH expected_view IN ARRAY ARRAY[
        'infrastructure.vw_location_hierarchy',
        'asset.vw_asset_register',
        'asset.vw_asset_current_location',
        'asset.vw_asset_history',
        'incident.vw_incident_summary',
        'incident.vw_open_work_orders',
        'asset.vw_maintenance_due',
        'common.vw_dashboard_summary'
    ]
    LOOP
        IF to_regclass(expected_view) IS NULL THEN
            RAISE EXCEPTION 'Missing view: %', expected_view;
        END IF;
    END LOOP;

    FOREACH expected_function IN ARRAY ARRAY[
        'common.next_sequence_value',
        'common.generate_business_number',
        'infrastructure.get_location_path',
        'asset.get_current_asset_location',
        'infrastructure.create_positions_from_template',
        'infrastructure.create_location_from_template',
        'infrastructure.validate_installation_capacity',
        'asset.calculate_next_maintenance_due_date'
    ]
    LOOP
        IF NOT EXISTS (
            SELECT 1
            FROM pg_proc p
            JOIN pg_namespace n ON n.oid = p.pronamespace
            WHERE n.nspname || '.' || p.proname = expected_function
        ) THEN
            RAISE EXCEPTION 'Missing function: %', expected_function;
        END IF;
    END LOOP;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_trigger
        WHERE tgname = 'trg_asset_installations_sync_location'
    ) THEN
        RAISE EXCEPTION 'Missing trigger trg_asset_installations_sync_location';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM asset.assets
        WHERE asset_number = 'CAM000001'
    ) THEN
        RAISE EXCEPTION 'Sample asset CAM000001 missing';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM incident.incidents
        WHERE incident_number = 'INC000153'
    ) THEN
        RAISE EXCEPTION 'Sample incident INC000153 missing';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM incident.work_orders
        WHERE work_order_number = 'WO000075'
    ) THEN
        RAISE EXCEPTION 'Sample work order WO000075 missing';
    END IF;

    IF infrastructure.get_location_path('66666666-6666-6666-6666-666666666664'::UUID) IS NULL THEN
        RAISE EXCEPTION 'Location path function returned NULL for sample location';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM asset.get_current_asset_location('88888888-8888-8888-8888-888888888881'::UUID)
    ) THEN
        RAISE EXCEPTION 'Current asset location function returned no row';
    END IF;

    IF common.generate_business_number('INCIDENT') IS NULL THEN
        RAISE EXCEPTION 'Business number generation returned NULL';
    END IF;

    SELECT infrastructure.create_location_from_template(
        '22222222-2222-2222-2222-222222222222'::UUID,
        '66666666-6666-6666-6666-666666666661'::UUID,
        lt.id,
        'VAL-POLE',
        'Validation Pole',
        '33333333-3333-3333-3333-333333333331'::UUID
    )
    INTO v_template_location_id
    FROM master.location_templates lt
    WHERE lt.code = 'POLE_SITE';

    SELECT COUNT(*)
    INTO v_template_position_count
    FROM infrastructure.location_positions
    WHERE location_id = v_template_location_id;

    IF v_template_position_count = 0 THEN
        RAISE EXCEPTION 'Template creation did not create positions';
    END IF;

    DELETE FROM infrastructure.locations
    WHERE id = v_template_location_id;
END;
$$;
