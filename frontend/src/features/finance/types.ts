export interface Expense {
  id: string;
  expense_number?: string;
  expense_no?: string;
  project_id: string;
  expense_date: string;
  expense_category_id: string;
  expense_category_name?: string | null;
  description?: string | null;
  bill_reference?: string | null;
  amount: number;
  payment_mode_id: string;
  payment_mode_name?: string | null;
  payment_status_id: string;
  payment_status_name?: string | null;
  remarks?: string | null;
  created_at: string;
  updated_at?: string | null;
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
  name?: string;
  project_name?: string;
  project_code?: string;
  code?: string;
}
