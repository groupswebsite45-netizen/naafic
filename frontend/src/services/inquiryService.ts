import { apiClient } from './api';
import {
  Inquiry,
  InquiryListResponse,
  InquiryStats,
  InquiryCreatePayload,
  InquiryUpdatePayload,
  InquiryConvertPayload,
  InquiryConvertResponse,
} from '../types/inquiry';

export const inquiryService = {
  // Public Landing Page submission
  async submitPublicInquiry(payload: InquiryCreatePayload): Promise<Inquiry> {
    const response = await apiClient.post<Inquiry>('/public/inquiries', payload);
    return response.data;
  },

  // Super Admin Inbox APIs
  async getInquiryStats(): Promise<InquiryStats> {
    const response = await apiClient.get<InquiryStats>('/super-admin/inquiries/stats');
    return response.data;
  },

  async getInquiries(params?: {
    status?: string;
    priority?: string;
    search?: string;
    skip?: number;
    limit?: number;
  }): Promise<InquiryListResponse> {
    const response = await apiClient.get<InquiryListResponse>('/super-admin/inquiries', { params });
    return response.data;
  },

  async getInquiry(id: number): Promise<Inquiry> {
    const response = await apiClient.get<Inquiry>(`/super-admin/inquiries/${id}`);
    return response.data;
  },

  async updateInquiry(id: number, payload: InquiryUpdatePayload): Promise<Inquiry> {
    const response = await apiClient.patch<Inquiry>(`/super-admin/inquiries/${id}`, payload);
    return response.data;
  },

  async convertInquiry(id: number, payload: InquiryConvertPayload = {}): Promise<InquiryConvertResponse> {
    const response = await apiClient.post<InquiryConvertResponse>(`/super-admin/inquiries/${id}/convert`, payload);
    return response.data;
  },

  async deleteInquiry(id: number): Promise<void> {
    await apiClient.delete(`/super-admin/inquiries/${id}`);
  },
};
