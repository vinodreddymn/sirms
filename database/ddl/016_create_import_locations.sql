/*
===============================================================================
Project     : SIRMS
Version     : 1.0
Module      : Infrastructure
Description : Stored procedure to parse and dynamically insert hierarchical location data.
===============================================================================
*/

CREATE OR REPLACE PROCEDURE infrastructure.import_locations()
LANGUAGE plpgsql
AS $$
DECLARE
    r RECORD;
    v_parent_id UUID;
    v_project_id UUID;
    v_location_type_id BIGINT;
    v_existing_id UUID;
    v_seed_count INT;
    v_processed_count INT := 0;
    v_missing_parent VARCHAR(50);
BEGIN
    -- 1. Upfront validation: Check for parent codes that do not exist in master.location_seed AND do not exist in infrastructure.locations
    SELECT s.parent_code INTO v_missing_parent
    FROM master.location_seed s
    WHERE s.parent_code IS NOT NULL
      AND s.parent_code NOT IN (SELECT code FROM master.location_seed WHERE code IS NOT NULL)
      AND s.parent_code NOT IN (SELECT code FROM infrastructure.locations)
    LIMIT 1;

    IF v_missing_parent IS NOT NULL THEN
        RAISE EXCEPTION 'Import aborted: Parent location with code % does not exist in seed table or database.', v_missing_parent;
    END IF;

    -- Get total count to detect cycles/orphans
    SELECT COUNT(*) INTO v_seed_count FROM master.location_seed;

    -- 2. Process hierarchy using recursive CTE to guarantee parent-first order
    FOR r IN (
        WITH RECURSIVE location_hierarchy AS (
            -- Anchor member: root locations or locations whose parent is already in the database
            SELECT 
                s.parent_code,
                s.location_type_code,
                s.code,
                s.name,
                s.remarks,
                s.display_order,
                0 AS depth,
                COALESCE(
                    (SELECT p.id FROM common.projects p WHERE p.project_code = s.code),
                    (SELECT l.project_id FROM infrastructure.locations l WHERE l.code = s.parent_code LIMIT 1)
                ) AS project_id
            FROM master.location_seed s
            WHERE s.parent_code IS NULL 
               OR (
                   s.parent_code NOT IN (SELECT code FROM master.location_seed WHERE code IS NOT NULL)
                   AND s.parent_code IN (SELECT code FROM infrastructure.locations)
               )
            
            UNION ALL
            
            -- Recursive member: child locations
            SELECT 
                s.parent_code,
                s.location_type_code,
                s.code,
                s.name,
                s.remarks,
                s.display_order,
                h.depth + 1 AS depth,
                h.project_id
            FROM master.location_seed s
            JOIN location_hierarchy h ON s.parent_code = h.code
        )
        SELECT * FROM location_hierarchy ORDER BY depth ASC
    ) LOOP
        v_processed_count := v_processed_count + 1;

        -- Resolve location_type_id using location_type_code
        SELECT id INTO v_location_type_id
        FROM master.location_types
        WHERE code = r.location_type_code;

        IF v_location_type_id IS NULL THEN
            RAISE EXCEPTION 'Import aborted: Location type code % not found in master.location_types.', r.location_type_code;
        END IF;

        -- Resolve project_id
        IF r.project_id IS NULL THEN
            RAISE EXCEPTION 'Import aborted: Could not resolve project_id for location code %.', r.code;
        END IF;

        -- Resolve parent_location_id using parent_code and project_id to ensure correct scoping
        IF r.parent_code IS NULL THEN
            v_parent_id := NULL;
        ELSE
            SELECT id INTO v_parent_id
            FROM infrastructure.locations
            WHERE project_id = r.project_id AND code = r.parent_code;

            IF v_parent_id IS NULL THEN
                RAISE EXCEPTION 'Import aborted: Parent location with code % under project_id % not found in database.', r.parent_code, r.project_id;
            END IF;
        END IF;

        -- Check whether (project_id, code) already exists (idempotency check)
        SELECT id INTO v_existing_id
        FROM infrastructure.locations
        WHERE project_id = r.project_id AND code = r.code;

        -- Insert only if missing
        IF v_existing_id IS NULL THEN
            INSERT INTO infrastructure.locations (
                project_id,
                parent_location_id,
                location_type_id,
                code,
                name,
                remarks
            ) VALUES (
                r.project_id,
                v_parent_id,
                v_location_type_id,
                r.code,
                r.name,
                r.remarks
            );
        END IF;
    END LOOP;

    -- Verify all records were processed (detects cyclic dependencies)
    IF v_processed_count < v_seed_count THEN
        RAISE EXCEPTION 'Import aborted: Cyclic dependency or disconnected tree detected in master.location_seed. Processed % of % rows.', v_processed_count, v_seed_count;
    END IF;
END;
$$;
