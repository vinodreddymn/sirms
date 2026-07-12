/*
===============================================================================
Project     : SIRMS
Version     : 1.0
Module      : Functions
Description : Creates utility, numbering, and template helper functions.
===============================================================================
*/

CREATE OR REPLACE FUNCTION common.set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION common.next_sequence_value(p_entity_name VARCHAR)
RETURNS VARCHAR
LANGUAGE plpgsql
AS $$
DECLARE
    seq_row common.number_sequences%ROWTYPE;
    next_value BIGINT;
BEGIN
    SELECT *
    INTO seq_row
    FROM common.number_sequences
    WHERE entity_name = p_entity_name
      AND is_active = TRUE
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Number sequence not configured for entity %', p_entity_name;
    END IF;

    next_value := seq_row.current_value + 1;

    UPDATE common.number_sequences
    SET current_value = next_value,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = seq_row.id;

    RETURN seq_row.prefix || LPAD(next_value::TEXT, seq_row.number_length, '0');
END;
$$;

CREATE OR REPLACE FUNCTION common.generate_business_number(p_entity_name VARCHAR)
RETURNS VARCHAR
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN common.next_sequence_value(p_entity_name);
END;
$$;

CREATE OR REPLACE FUNCTION infrastructure.get_location_path(p_location_id UUID)
RETURNS TEXT
LANGUAGE sql
AS $$
WITH RECURSIVE location_path AS
(
    SELECT
        l.id,
        l.parent_location_id,
        l.name,
        1 AS depth
    FROM infrastructure.locations l
    WHERE l.id = p_location_id

    UNION ALL

    SELECT
        parent.id,
        parent.parent_location_id,
        parent.name,
        lp.depth + 1
    FROM infrastructure.locations parent
    JOIN location_path lp ON lp.parent_location_id = parent.id
)
SELECT string_agg(name, ' -> ' ORDER BY depth DESC)
FROM location_path;
$$;

CREATE OR REPLACE FUNCTION asset.get_current_asset_location(p_asset_id UUID)
RETURNS TABLE
(
    location_id UUID,
    location_code VARCHAR(50),
    location_name VARCHAR(200),
    position_id UUID,
    position_number VARCHAR(50)
)
LANGUAGE sql
AS $$
SELECT
    l.id,
    l.code,
    l.name,
    lp.id,
    lp.position_number
FROM asset.asset_installations ai
JOIN infrastructure.location_positions lp ON lp.id = ai.location_position_id
JOIN infrastructure.locations l ON l.id = lp.location_id
WHERE ai.asset_id = p_asset_id
  AND ai.current_flag = TRUE
  AND ai.is_active = TRUE
LIMIT 1;
$$;

