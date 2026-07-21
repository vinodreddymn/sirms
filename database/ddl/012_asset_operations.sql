-- O&M extensions for the asset module. Keep these records permanently.
ALTER TABLE asset.assets ADD COLUMN IF NOT EXISTS asset_role VARCHAR(20) NOT NULL DEFAULT 'SPARE';
ALTER TABLE asset.assets ADD COLUMN IF NOT EXISTS health_rating VARCHAR(20);
ALTER TABLE asset.assets ADD COLUMN IF NOT EXISTS network_configuration JSONB NOT NULL DEFAULT '{}'::jsonb;
ALTER TABLE asset.assets ADD CONSTRAINT chk_assets_asset_role CHECK (asset_role IN ('INSTALLED', 'SPARE'));
ALTER TABLE asset.assets ADD CONSTRAINT chk_assets_health_rating CHECK (health_rating IS NULL OR health_rating IN ('EXCELLENT', 'GOOD', 'AVERAGE', 'POOR', 'CRITICAL'));

CREATE TABLE IF NOT EXISTS asset.repair_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), asset_id UUID NOT NULL REFERENCES asset.assets(id), fault_date DATE NOT NULL,
    fault_description TEXT NOT NULL, removed_from_location_id UUID REFERENCES infrastructure.locations(id), removal_date DATE,
    replacement_asset_id UUID REFERENCES asset.assets(id), dispatch_date DATE, courier_number VARCHAR(100), vendor_id UUID REFERENCES common.vendors(id),
    repair_cost NUMERIC(14,2), rma_number VARCHAR(100), return_date DATE, repair_remarks TEXT, repair_warranty_expiry DATE,
    repair_report_attachment_id UUID REFERENCES common.attachments(id), created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, created_by UUID REFERENCES security.users(id)
);
CREATE TABLE IF NOT EXISTS asset.asset_replacements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), old_asset_id UUID NOT NULL REFERENCES asset.assets(id), new_asset_id UUID NOT NULL REFERENCES asset.assets(id),
    replacement_date DATE NOT NULL, engineer_id UUID REFERENCES security.users(id), reason TEXT NOT NULL, remarks TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, CONSTRAINT uq_asset_replacements_old_new_date UNIQUE(old_asset_id, new_asset_id, replacement_date)
);
CREATE TABLE IF NOT EXISTS asset.asset_timeline_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), asset_id UUID NOT NULL REFERENCES asset.assets(id), event_type VARCHAR(40) NOT NULL,
    event_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, description TEXT NOT NULL, metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb, created_by UUID REFERENCES security.users(id)
);
CREATE TABLE IF NOT EXISTS asset.asset_field_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), asset_id UUID NOT NULL REFERENCES asset.assets(id), note TEXT NOT NULL,
    observed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, created_by UUID REFERENCES security.users(id)
);
CREATE INDEX IF NOT EXISTS idx_repair_history_asset_id ON asset.repair_history(asset_id);
CREATE INDEX IF NOT EXISTS idx_asset_replacements_old_asset ON asset.asset_replacements(old_asset_id);
CREATE INDEX IF NOT EXISTS idx_asset_replacements_new_asset ON asset.asset_replacements(new_asset_id);
CREATE INDEX IF NOT EXISTS idx_asset_timeline_events_asset_at ON asset.asset_timeline_events(asset_id, event_at DESC);
CREATE INDEX IF NOT EXISTS idx_asset_field_notes_asset_at ON asset.asset_field_notes(asset_id, observed_at DESC);

INSERT INTO master.movement_types (code, name, description, display_order)
VALUES ('REPLACEMENT_OUT', 'Replacement Out', 'Asset removed during replacement', 80),
       ('REPLACEMENT_IN', 'Replacement In', 'Spare installed as replacement', 81)
ON CONFLICT (code) DO NOTHING;
