import { apiClient } from './api';
import { DashboardOverview, SystemHealth, SystemSetting } from '../types/admin';
import { User, UserProfileUpdatePayload } from '../types/user';

export const adminService = {
  async getDashboardOverview(): Promise<DashboardOverview> {
    const response = await apiClient.get<DashboardOverview>('/admin/dashboard');
    return response.data;
  },

  async getSystemHealth(): Promise<SystemHealth> {
    const response = await apiClient.get<SystemHealth>('/admin/health');
    return response.data;
  },

  async getPublicSettings(): Promise<SystemSetting[]> {
    const response = await apiClient.get<SystemSetting[]>('/system/settings/public');
    return response.data;
  },

  async updateProfile(payload: UserProfileUpdatePayload): Promise<User> {
    const response = await apiClient.put<User>('/profile', payload);
    return response.data;
  },
};