CREATE OR REPLACE FUNCTION infrastructure.create_positions_from_template(
    p_location_id UUID,
    p_position_template_id BIGINT,
    p_created_by UUID DEFAULT NULL
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO infrastructure.location_positions
    (
        location_id,
        position_template_node_id,
        position_type_id,
        position_number,
        maximum_capacity,
        created_by
    )
    SELECT
        p_location_id,
        ptn.id,
        ptn.position_type_id,
        ptn.position_number,
        ptn.maximum_capacity,
        p_created_by
    FROM master.position_template_nodes ptn
    WHERE ptn.position_template_id = p_position_template_id
      AND ptn.is_active = TRUE;
END;
$$;

CREATE OR REPLACE FUNCTION infrastructure.create_location_from_template(
    p_project_id UUID,
    p_parent_location_id UUID,
    p_location_template_id BIGINT,
    p_code_prefix VARCHAR(30),
    p_name_prefix VARCHAR(100),
    p_created_by UUID DEFAULT NULL
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    root_node RECORD;
    new_location_id UUID;
BEGIN
    SELECT ltn.*
    INTO root_node
    FROM master.location_template_nodes ltn
    WHERE ltn.location_template_id = p_location_template_id
      AND ltn.parent_node_id IS NULL
      AND ltn.is_active = TRUE
    ORDER BY ltn.node_order
    LIMIT 1;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'No active root node found for location template %', p_location_template_id;
    END IF;

    new_location_id := infrastructure.create_location_node_from_template(
        p_project_id,
        p_parent_location_id,
        root_node.id,
        p_code_prefix,
        p_name_prefix,
        p_created_by
    );

    RETURN new_location_id;
END;
$$;

CREATE OR REPLACE FUNCTION infrastructure.create_location_node_from_template(
    p_project_id UUID,
    p_parent_location_id UUID,
    p_template_node_id BIGINT,
    p_code_prefix VARCHAR(30),
    p_name_prefix VARCHAR(100),
    p_created_by UUID DEFAULT NULL
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    template_node RECORD;
    child_node RECORD;
    new_location_id UUID;
    child_index INTEGER := 0;
BEGIN
    SELECT *
    INTO template_node
    FROM master.location_template_nodes
    WHERE id = p_template_node_id
      AND is_active = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Location template node % not found', p_template_node_id;
    END IF;

    INSERT INTO infrastructure.locations
    (
        project_id,
        parent_location_id,
        location_template_node_id,
        location_type_id,
        code,
        name,
        created_by
    )
    VALUES
    (
        p_project_id,
        p_parent_location_id,
        template_node.id,
        template_node.location_type_id,
        p_code_prefix,
        p_name_prefix,
        p_created_by
    )
    RETURNING id INTO new_location_id;

    IF template_node.create_positions_from_template AND template_node.position_template_id IS NOT NULL THEN
        PERFORM infrastructure.create_positions_from_template(new_location_id, template_node.position_template_id, p_created_by);
    END IF;

    FOR child_node IN
        SELECT *
        FROM master.location_template_nodes
        WHERE parent_node_id = template_node.id
          AND is_active = TRUE
        ORDER BY node_order, id
    LOOP
        child_index := child_index + 1;

        PERFORM infrastructure.create_location_node_from_template(
            p_project_id,
            new_location_id,
            child_node.id,
            p_code_prefix || '-' || LPAD(child_index::TEXT, 2, '0'),
            child_node.name,
            p_created_by
        );
    END LOOP;

    RETURN new_location_id;
END;
$$;

CREATE OR REPLACE FUNCTION infrastructure.validate_installation_capacity(
    p_location_position_id UUID,
    p_exclude_installation_id UUID DEFAULT NULL
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_capacity INTEGER;
    v_used_count INTEGER;
BEGIN
    SELECT maximum_capacity
    INTO v_capacity
    FROM infrastructure.location_positions
    WHERE id = p_location_position_id;

    SELECT COUNT(*)
    INTO v_used_count
    FROM asset.asset_installations
    WHERE location_position_id = p_location_position_id
      AND current_flag = TRUE
      AND is_active = TRUE
      AND (p_exclude_installation_id IS NULL OR id <> p_exclude_installation_id);

    RETURN v_used_count < v_capacity;
END;
$$;

CREATE OR REPLACE FUNCTION asset.validate_specification_value()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    spec_type VARCHAR(20);
BEGIN
    SELECT data_type
    INTO spec_type
    FROM master.specification_definitions
    WHERE id = NEW.specification_definition_id;

    IF spec_type = 'TEXT' AND NEW.value_text IS NULL THEN
        RAISE EXCEPTION 'TEXT specification requires value_text';
    ELSIF spec_type = 'NUMBER' AND NEW.value_number IS NULL THEN
        RAISE EXCEPTION 'NUMBER specification requires value_number';
    ELSIF spec_type = 'BOOLEAN' AND NEW.value_boolean IS NULL THEN
        RAISE EXCEPTION 'BOOLEAN specification requires value_boolean';
    ELSIF spec_type = 'DATE' AND NEW.value_date IS NULL THEN
        RAISE EXCEPTION 'DATE specification requires value_date';
    ELSIF spec_type = 'JSON' AND NEW.value_json IS NULL THEN
        RAISE EXCEPTION 'JSON specification requires value_json';
    END IF;

    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION asset.validate_installation_capacity_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.current_flag AND NOT infrastructure.validate_installation_capacity(NEW.location_position_id, NEW.id) THEN
        RAISE EXCEPTION 'Location position % capacity exceeded', NEW.location_position_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION asset.sync_asset_current_location()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_location_id UUID;
BEGIN
    SELECT lp.location_id
    INTO v_location_id
    FROM infrastructure.location_positions lp
    WHERE lp.id = NEW.location_position_id;

    IF NEW.current_flag THEN
        UPDATE asset.asset_installations
        SET current_flag = FALSE,
            removed_on = COALESCE(removed_on, NEW.installed_on),
            updated_at = CURRENT_TIMESTAMP
        WHERE asset_id = NEW.asset_id
          AND id <> NEW.id
          AND current_flag = TRUE;

        UPDATE asset.assets
        SET current_location_id = v_location_id,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = NEW.asset_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION asset.calculate_next_maintenance_due_date(
    p_schedule_start_date DATE,
    p_frequency_days INTEGER,
    p_last_performed_on TIMESTAMP DEFAULT NULL
)
RETURNS DATE
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_last_performed_on IS NOT NULL THEN
        RETURN p_last_performed_on::DATE + p_frequency_days;
    END IF;

    RETURN p_schedule_start_date + p_frequency_days;
END;
$$;
