import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { notificationService, NotificationFilterParams } from '../services/notificationService';
import type {
  NotificationItem,
  NotificationSummaryStats,
  NotificationTemplate,
  NotificationSettings,
  ChannelConfigItem,
  SingleNotificationPayload,
  BulkNotificationPayload,
  BulkNotificationResponse,
  MissingContactsResponse,
  AttendanceAlertsResponse,
  AttendanceAlertNotifyRequest,
  AttendanceAlertNotifyResponse,
  ResultAlertsResponse,
  ResultAlertNotifyRequest,
  ResultAlertNotifyResponse,
  MessagePreviewResponse,
  NotificationCountersResponse,
  NotificationTemplateUpdate,
} from '../types/notification';

export const useNotificationStore = defineStore('notification', () => {
  // State
  const notifications = ref<NotificationItem[]>([]);
  const totalNotifications = ref<number>(0);
  const currentPage = ref<number>(1);
  const totalPages = ref<number>(1);
  const pageSize = ref<number>(20);

  const stats = ref<NotificationSummaryStats | null>(null);
  const counters = ref<NotificationCountersResponse | null>(null);
  const attendanceAlerts = ref<AttendanceAlertsResponse | null>(null);
  const resultAlerts = ref<ResultAlertsResponse | null>(null);
  const templates = ref<NotificationTemplate[]>([]);
  const settings = ref<NotificationSettings | null>(null);
  const channelConfigs = ref<ChannelConfigItem[]>([]);
  const missingContacts = ref<MissingContactsResponse | null>(null);

  // In-App Header Notifications State
  const unreadCount = ref<number>(0);
  const headerNotifications = ref<NotificationItem[]>([]);
  const isHeaderLoading = ref<boolean>(false);

  // Polling Interval Reference
  let pollingTimer: any = null;

  const isLoading = ref<boolean>(false);
  const isActionLoading = ref<boolean>(false);
  const error = ref<string | null>(null);

  // Getters
  const pendingCount = computed(() => stats.value?.pending_count ?? 0);
  const failedCount = computed(() => stats.value?.failed_count ?? 0);
  const unreadAlertsCount = computed(() => {
    const attendancePending = counters.value?.absent_pending_notify_count ?? 0;
    const resultPending = counters.value?.released_results_pending_notify_count ?? 0;
    return attendancePending + resultPending;
  });

  // Actions
  async function fetchNotifications(params: NotificationFilterParams = {}) {
    isLoading.value = true;
    error.value = null;
    try {
      const mergedParams: NotificationFilterParams = {
        page: params.page || currentPage.value,
        limit: params.limit || pageSize.value,
        ...params,
      };
      const data = await notificationService.getNotifications(mergedParams);
      notifications.value = data.items;
      totalNotifications.value = data.total;
      currentPage.value = data.page;
      totalPages.value = data.total_pages;
      pageSize.value = data.limit;
      return data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to load notifications.';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchStats() {
    try {
      const data = await notificationService.getStats();
      stats.value = data;
      return data;
    } catch (err) {
      console.error('Failed to fetch notification stats', err);
    }
  }

  async function fetchCounters() {
    try {
      const data = await notificationService.getCounters();
      counters.value = data;
      return data;
    } catch (err) {
      console.error('Failed to fetch notification counters', err);
    }
  }

  async function fetchAttendanceAlerts(date?: string) {
    isLoading.value = true;
    try {
      const data = await notificationService.getAttendanceAlerts(date);
      attendanceAlerts.value = data;
      return data;
    } finally {
      isLoading.value = false;
    }
  }

  async function previewAttendanceAlerts(payload: AttendanceAlertNotifyRequest): Promise<MessagePreviewResponse> {
    isActionLoading.value = true;
    try {
      return await notificationService.previewAttendanceAlerts(payload);
    } finally {
      isActionLoading.value = false;
    }
  }

  async function notifyAttendanceAlerts(payload: AttendanceAlertNotifyRequest): Promise<AttendanceAlertNotifyResponse> {
    isActionLoading.value = true;
    try {
      const res = await notificationService.notifyAttendanceAlerts(payload);
      await Promise.all([fetchCounters(), fetchStats(), fetchAttendanceAlerts(payload.date)]);
      return res;
    } finally {
      isActionLoading.value = false;
    }
  }

  async function fetchResultAlerts(academicYear?: string) {
    isLoading.value = true;
    try {
      const data = await notificationService.getResultAlerts(academicYear);
      resultAlerts.value = data;
      return data;
    } finally {
      isLoading.value = false;
    }
  }

  async function previewResultAlerts(payload: ResultAlertNotifyRequest): Promise<MessagePreviewResponse> {
    isActionLoading.value = true;
    try {
      return await notificationService.previewResultAlerts(payload);
    } finally {
      isActionLoading.value = false;
    }
  }

  async function notifyResultAlerts(payload: ResultAlertNotifyRequest): Promise<ResultAlertNotifyResponse> {
    isActionLoading.value = true;
    try {
      const res = await notificationService.notifyResultAlerts(payload);
      await Promise.all([fetchCounters(), fetchStats(), fetchResultAlerts()]);
      return res;
    } finally {
      isActionLoading.value = false;
    }
  }

  async function fetchTemplates() {
    try {
      const data = await notificationService.getTemplates();
      templates.value = data;
      return data;
    } catch (err) {
      console.error('Failed to fetch notification templates', err);
    }
  }

  async function updateTemplate(code: string, data: NotificationTemplateUpdate) {
    isActionLoading.value = true;
    try {
      const updated = await notificationService.updateTemplate(code, data);
      await fetchTemplates();
      return updated;
    } finally {
      isActionLoading.value = false;
    }
  }

  async function fetchSettings() {
    try {
      const data = await notificationService.getSettings();
      settings.value = data;
      return data;
    } catch (err) {
      console.error('Failed to fetch notification settings', err);
    }
  }

  async function updateSettings(newSettings: Partial<NotificationSettings>) {
    isActionLoading.value = true;
    try {
      const updated = await notificationService.updateSettings(newSettings);
      settings.value = updated;
      return updated;
    } finally {
      isActionLoading.value = false;
    }
  }

  async function fetchChannelConfigs() {
    try {
      const data = await notificationService.getChannelConfigs();
      channelConfigs.value = data.channels;
      return data.channels;
    } catch (err) {
      console.error('Failed to fetch channel configs', err);
    }
  }

  async function fetchMissingContacts(classId?: number, academicYear?: string) {
    try {
      const data = await notificationService.getMissingContacts(classId, academicYear);
      missingContacts.value = data;
      return data;
    } catch (err) {
      console.error('Failed to fetch missing contacts', err);
    }
  }

  async function sendSingleNotification(payload: SingleNotificationPayload): Promise<NotificationItem> {
    isActionLoading.value = true;
    try {
      const notif = await notificationService.sendSingle(payload);
      await Promise.all([fetchStats(), fetchCounters(), fetchNotifications({ page: 1 })]);
      return notif;
    } finally {
      isActionLoading.value = false;
    }
  }

  async function sendBulkNotifications(payload: BulkNotificationPayload): Promise<BulkNotificationResponse> {
    isActionLoading.value = true;
    try {
      const res = await notificationService.sendBulk(payload);
      await Promise.all([fetchStats(), fetchCounters(), fetchNotifications({ page: 1 })]);
      return res;
    } finally {
      isActionLoading.value = false;
    }
  }

  async function retryNotification(id: number): Promise<NotificationItem> {
    isActionLoading.value = true;
    try {
      const updated = await notificationService.retryNotification(id);
      await Promise.all([fetchStats(), fetchCounters(), fetchNotifications()]);
      return updated;
    } finally {
      isActionLoading.value = false;
    }
  }

  async function retryAllFailed(): Promise<{ success: boolean; total_retried: number; message: string }> {
    isActionLoading.value = true;
    try {
      const res = await notificationService.retryAllFailed();
      await Promise.all([fetchStats(), fetchCounters(), fetchNotifications({ page: 1 })]);
      return res;
    } finally {
      isActionLoading.value = false;
    }
  }

  async function fetchUnreadCount() {
    try {
      const data = await notificationService.getUnreadCount();
      unreadCount.value = data.unread_count;
      return data.unread_count;
    } catch (err) {
      console.error('Failed to fetch unread notification count', err);
      return unreadCount.value;
    }
  }

  async function fetchHeaderNotifications() {
    isHeaderLoading.value = true;
    try {
      const data = await notificationService.getNotifications({
        page: 1,
        limit: 10,
      });
      headerNotifications.value = data.items;
      await fetchUnreadCount();
      return data.items;
    } catch (err) {
      console.error('Failed to fetch header notifications', err);
      return [];
    } finally {
      isHeaderLoading.value = false;
    }
  }

  async function markNotificationRead(id: number) {
    try {
      const res = await notificationService.markAsRead(id);
      // Immediately update local state
      const notif = headerNotifications.value.find(n => n.id === id);
      if (notif) {
        notif.status = 'READ';
        notif.read_at = res.read_at || new Date().toISOString();
      }
      const pageNotif = notifications.value.find(n => n.id === id);
      if (pageNotif) {
        pageNotif.status = 'READ';
        pageNotif.read_at = res.read_at || new Date().toISOString();
      }
      if (unreadCount.value > 0) {
        unreadCount.value--;
      }
      // Sync stats in background
      fetchStats();
      return res;
    } catch (err) {
      console.error(`Failed to mark notification ${id} as read`, err);
      throw err;
    }
  }

  async function markAllNotificationsRead() {
    isActionLoading.value = true;
    try {
      const res = await notificationService.markAllAsRead();
      const now = new Date().toISOString();
      headerNotifications.value.forEach(n => {
        n.status = 'READ';
        n.read_at = now;
      });
      notifications.value.forEach(n => {
        n.status = 'READ';
        n.read_at = now;
      });
      unreadCount.value = 0;
      fetchStats();
      return res;
    } catch (err) {
      console.error('Failed to mark all notifications as read', err);
      throw err;
    } finally {
      isActionLoading.value = false;
    }
  }

  function startNotificationPolling(intervalMs = 30000) {
    if (pollingTimer) return;
    fetchUnreadCount();
    pollingTimer = setInterval(() => {
      if (typeof document !== 'undefined' && document.hidden) return;
      fetchUnreadCount();
    }, intervalMs);
  }

  function stopNotificationPolling() {
    if (pollingTimer) {
      clearInterval(pollingTimer);
      pollingTimer = null;
    }
  }

  return {
    notifications,
    totalNotifications,
    currentPage,
    totalPages,
    pageSize,
    stats,
    counters,
    attendanceAlerts,
    resultAlerts,
    templates,
    settings,
    channelConfigs,
    missingContacts,
    unreadCount,
    headerNotifications,
    isHeaderLoading,
    isLoading,
    isActionLoading,
    error,
    pendingCount,
    failedCount,
    unreadAlertsCount,
    fetchNotifications,
    fetchStats,
    fetchCounters,
    fetchAttendanceAlerts,
    previewAttendanceAlerts,
    notifyAttendanceAlerts,
    fetchResultAlerts,
    previewResultAlerts,
    notifyResultAlerts,
    fetchTemplates,
    updateTemplate,
    fetchSettings,
    updateSettings,
    fetchChannelConfigs,
    fetchMissingContacts,
    fetchUnreadCount,
    fetchHeaderNotifications,
    markNotificationRead,
    markAllNotificationsRead,
    startNotificationPolling,
    stopNotificationPolling,
    sendSingleNotification,
    sendBulkNotifications,
    retryNotification,
    retryAllFailed,
  };
});
