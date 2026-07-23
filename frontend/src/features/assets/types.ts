export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface LookupOption {
  id: string;
  code?: string | null;
  name: string;
}

export interface AssetListItem {
  id: string;
  asset_number: string;
  category: string;
  subcategory?: string | null;
  manufacturer?: string | null;
  model?: string | null;
  serial_number?: string | null;
  barcode?: string | null;
  status: string;
  condition?: string | null;
  lifecycle?: string | null;
  current_location?: string | null;
  purchase_date?: string | null;
  warranty_expiry?: string | null;
  remarks?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface AssetSummary {
  total_assets: number;
  active_assets: number;
  assets_in_repair: number;
  retired_assets: number;
  warranty_expiring_soon: number;
}

export interface AssetLookupValue {
  id: string | number;
  code?: string | null;
  name: string;
}

export interface AssetSpecificationValue {
  id: string;
  specification_definition_id: number;
  specification_name: string;
  code: string;
  data_type: 'TEXT' | 'NUMBER' | 'BOOLEAN' | 'DATE' | 'JSON';
  unit?: string | null;
  value: string | number | boolean | Record<string, unknown> | null;
  created_at: string;
  updated_at?: string | null;
}

export interface AssetRelationship {
  id: string;
  related_asset_id: string;
  related_asset_number: string;
  related_asset_name: string;
  relationship_type?: string | null;
  direction: string;
}

export interface AssetMovementHistory {
  id: string;
  movement_type?: string | null;
  from_location?: string | null;
  to_location?: string | null;
  vendor?: string | null;
  quantity?: number | null;
  moved_at: string;
  remarks?: string | null;
}

export interface AssetDocument {
  id: string;
  attachment_id: string;
  file_name: string;
  file_path: string;
  mime_type?: string | null;
  file_size_bytes?: number | null;
  document_type?: string | null;
  created_at: string;
}

export interface AssetPhoto {
  id: string;
  attachment_id: string;
  file_name: string;
  file_path: string;
  mime_type?: string | null;
  created_at: string;
}

export interface AssetChecklistTask {
  id: string;
  task_description: string;
  sequence_order: number;
  is_required: boolean;
}

export interface AssetMaintenanceSchedule {
  id: string;
  checklist_id: string;
  checklist_name: string;
  next_due_date?: string | null;
  frequency_days?: number | null;
  is_active: boolean;
  last_maintenance?: string | null;
  tasks: AssetChecklistTask[];
}

export interface AssetMaintenanceHistory {
  id: string;
  schedule_id: string;
  checklist_name: string;
  performed_on?: string | null;
  completed: boolean;
  remarks?: string | null;
  performed_by?: string | null;
}

export interface AssetDetails {
  id: string;
  basic_information: AssetListItem;
  qr_code?: string | null;
  project: AssetLookupValue;
  status: AssetLookupValue;
  condition?: AssetLookupValue | null;
  lifecycle?: AssetLookupValue | null;
  category: AssetLookupValue;
  subcategory?: AssetLookupValue | null;
  manufacturer?: AssetLookupValue | null;
  model?: AssetLookupValue | null;
  installation?: {
    location_id?: string | null;
    location_name?: string | null;
    position_id?: string | null;
    position_name?: string | null;
    installed_on?: string | null;
    removed_on?: string | null;
    current_flag: boolean;
    installation_status?: string | null;
    remarks?: string | null;
    // Fixed infrastructure — belongs to the Position
    power_source?: string | null;
    electrical_panel?: string | null;
    network_switch?: string | null;
    switch_port?: string | null;
    patch_panel?: string | null;
    junction_box?: string | null;
    mounting_details?: string | null;
    infrastructure_details?: Record<string, unknown> | null;
  } | null;
  specifications: AssetSpecificationValue[];
  power_sources: AssetRelationship[];
  network_connections: AssetRelationship[];
  parent_assets: AssetRelationship[];
  child_assets: AssetRelationship[];
  related_assets: AssetRelationship[];
  movement_history: AssetMovementHistory[];
  documents: AssetDocument[];
  photos: AssetPhoto[];
  maintenance_schedules: AssetMaintenanceSchedule[];
  maintenance_history: AssetMaintenanceHistory[];
}

export interface AssetSpecificationDefinition {
  id: number;
  code: string;
  name: string;
  data_type: 'TEXT' | 'NUMBER' | 'BOOLEAN' | 'DATE' | 'JSON';
  unit_of_measure?: string | null;
  required_flag: boolean;
  display_order: number;
}

export interface AssetFormPayload {
  project_id: string;
  asset_number: string;
  asset_category_id: number;
  asset_subcategory_id?: number | null;
  manufacturer_id?: number | null;
  asset_model_id?: number | null;
  asset_status_id: number;
  asset_condition_id?: number | null;
  asset_lifecycle_id?: number | null;
  serial_number?: string | null;
  barcode?: string | null;
  qr_code?: string | null;
  purchase_date?: string | null;
  warranty_expiry?: string | null;
  current_location_id?: string | null;
  remarks?: string | null;
  location_position_id?: string | null;
  installation_date?: string | null;
  specification_values: AssetSpecificationFormValue[];
  relationship_ids: {
    POWERED_BY: string[];
    CONNECTED_TO: string[];
    PARENT_OF: string[];
    CHILD_OF: string[];
  };
}

export interface AssetSpecificationFormValue {
  specification_definition_id: number;
  value_text?: string | null;
  value_number?: number | null;
  value_boolean?: boolean | null;
  value_date?: string | null;
  value_json?: Record<string, unknown> | null;
}
