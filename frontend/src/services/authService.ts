import { apiClient } from './api';
import {
  LoginPayload,
  AuthResponse,
  CurrentUserResponse,
  PasswordChangePayload,
} from '../types/auth';

export const authService = {
  async login(payload: LoginPayload): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/login', payload);
    return response.data;
  },

  async getCurrentUser(): Promise<CurrentUserResponse> {
    const response = await apiClient.get<CurrentUserResponse>('/auth/me');
    return response.data;
  },

  async logout(refreshToken?: string): Promise<void> {
    try {
      await apiClient.post('/auth/logout', { refresh_token: refreshToken });
    } catch {
      // Best effort server revocation
    }
  },

  async changePassword(payload: PasswordChangePayload): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>('/profile/change-password', payload);
    return response.data;
  },
};
