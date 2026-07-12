/*
===============================================================================
Project     : SIRMS
Version     : 1.0
Module      : Asset
Description : Creates asset register, specs, movement, stock, and maintenance.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS asset.assets
(
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id                  UUID NOT NULL REFERENCES common.projects(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    asset_number                VARCHAR(50) NOT NULL UNIQUE,
    asset_category_id           BIGINT NOT NULL REFERENCES master.asset_categories(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    asset_subcategory_id        BIGINT REFERENCES master.asset_subcategories(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    manufacturer_id             BIGINT REFERENCES master.manufacturers(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    asset_model_id              BIGINT REFERENCES master.asset_models(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    asset_status_id             BIGINT NOT NULL REFERENCES master.asset_status(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    asset_condition_id          BIGINT REFERENCES master.asset_condition(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    asset_lifecycle_id          BIGINT REFERENCES master.asset_lifecycle(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    serial_number               VARCHAR(100),
    barcode                     VARCHAR(100),
    qr_code                     VARCHAR(100),
    purchase_date               DATE,
    warranty_expiry             DATE,
    current_location_id         UUID REFERENCES infrastructure.locations(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    remarks                     TEXT,
    is_active                   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at                  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by                  UUID,
    updated_at                  TIMESTAMP,
    updated_by                  UUID,
    CONSTRAINT uq_assets_serial_number UNIQUE(serial_number),
    CONSTRAINT uq_assets_barcode UNIQUE(barcode),
    CONSTRAINT uq_assets_qr_code UNIQUE(qr_code),
    CONSTRAINT chk_assets_warranty CHECK (warranty_expiry IS NULL OR purchase_date IS NULL OR warranty_expiry >= purchase_date)
);

CREATE TABLE IF NOT EXISTS asset.asset_specifications
(
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id                    UUID NOT NULL REFERENCES asset.assets(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    specification_definition_id BIGINT NOT NULL REFERENCES master.specification_definitions(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    value_text                  TEXT,
    value_number                NUMERIC(18, 4),
    value_boolean               BOOLEAN,
    value_date                  DATE,
    value_json                  JSONB,
    is_active                   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at                  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by                  UUID,
    updated_at                  TIMESTAMP,
    updated_by                  UUID,
    CONSTRAINT uq_asset_specifications UNIQUE(asset_id, specification_definition_id)
);

CREATE TABLE IF NOT EXISTS asset.asset_installations
(
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id                    UUID NOT NULL REFERENCES asset.assets(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    location_position_id        UUID NOT NULL REFERENCES infrastructure.location_positions(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    installed_on                DATE NOT NULL,
    removed_on                  DATE,
    current_flag                BOOLEAN NOT NULL DEFAULT TRUE,
    installed_by                UUID REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    removed_by                  UUID REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    remarks                     TEXT,
    is_active                   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at                  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by                  UUID,
    updated_at                  TIMESTAMP,
    updated_by                  UUID,
    CONSTRAINT chk_asset_installations_dates CHECK (removed_on IS NULL OR removed_on >= installed_on)
);

CREATE TABLE IF NOT EXISTS asset.asset_movements
(
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id                    UUID NOT NULL REFERENCES asset.assets(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    movement_type_id            BIGINT NOT NULL REFERENCES master.movement_types(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    from_location_id            UUID REFERENCES infrastructure.locations(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    to_location_id              UUID REFERENCES infrastructure.locations(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    vendor_id                   UUID REFERENCES common.vendors(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    movement_date               TIMESTAMP NOT NULL,
    reference_document          VARCHAR(100),
    remarks                     TEXT,
    is_active                   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at                  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by                  UUID,
    updated_at                  TIMESTAMP,
    updated_by                  UUID,
    CONSTRAINT chk_asset_movements_locations CHECK (from_location_id IS NOT NULL OR to_location_id IS NOT NULL OR vendor_id IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS asset.stock_transactions
(
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id                  UUID NOT NULL REFERENCES common.projects(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    asset_id                    UUID REFERENCES asset.assets(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    stock_transaction_type_id   BIGINT NOT NULL REFERENCES master.stock_transaction_types(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    location_id                 UUID REFERENCES infrastructure.locations(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    vendor_id                   UUID REFERENCES common.vendors(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    quantity                    INTEGER NOT NULL DEFAULT 1,
    transaction_date            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reference_number            VARCHAR(100),
    remarks                     TEXT,
    is_active                   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at                  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by                  UUID,
    updated_at                  TIMESTAMP,
    updated_by                  UUID,
    CONSTRAINT chk_stock_transactions_quantity CHECK (quantity > 0)
);

CREATE TABLE IF NOT EXISTS asset.asset_documents
(
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id                    UUID NOT NULL REFERENCES asset.assets(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    document_type_id            BIGINT NOT NULL REFERENCES master.document_types(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    attachment_id               UUID REFERENCES common.attachments(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    document_title              VARCHAR(150) NOT NULL,
    document_number             VARCHAR(100),
    issue_date                  DATE,
    expiry_date                 DATE,
    remarks                     TEXT,
    is_active                   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at                  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by                  UUID,
    updated_at                  TIMESTAMP,
    updated_by                  UUID,
    CONSTRAINT chk_asset_documents_dates CHECK (expiry_date IS NULL OR issue_date IS NULL OR expiry_date >= issue_date)
);

CREATE TABLE IF NOT EXISTS asset.asset_photos
(
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id                    UUID NOT NULL REFERENCES asset.assets(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    photo_type_id               BIGINT NOT NULL REFERENCES master.photo_types(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    attachment_id               UUID REFERENCES common.attachments(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    caption                     VARCHAR(255),
    taken_at                    TIMESTAMP,
    remarks                     TEXT,
    is_active                   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at                  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by                  UUID,
    updated_at                  TIMESTAMP,
    updated_by                  UUID
);

CREATE TABLE IF NOT EXISTS asset.asset_relationships
(
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id                    UUID NOT NULL REFERENCES asset.assets(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    related_asset_id            UUID NOT NULL REFERENCES asset.assets(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    relationship_type_id        BIGINT NOT NULL REFERENCES master.relationship_types(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    remarks                     TEXT,
    is_active                   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at                  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by                  UUID,
    updated_at                  TIMESTAMP,
    updated_by                  UUID,
    CONSTRAINT uq_asset_relationships UNIQUE(asset_id, related_asset_id, relationship_type_id),
    CONSTRAINT chk_asset_relationships_self CHECK (asset_id <> related_asset_id)
);

CREATE TABLE IF NOT EXISTS asset.maintenance_checklists
(
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_subcategory_id        BIGINT REFERENCES master.asset_subcategories(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    maintenance_type_id         BIGINT NOT NULL REFERENCES master.maintenance_types(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    checklist_code              VARCHAR(50) NOT NULL UNIQUE,
    checklist_name              VARCHAR(150) NOT NULL,
    remarks                     TEXT,
    is_active                   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at                  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by                  UUID,
    updated_at                  TIMESTAMP,
    updated_by                  UUID
);

CREATE TABLE IF NOT EXISTS asset.checklist_items
(
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    checklist_id                UUID NOT NULL REFERENCES asset.maintenance_checklists(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    item_sequence               INTEGER NOT NULL,
    item_description            VARCHAR(255) NOT NULL,
    is_mandatory                BOOLEAN NOT NULL DEFAULT TRUE,
    remarks                     TEXT,
    is_active                   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at                  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by                  UUID,
    updated_at                  TIMESTAMP,
    updated_by                  UUID,
    CONSTRAINT uq_checklist_items UNIQUE(checklist_id, item_sequence),
    CONSTRAINT chk_checklist_items_sequence CHECK (item_sequence > 0)
);

CREATE TABLE IF NOT EXISTS asset.maintenance_schedules
(
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id                    UUID NOT NULL REFERENCES asset.assets(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    maintenance_type_id         BIGINT NOT NULL REFERENCES master.maintenance_types(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    checklist_id                UUID REFERENCES asset.maintenance_checklists(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    schedule_start_date         DATE NOT NULL,
    frequency_days              INTEGER NOT NULL,
    next_due_date               DATE NOT NULL,
    assigned_to                 UUID REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    vendor_id                   UUID REFERENCES common.vendors(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    remarks                     TEXT,
    is_active                   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at                  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by                  UUID,
    updated_at                  TIMESTAMP,
    updated_by                  UUID,
    CONSTRAINT chk_maintenance_schedules_frequency CHECK (frequency_days > 0)
);

CREATE TABLE IF NOT EXISTS asset.maintenance_history
(
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id                    UUID NOT NULL REFERENCES asset.assets(id) ON UPDATE RESTRICT ON DELETE CASCADE,
    maintenance_schedule_id     UUID REFERENCES asset.maintenance_schedules(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    maintenance_type_id         BIGINT NOT NULL REFERENCES master.maintenance_types(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    performed_on                TIMESTAMP NOT NULL,
    performed_by                UUID REFERENCES security.users(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    vendor_id                   UUID REFERENCES common.vendors(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    checklist_id                UUID REFERENCES asset.maintenance_checklists(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    completion_notes            TEXT,
    failure_category_id         BIGINT REFERENCES master.failure_categories(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    root_cause_category_id      BIGINT REFERENCES master.root_cause_categories(id) ON UPDATE RESTRICT ON DELETE SET NULL,
    is_active                   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at                  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by                  UUID,
    updated_at                  TIMESTAMP,
    updated_by                  UUID
);

COMMENT ON TABLE asset.assets IS 'Core asset register.';
COMMENT ON TABLE asset.asset_specifications IS 'Dynamic specification values for assets.';
COMMENT ON TABLE asset.asset_installations IS 'Historical installation records for assets.';
COMMENT ON TABLE asset.asset_movements IS 'Permanent movement history for assets.';
COMMENT ON TABLE asset.stock_transactions IS 'Traceable stock ledger entries.';
COMMENT ON TABLE asset.asset_documents IS 'Documents linked to assets.';
COMMENT ON TABLE asset.asset_photos IS 'Photos linked to assets.';
COMMENT ON TABLE asset.asset_relationships IS 'Relationships between assets.';
COMMENT ON TABLE asset.maintenance_checklists IS 'Checklist headers for maintenance.';
COMMENT ON TABLE asset.checklist_items IS 'Checklist line items.';
COMMENT ON TABLE asset.maintenance_schedules IS 'Planned maintenance schedules.';
COMMENT ON TABLE asset.maintenance_history IS 'Completed maintenance events.';

ALTER TABLE common.qr_generation_history
    ADD CONSTRAINT fk_qr_generation_history_asset
    FOREIGN KEY (asset_id) REFERENCES asset.assets(id) ON UPDATE RESTRICT ON DELETE SET NULL;

ALTER TABLE common.qr_print_history
    ADD CONSTRAINT fk_qr_print_history_asset
    FOREIGN KEY (asset_id) REFERENCES asset.assets(id) ON UPDATE RESTRICT ON DELETE SET NULL;

ALTER TABLE common.barcode_history
    ADD CONSTRAINT fk_barcode_history_asset
    FOREIGN KEY (asset_id) REFERENCES asset.assets(id) ON UPDATE RESTRICT ON DELETE SET NULL;

ALTER TABLE common.favorite_assets
    ADD CONSTRAINT fk_favorite_assets_asset
    FOREIGN KEY (asset_id) REFERENCES asset.assets(id) ON UPDATE RESTRICT ON DELETE CASCADE;
