export interface WorkRequest {
  id: string;
  work_request_number: string;
  project_id: string;
  work_type_id?: string | null;
  asset_id?: string | null;
  location_id?: string | null;
  status_id: number;
  priority_id: number;
  category_id?: number | null;
  
  reported_by?: string | null;
  assigned_to_id?: string | null;

  target_start_date?: string | null;
  target_completion_date?: string | null;
  actual_start_date?: string | null;
  actual_completion_date?: string | null;
  
  estimated_cost?: number | null;
  actual_cost?: number | null;

  reported_at: string;
  description: string;
  closed_date?: string | null;
  closed_by?: string | null;
  completion_notes?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface WorkRequestUpdate {
  id: string;
  incident_id: string;
  status_after_update_id?: number | null;
  updated_by?: string | null;
  update_notes: string;
  time_spent_minutes?: number | null;
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
