export interface Incident {
  id: string;
  incident_number: string;
  project_id: string;
  asset_id?: string | null;
  location_id?: string | null;
  incident_status_id: number;
  incident_priority_id: number;
  incident_category_id?: number | null;
  reported_by?: string | null;
  reported_at: string;
  description: string;
  closed_date?: string | null;
  closed_by?: string | null;
  resolution_remarks?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface IncidentUpdate {
  id: string;
  incident_id: string;
  status_after_update_id?: number | null;
  updated_by?: string | null;
  update_notes: string;
  update_at?: string;
  created_at: string;
}

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface Lookup {
  id: number | string;
  name: string;
  code?: string;
}
