import { api } from '../../services/api';
import type {
  DispatchDetails,
  DispatchFormPayload,
  DispatchItemListItem,
  DispatchListItem,
  PaginatedResponse,
  ReceiveItemPayload,
} from './types';

export const getDispatches = async (params?: Record<string, any>) => {
  const response = await api.get<PaginatedResponse<DispatchListItem>>('/dispatches', { params });
  return response.data;
};

export const getDispatchDetails = async (id: string) => {
  const response = await api.get<DispatchDetails>(`/dispatches/${id}`);
  return response.data;
};

export const createDispatch = async (payload: DispatchFormPayload) => {
  const response = await api.post<DispatchDetails>('/dispatches', payload);
  return response.data;
};

export const updateDispatch = async (id: string, payload: Partial<DispatchFormPayload>) => {
  const response = await api.put<DispatchDetails>(`/dispatches/${id}`, payload);
  return response.data;
};

export const submitDispatch = async (id: string) => {
  const response = await api.post<DispatchDetails>(`/dispatches/${id}/submit`);
  return response.data;
};

export const receiveDispatchItem = async (dispatchId: string, itemId: string, payload: ReceiveItemPayload) => {
  const response = await api.post<DispatchItemListItem>(`/dispatches/${dispatchId}/items/${itemId}/receive`, payload);
  return response.data;
};
