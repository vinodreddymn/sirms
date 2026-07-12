/*
===============================================================================
Project     : SIRMS
Version     : 1.0
Module      : Infrastructure
Description : Creates location hierarchy, project templates, and positions.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS infrastructure.locations
(
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id                  UUID NOT NULL REFERENCES common.projects(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    parent_location_id          UUID REFERENCES infrastructure.locations(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    location_template_node_id   BIGINT REFERENCES master.location_template_nodes(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    location_type_id            BIGINT NOT NULL REFERENCES master.location_types(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    code                        VARCHAR(50) NOT NULL,
    name                        VARCHAR(200) NOT NULL,
    latitude                    NUMERIC(10, 7),
    longitude                   NUMERIC(10, 7),
    elevation_meters            NUMERIC(10, 2),
    geo_json                    JSONB,
    remarks                     TEXT,
    is_active                   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at                  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by                  UUID,
    updated_at                  TIMESTAMP,
    updated_by                  UUID,
    CONSTRAINT uq_locations_project_code UNIQUE(project_id, code),
    CONSTRAINT chk_locations_latitude CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90),
    CONSTRAINT chk_locations_longitude CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180)
);

CREATE TABLE IF NOT EXISTS infrastructure.location_positions
(
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_id                 UUID NOT NULL REFERENCES infrastructure.locations(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    position_template_node_id   BIGINT REFERENCES master.position_template_nodes(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    position_type_id            BIGINT NOT NULL REFERENCES master.position_types(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    position_number             VARCHAR(50) NOT NULL,
    maximum_capacity            INTEGER NOT NULL DEFAULT 1,
    remarks                     TEXT,
    is_active                   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at                  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by                  UUID,
    updated_at                  TIMESTAMP,
    updated_by                  UUID,
    CONSTRAINT uq_location_positions UNIQUE(location_id, position_type_id, position_number),
    CONSTRAINT chk_location_positions_capacity CHECK (maximum_capacity > 0)
);

COMMENT ON TABLE infrastructure.locations IS 'Unlimited hierarchy of locations inside a project.';
COMMENT ON TABLE infrastructure.location_positions IS 'Physical installation positions inside locations.';
