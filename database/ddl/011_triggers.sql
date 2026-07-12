/*
===============================================================================
Project     : SIRMS
Version     : 1.0
Module      : Triggers
Description : Creates updated_at, numbering, and validation triggers.
===============================================================================
*/

CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON security.users
FOR EACH ROW
EXECUTE FUNCTION common.set_updated_at();

CREATE TRIGGER trg_projects_updated_at
BEFORE UPDATE ON common.projects
FOR EACH ROW
EXECUTE FUNCTION common.set_updated_at();

CREATE TRIGGER trg_locations_updated_at
BEFORE UPDATE ON infrastructure.locations
FOR EACH ROW
EXECUTE FUNCTION common.set_updated_at();

CREATE TRIGGER trg_assets_updated_at
BEFORE UPDATE ON asset.assets
FOR EACH ROW
EXECUTE FUNCTION common.set_updated_at();

CREATE TRIGGER trg_incidents_updated_at
BEFORE UPDATE ON incident.incidents
FOR EACH ROW
EXECUTE FUNCTION common.set_updated_at();

CREATE TRIGGER trg_number_sequences_updated_at
BEFORE UPDATE ON common.number_sequences
FOR EACH ROW
EXECUTE FUNCTION common.set_updated_at();

CREATE TRIGGER trg_asset_specifications_validate
BEFORE INSERT OR UPDATE ON asset.asset_specifications
FOR EACH ROW
EXECUTE FUNCTION asset.validate_specification_value();

CREATE TRIGGER trg_asset_installations_validate_capacity
BEFORE INSERT OR UPDATE ON asset.asset_installations
FOR EACH ROW
EXECUTE FUNCTION asset.validate_installation_capacity_trigger();

CREATE TRIGGER trg_asset_installations_sync_location
AFTER INSERT OR UPDATE ON asset.asset_installations
FOR EACH ROW
EXECUTE FUNCTION asset.sync_asset_current_location();
