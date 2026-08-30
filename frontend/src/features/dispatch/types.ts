export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface DispatchItemListItem {
  id: string;
  dispatch_id: string;
  asset_id?: string | null;
  asset_number?: string | null;
  asset_category?: string | null;
  asset_subcategory?: string | null;
  asset_serial_number?: string | null;
  dispatch_type: 'Asset' | 'Component';
  component_name?: string | null;
  quantity: number;
  condition: 'Faulty' | 'Working' | 'Damaged';
  status: 'Out' | 'Returned';
  return_date?: string | null;
  result?: 'Repaired' | 'Replaced' | 'Beyond Repair' | 'Returned Without Repair' | null;
  repair_cost?: number | null;
  remarks?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface DispatchListItem {
  id: string;
  dispatch_no: string;
  delivery_challan_no?: string | null;
  dispatch_date: string;
  vendor_id?: string | null;
  vendor_name?: string | null;
  purpose: 'Repair' | 'Warranty' | 'Calibration' | 'Transfer' | 'Others';
  courier_name?: string | null;
  tracking_number?: string | null;
  remarks?: string | null;
  status: 'Draft' | 'Dispatched' | 'Partially Returned' | 'Closed' | 'Cancelled';
  created_at: string;
  updated_at?: string | null;
}

export interface DispatchDetails extends DispatchListItem {
  items: DispatchItemListItem[];
}

export interface DispatchFormPayload {
  dispatch_date: string;
  vendor_id?: string | null;
  purpose: 'Repair' | 'Warranty' | 'Calibration' | 'Transfer' | 'Others';
  courier_name?: string | null;
  tracking_number?: string | null;
  remarks?: string | null;
  items: DispatchItemFormPayload[];
}

export interface DispatchItemFormPayload {
  asset_id?: string | null;
  dispatch_type: 'Asset' | 'Component';
  component_name?: string | null;
  quantity: number;
  condition: 'Faulty' | 'Working' | 'Damaged';
  remarks?: string | null;
}

export interface ReceiveItemPayload {
  return_date: string;
  result: 'Repaired' | 'Replaced' | 'Beyond Repair' | 'Returned Without Repair';
  repair_cost?: number | null;
  remarks?: string | null;
  to_location_id: string | null;
}
