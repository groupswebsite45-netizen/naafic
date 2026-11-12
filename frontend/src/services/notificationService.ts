import { apiClient } from './api';
import type {
  NotificationListResponse,
  NotificationItem,
  NotificationSummaryStats,
  NotificationTemplate,
  NotificationSettings,
  ChannelConfigItem,
  ChannelConfigResponse,
  MissingContactsResponse,
  SingleNotificationPayload,
  BulkNotificationPayload,
  BulkNotificationResponse,
  AttendanceAlertsResponse,
  AttendanceAlertNotifyRequest,
  AttendanceAlertNotifyResponse,
  ResultAlertsResponse,
  ResultAlertNotifyRequest,
  ResultAlertNotifyResponse,
  MessagePreviewResponse,
  NotificationCountersResponse,
  NotificationTemplateUpdate,
  HormuudConnectionTestResult,
  HormuudBalanceResult,
} from '../types/notification';

export interface NotificationFilterParams {
  page?: number;
  limit?: number;
  status?: string;
  notification_type?: string;
  channel?: string;
  class_id?: number;
  student_id?: number;
  start_date?: string;
  end_date?: string;
  search?: string;
  academic_year?: string;
}

export const notificationService = {
  async getNotifications(params: NotificationFilterParams = {}): Promise<NotificationListResponse> {
    const response = await apiClient.get<NotificationListResponse>('/notifications', { params });
    return response.data;
  },

  async getStats(): Promise<NotificationSummaryStats> {
    const response = await apiClient.get<NotificationSummaryStats>('/notifications/stats');
    return response.data;
  },

  async getCounters(): Promise<NotificationCountersResponse> {
    const response = await apiClient.get<NotificationCountersResponse>('/notifications/counters');
    return response.data;
  },

  async getAttendanceAlerts(date?: string): Promise<AttendanceAlertsResponse> {
    const response = await apiClient.get<AttendanceAlertsResponse>('/notifications/attendance-alerts', {
      params: date ? { date } : {}
    });
    return response.data;
  },

  async previewAttendanceAlerts(payload: AttendanceAlertNotifyRequest): Promise<MessagePreviewResponse> {
    const response = await apiClient.post<MessagePreviewResponse>('/notifications/attendance-alerts/preview', payload);
    return response.data;
  },

  async notifyAttendanceAlerts(payload: AttendanceAlertNotifyRequest): Promise<AttendanceAlertNotifyResponse> {
    const response = await apiClient.post<AttendanceAlertNotifyResponse>('/notifications/attendance-alerts/notify', payload);
    return response.data;
  },

  async getResultAlerts(academicYear?: string): Promise<ResultAlertsResponse> {
    const response = await apiClient.get<ResultAlertsResponse>('/notifications/result-alerts', {
      params: academicYear ? { academic_year: academicYear } : {}
    });
    return response.data;
  },

  async previewResultAlerts(payload: ResultAlertNotifyRequest): Promise<MessagePreviewResponse> {
    const response = await apiClient.post<MessagePreviewResponse>('/notifications/result-alerts/preview', payload);
    return response.data;
  },

  async notifyResultAlerts(payload: ResultAlertNotifyRequest): Promise<ResultAlertNotifyResponse> {
    const response = await apiClient.post<ResultAlertNotifyResponse>('/notifications/result-alerts/notify', payload);
    return response.data;
  },

  async getNotificationDetail(id: number): Promise<NotificationItem> {
    const response = await apiClient.get<NotificationItem>(`/notifications/${id}`);
    return response.data;
  },

  async sendSingle(payload: SingleNotificationPayload): Promise<NotificationItem> {
    const response = await apiClient.post<NotificationItem>('/notifications/send', payload);
    return response.data;
  },

  async sendBulk(payload: BulkNotificationPayload): Promise<BulkNotificationResponse> {
    const response = await apiClient.post<BulkNotificationResponse>('/notifications/send-bulk', payload);
    return response.data;
  },

  async retryNotification(id: number): Promise<NotificationItem> {
    const response = await apiClient.post<NotificationItem>(`/notifications/${id}/retry`);
    return response.data;
  },

  async retryAllFailed(): Promise<{ success: boolean; total_retried: number; message: string }> {
    const response = await apiClient.post<{ success: boolean; total_retried: number; message: string }>('/notifications/retry-failed');
    return response.data;
  },

  async getTemplates(): Promise<NotificationTemplate[]> {
    const response = await apiClient.get<NotificationTemplate[]>('/notifications/templates');
    return response.data;
  },

  async updateTemplate(code: string, data: NotificationTemplateUpdate): Promise<NotificationTemplate> {
    const response = await apiClient.put<NotificationTemplate>(`/notifications/templates/${code}`, data);
    return response.data;
  },

  async getSettings(): Promise<NotificationSettings> {
    const response = await apiClient.get<NotificationSettings>('/notifications/settings');
    return response.data;
  },

  async updateSettings(settings: Partial<NotificationSettings>): Promise<NotificationSettings> {
    const response = await apiClient.put<NotificationSettings>('/notifications/settings', settings);
    return response.data;
  },

  async getChannelConfigs(): Promise<ChannelConfigResponse> {
    const response = await apiClient.get<ChannelConfigResponse>('/notifications/channels');
    return response.data;
  },

  async getMissingContacts(classId?: number, academicYear?: string): Promise<MissingContactsResponse> {
    const response = await apiClient.get<MissingContactsResponse>('/notifications/missing-contacts', {
      params: { class_id: classId, academic_year: academicYear }
    });
    return response.data;
  },

  async getHormuudStatus(): Promise<ChannelConfigItem> {
    const response = await apiClient.get<ChannelConfigItem>('/notifications/providers/hormuud/status');
    return response.data;
  },

  async testHormuudConnection(): Promise<HormuudConnectionTestResult> {
    const response = await apiClient.post<HormuudConnectionTestResult>('/notifications/providers/hormuud/test-connection');
    return response.data;
  },

  async getHormuudBalance(): Promise<HormuudBalanceResult> {
    const response = await apiClient.get<HormuudBalanceResult>('/notifications/providers/hormuud/balance');
    return response.data;
  },

  async getUnreadCount(): Promise<{ unread_count: number }> {
    const response = await apiClient.get<{ unread_count: number }>('/notifications/unread-count');
    return response.data;
  },

  async markAsRead(id: number): Promise<{ success: boolean; id: number; status: string; read_at: string }> {
    const response = await apiClient.post<{ success: boolean; id: number; status: string; read_at: string }>(`/notifications/${id}/read`);
    return response.data;
  },

  async markAllAsRead(): Promise<{ success: boolean; marked_count: number }> {
    const response = await apiClient.post<{ success: boolean; marked_count: number }>('/notifications/mark-all-read');
    return response.data;
  },
};
