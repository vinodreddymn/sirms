import { api } from './api';
import type { Expense, Paginated } from '../features/finance/types';

export const expensesApi = {
  list: (params = {}) => api.get<Paginated<Expense>>('/expenses', { params }),
  get: (id: string) => api.get<Expense>(`/expenses/${id}`),
  create: (payload: any) => api.post('/expenses', payload),
  update: (id: string, payload: any) => api.put(`/expenses/${id}`, payload),
  delete: (id: string) => api.delete(`/expenses/${id}`),
  listAttachments: (id: string) => api.get(`/expenses/${id}/attachments`),
  uploadAttachment: (id: string, payload: any) => api.post(`/expenses/${id}/attachments`, payload),
  deleteAttachment: (id: string) => api.delete(`/expenses/attachments/${id}`),
};
