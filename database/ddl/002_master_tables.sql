/*
===============================================================================
Project     : SIRMS
Version     : 1.0
Module      : Master
Description : Creates all reference and template master tables.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS master.location_types
(
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(30) NOT NULL UNIQUE,
    name                VARCHAR(100) NOT NULL UNIQUE,
    description         TEXT,
    display_order       INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID,
    updated_at          TIMESTAMP,
    updated_by          UUID,
    CONSTRAINT chk_location_types_display_order CHECK (display_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.location_templates
(
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(30) NOT NULL UNIQUE,
    name                VARCHAR(100) NOT NULL UNIQUE,
    description         TEXT,
    display_order       INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID,
    updated_at          TIMESTAMP,
    updated_by          UUID,
    CONSTRAINT chk_location_templates_display_order CHECK (display_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.location_template_nodes
(
    id                          BIGSERIAL PRIMARY KEY,
    location_template_id        BIGINT NOT NULL REFERENCES master.location_templates(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    parent_node_id              BIGINT REFERENCES master.location_template_nodes(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    location_type_id            BIGINT NOT NULL REFERENCES master.location_types(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    code                        VARCHAR(30) NOT NULL,
    name                        VARCHAR(100) NOT NULL,
    node_order                  INTEGER NOT NULL DEFAULT 0,
    create_positions_from_template BOOLEAN NOT NULL DEFAULT FALSE,
    position_template_id        BIGINT,
    remarks                     TEXT,
    is_active                   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at                  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by                  UUID,
    updated_at                  TIMESTAMP,
    updated_by                  UUID,
    CONSTRAINT uq_location_template_nodes UNIQUE(location_template_id, code),
    CONSTRAINT chk_location_template_nodes_order CHECK (node_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.position_types
(
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(30) NOT NULL UNIQUE,
    name                VARCHAR(100) NOT NULL UNIQUE,
    description         TEXT,
    display_order       INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID,
    updated_at          TIMESTAMP,
    updated_by          UUID,
    CONSTRAINT chk_position_types_display_order CHECK (display_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.position_templates
(
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(30) NOT NULL UNIQUE,
    name                VARCHAR(100) NOT NULL UNIQUE,
    description         TEXT,
    display_order       INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID,
    updated_at          TIMESTAMP,
    updated_by          UUID,
    CONSTRAINT chk_position_templates_display_order CHECK (display_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.position_template_nodes
(
    id                      BIGSERIAL PRIMARY KEY,
    position_template_id    BIGINT NOT NULL REFERENCES master.position_templates(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    position_type_id        BIGINT NOT NULL REFERENCES master.position_types(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    position_number         VARCHAR(50) NOT NULL,
    maximum_capacity        INTEGER NOT NULL DEFAULT 1,
    node_order              INTEGER NOT NULL DEFAULT 0,
    remarks                 TEXT,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID,
    CONSTRAINT uq_position_template_nodes UNIQUE(position_template_id, position_number),
    CONSTRAINT chk_position_template_nodes_capacity CHECK (maximum_capacity > 0),
    CONSTRAINT chk_position_template_nodes_order CHECK (node_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.asset_categories
(
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(30) NOT NULL UNIQUE,
    name                VARCHAR(100) NOT NULL UNIQUE,
    description         TEXT,
    display_order       INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID,
    updated_at          TIMESTAMP,
    updated_by          UUID,
    CONSTRAINT chk_asset_categories_display_order CHECK (display_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.asset_subcategories
(
    id                  BIGSERIAL PRIMARY KEY,
    asset_category_id   BIGINT NOT NULL REFERENCES master.asset_categories(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    code                VARCHAR(30) NOT NULL UNIQUE,
    name                VARCHAR(100) NOT NULL UNIQUE,
    description         TEXT,
    display_order       INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID,
    updated_at          TIMESTAMP,
    updated_by          UUID,
    CONSTRAINT chk_asset_subcategories_display_order CHECK (display_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.manufacturers
(
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(30) NOT NULL UNIQUE,
    name                VARCHAR(120) NOT NULL UNIQUE,
    description         TEXT,
    display_order       INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID,
    updated_at          TIMESTAMP,
    updated_by          UUID,
    CONSTRAINT chk_manufacturers_display_order CHECK (display_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.asset_models
(
    id                      BIGSERIAL PRIMARY KEY,
    manufacturer_id         BIGINT NOT NULL REFERENCES master.manufacturers(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    asset_subcategory_id    BIGINT REFERENCES master.asset_subcategories(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    code                    VARCHAR(50) NOT NULL UNIQUE,
    name                    VARCHAR(150) NOT NULL UNIQUE,
    description             TEXT,
    display_order           INTEGER NOT NULL DEFAULT 0,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID,
    CONSTRAINT chk_asset_models_display_order CHECK (display_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.asset_status
(
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(30) NOT NULL UNIQUE,
    name                VARCHAR(100) NOT NULL UNIQUE,
    description         TEXT,
    display_order       INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID,
    updated_at          TIMESTAMP,
    updated_by          UUID,
    CONSTRAINT chk_asset_status_display_order CHECK (display_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.asset_condition
(
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(30) NOT NULL UNIQUE,
    name                VARCHAR(100) NOT NULL UNIQUE,
    description         TEXT,
    display_order       INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID,
    updated_at          TIMESTAMP,
    updated_by          UUID,
    CONSTRAINT chk_asset_condition_display_order CHECK (display_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.asset_lifecycle
(
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(30) NOT NULL UNIQUE,
    name                VARCHAR(100) NOT NULL UNIQUE,
    description         TEXT,
    display_order       INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID,
    updated_at          TIMESTAMP,
    updated_by          UUID,
    CONSTRAINT chk_asset_lifecycle_display_order CHECK (display_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.maintenance_types
(
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(30) NOT NULL UNIQUE,
    name                VARCHAR(100) NOT NULL UNIQUE,
    description         TEXT,
    display_order       INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID,
    updated_at          TIMESTAMP,
    updated_by          UUID,
    CONSTRAINT chk_maintenance_types_display_order CHECK (display_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.failure_categories
(
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(30) NOT NULL UNIQUE,
    name                VARCHAR(100) NOT NULL UNIQUE,
    description         TEXT,
    display_order       INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID,
    updated_at          TIMESTAMP,
    updated_by          UUID,
    CONSTRAINT chk_failure_categories_display_order CHECK (display_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.root_cause_categories
(
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(30) NOT NULL UNIQUE,
    name                VARCHAR(100) NOT NULL UNIQUE,
    description         TEXT,
    display_order       INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID,
    updated_at          TIMESTAMP,
    updated_by          UUID,
    CONSTRAINT chk_root_cause_categories_display_order CHECK (display_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.incident_status
(
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(30) NOT NULL UNIQUE,
    name                VARCHAR(100) NOT NULL UNIQUE,
    description         TEXT,
    display_order       INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID,
    updated_at          TIMESTAMP,
    updated_by          UUID,
    CONSTRAINT chk_incident_status_display_order CHECK (display_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.incident_priority
(
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(30) NOT NULL UNIQUE,
    name                VARCHAR(100) NOT NULL UNIQUE,
    description         TEXT,
    display_order       INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID,
    updated_at          TIMESTAMP,
    updated_by          UUID,
    CONSTRAINT chk_incident_priority_display_order CHECK (display_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.incident_categories
(
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(30) NOT NULL UNIQUE,
    name                VARCHAR(100) NOT NULL UNIQUE,
    description         TEXT,
    display_order       INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID,
    updated_at          TIMESTAMP,
    updated_by          UUID,
    CONSTRAINT chk_incident_categories_display_order CHECK (display_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.work_order_status
(
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(30) NOT NULL UNIQUE,
    name                VARCHAR(100) NOT NULL UNIQUE,
    description         TEXT,
    display_order       INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID,
    updated_at          TIMESTAMP,
    updated_by          UUID,
    CONSTRAINT chk_work_order_status_display_order CHECK (display_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.relationship_types
(
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(30) NOT NULL UNIQUE,
    name                VARCHAR(100) NOT NULL UNIQUE,
    description         TEXT,
    display_order       INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID,
    updated_at          TIMESTAMP,
    updated_by          UUID,
    CONSTRAINT chk_relationship_types_display_order CHECK (display_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.document_types
(
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(30) NOT NULL UNIQUE,
    name                VARCHAR(100) NOT NULL UNIQUE,
    description         TEXT,
    display_order       INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID,
    updated_at          TIMESTAMP,
    updated_by          UUID,
    CONSTRAINT chk_document_types_display_order CHECK (display_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.photo_types
(
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(30) NOT NULL UNIQUE,
    name                VARCHAR(100) NOT NULL UNIQUE,
    description         TEXT,
    display_order       INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID,
    updated_at          TIMESTAMP,
    updated_by          UUID,
    CONSTRAINT chk_photo_types_display_order CHECK (display_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.project_types
(
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(30) NOT NULL UNIQUE,
    name                VARCHAR(100) NOT NULL UNIQUE,
    description         TEXT,
    display_order       INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID,
    updated_at          TIMESTAMP,
    updated_by          UUID,
    CONSTRAINT chk_project_types_display_order CHECK (display_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.user_role_templates
(
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(30) NOT NULL UNIQUE,
    name                VARCHAR(100) NOT NULL UNIQUE,
    description         TEXT,
    display_order       INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID,
    updated_at          TIMESTAMP,
    updated_by          UUID,
    CONSTRAINT chk_user_role_templates_display_order CHECK (display_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.specification_definitions
(
    id                      BIGSERIAL PRIMARY KEY,
    asset_category_id       BIGINT REFERENCES master.asset_categories(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    asset_subcategory_id    BIGINT REFERENCES master.asset_subcategories(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    code                    VARCHAR(50) NOT NULL UNIQUE,
    name                    VARCHAR(100) NOT NULL,
    data_type               VARCHAR(20) NOT NULL,
    unit_of_measure         VARCHAR(30),
    required_flag           BOOLEAN NOT NULL DEFAULT FALSE,
    display_order           INTEGER NOT NULL DEFAULT 0,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID,
    updated_at              TIMESTAMP,
    updated_by              UUID,
    CONSTRAINT chk_specification_definitions_data_type CHECK (data_type IN ('TEXT', 'NUMBER', 'BOOLEAN', 'DATE', 'JSON')),
    CONSTRAINT chk_specification_definitions_display_order CHECK (display_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.movement_types
(
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(30) NOT NULL UNIQUE,
    name                VARCHAR(100) NOT NULL UNIQUE,
    description         TEXT,
    display_order       INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID,
    updated_at          TIMESTAMP,
    updated_by          UUID,
    CONSTRAINT chk_movement_types_display_order CHECK (display_order >= 0)
);

CREATE TABLE IF NOT EXISTS master.stock_transaction_types
(
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(30) NOT NULL UNIQUE,
    name                VARCHAR(100) NOT NULL UNIQUE,
    quantity_effect     SMALLINT NOT NULL,
    description         TEXT,
    display_order       INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID,
    updated_at          TIMESTAMP,
    updated_by          UUID,
    CONSTRAINT chk_stock_transaction_types_effect CHECK (quantity_effect IN (-1, 1)),
    CONSTRAINT chk_stock_transaction_types_display_order CHECK (display_order >= 0)
);

ALTER TABLE master.location_template_nodes
    ADD CONSTRAINT fk_location_template_nodes_position_template
    FOREIGN KEY (position_template_id) REFERENCES master.position_templates(id) ON UPDATE RESTRICT ON DELETE SET NULL;

COMMENT ON TABLE master.location_types IS 'Lookup values for location hierarchy node types.';
COMMENT ON TABLE master.location_templates IS 'Reusable templates for automatic location creation.';
COMMENT ON TABLE master.location_template_nodes IS 'Template nodes under a location template.';
COMMENT ON TABLE master.position_types IS 'Lookup values for physical installation positions.';
COMMENT ON TABLE master.position_templates IS 'Reusable templates for automatic position creation.';
COMMENT ON TABLE master.position_template_nodes IS 'Position nodes defined under a position template.';
COMMENT ON TABLE master.asset_categories IS 'Top-level asset categories.';
COMMENT ON TABLE master.asset_subcategories IS 'Subcategories under each asset category.';
COMMENT ON TABLE master.manufacturers IS 'Manufacturers or brands for asset models.';
COMMENT ON TABLE master.asset_models IS 'Catalog of manufacturer models.';
COMMENT ON TABLE master.asset_status IS 'Operational status of an asset.';
COMMENT ON TABLE master.asset_condition IS 'Physical condition of an asset.';
COMMENT ON TABLE master.asset_lifecycle IS 'Lifecycle stage of an asset.';
COMMENT ON TABLE master.maintenance_types IS 'Maintenance modes such as preventive and corrective.';
COMMENT ON TABLE master.failure_categories IS 'Failure classes for maintenance and incident analysis.';
COMMENT ON TABLE master.root_cause_categories IS 'Root cause classes for investigation.';
COMMENT ON TABLE master.incident_status IS 'Lifecycle status for incidents.';
COMMENT ON TABLE master.incident_priority IS 'Priority values for incidents.';
COMMENT ON TABLE master.incident_categories IS 'Categories for classifying incidents.';
COMMENT ON TABLE master.work_order_status IS 'Lifecycle status for work orders.';
COMMENT ON TABLE master.relationship_types IS 'Supported asset-to-asset relationship types.';
COMMENT ON TABLE master.document_types IS 'Document classification values.';
COMMENT ON TABLE master.photo_types IS 'Photo classification values.';
COMMENT ON TABLE master.project_types IS 'Project type values.';
COMMENT ON TABLE master.user_role_templates IS 'Role templates used to bootstrap runtime roles.';
COMMENT ON TABLE master.specification_definitions IS 'Configurable asset specification definitions.';
COMMENT ON TABLE master.movement_types IS 'Movement types for asset movement history.';
COMMENT ON TABLE master.stock_transaction_types IS 'Stock transaction types and their quantity effect.';
