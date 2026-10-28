import { apiClient } from './api';
import {
  Institution,
  InstitutionCreatePayload,
  InstitutionUpdatePayload,
  Subscription,
  InstitutionPayment,
  SuperAdminDashboardStats,
} from '../types/institution';
import { User } from '../types/user';

export const superAdminService = {
  // Stats
  async getDashboardStats(): Promise<SuperAdminDashboardStats> {
    const response = await apiClient.get<SuperAdminDashboardStats>('/super-admin/stats');
    return response.data;
  },

  // Institutions
  async getInstitutions(params?: {
    q?: string;
    type?: string;
    status?: string;
    subscription_status?: string;
    skip?: number;
    limit?: number;
  }): Promise<Institution[]> {
    const response = await apiClient.get<Institution[]>('/super-admin/institutions', { params });
    return response.data;
  },

  async getInstitution(id: number): Promise<Institution> {
    const response = await apiClient.get<Institution>(`/super-admin/institutions/${id}`);
    return response.data;
  },

  async registerInstitution(payload: InstitutionCreatePayload): Promise<Institution> {
    const response = await apiClient.post<Institution>('/super-admin/institutions', payload);
    return response.data;
  },

  async updateInstitution(id: number, payload: InstitutionUpdatePayload): Promise<Institution> {
    const response = await apiClient.put<Institution>(`/super-admin/institutions/${id}`, payload);
    return response.data;
  },

  async toggleInstitutionStatus(id: number, newStatus: 'ACTIVE' | 'SUSPENDED' | 'PENDING'): Promise<{ message: string; status: string }> {
    const response = await apiClient.patch(`/super-admin/institutions/${id}/status`, null, {
      params: { new_status: newStatus },
    });
    return response.data;
  },

  async deleteInstitution(id: number, confirmationCode?: string): Promise<{ success: boolean; message: string; deleted_id: number }> {
    const response = await apiClient.delete(`/super-admin/institutions/${id}`, {
      params: { confirmation_code: confirmationCode },
    });
    return response.data;
  },

  // Subscriptions
  async getSubscriptions(params?: { institution_id?: number; status?: string }): Promise<Subscription[]> {
    const response = await apiClient.get<Subscription[]>('/super-admin/subscriptions', { params });
    return response.data;
  },

  async createSubscription(payload: {
    institution_id: number;
    plan_name: string;
    billing_cycle: string;
    price: number;
    setup_fee: number;
    status: string;
    start_date: string;
    end_date: string;
    auto_renew: boolean;
    notes?: string;
  }): Promise<Subscription> {
    const response = await apiClient.post<Subscription>('/super-admin/subscriptions', payload);
    return response.data;
  },

  // Payments
  async getPayments(params?: { institution_id?: number; status?: string }): Promise<InstitutionPayment[]> {
    const response = await apiClient.get<InstitutionPayment[]>('/super-admin/payments', { params });
    return response.data;
  },

  async recordPayment(payload: {
    institution_id: number;
    subscription_id?: number;
    reference?: string;
    amount: number;
    currency?: string;
    payment_method?: string;
    status?: string;
    invoice_number?: string;
    notes?: string;
  }): Promise<InstitutionPayment> {
    const response = await apiClient.post<InstitutionPayment>('/super-admin/payments', payload);
    return response.data;
  },

  // Users
  async getCompanyUsers(): Promise<User[]> {
    const response = await apiClient.get<User[]>('/super-admin/users');
    return response.data;
  },

  // Reports
  async getReports(): Promise<any> {
    const response = await apiClient.get('/super-admin/reports');
    return response.data;
  },

  // Settings
  async getSettings(): Promise<any> {
    const response = await apiClient.get('/super-admin/settings');
    return response.data;
  },
};
