export type NotificationStatus =
  | 'PENDING'
  | 'QUEUED'
  | 'SENT'
  | 'DELIVERED'
  | 'READ'
  | 'FAILED'
  | 'NOT_SENT'
  | 'NOT_CONFIGURED';

export type NotificationType =
  | 'ATTENDANCE_ABSENT'
  | 'RESULT_RELEASED'
  | 'FEE_REMINDER'
  | 'GENERAL_ANNOUNCEMENT'
  | 'CUSTOM';

export type NotificationChannel = 'SMS' | 'EMAIL' | 'IN_APP' | 'WHATSAPP';

export interface NotificationTemplate {
  id: number;
  code: string;
  name: string;
  title_template: string;
  body_template: string;
  category: string;
  is_active: boolean;
  is_system: boolean;
  created_at: string;
  updated_at: string;
}

export interface NotificationDelivery {
  id: number;
  notification_id: number;
  channel: string;
  recipient: string;
  provider_name?: string | null;
  provider_message_id?: string | null;
  status: NotificationStatus;
  error_code?: string | null;
  error_message?: string | null;
  attempt_number: number;
  sent_at?: string | null;
  delivered_at?: string | null;
  created_at: string;
}

export interface NotificationItem {
  id: number;
  notification_type: NotificationType;
  title: string;
  message: string;
  channel: NotificationChannel;
  status: NotificationStatus;
  failure_reason?: string | null;
  student_id?: number | null;
  student_name?: string | null;
  student_admission_number?: string | null;
  guardian_name?: string | null;
  guardian_phone?: string | null;
  guardian_email?: string | null;
  guardian_relationship?: string | null;
  class_id?: number | null;
  class_name?: string | null;
  academic_year?: string | null;
  related_attendance_id?: number | null;
  related_exam_id?: number | null;
  related_result_id?: number | null;
  related_release_batch_id?: number | null;
  idempotency_key?: string | null;
  created_by_id?: number | null;
  attempt_count: number;
  created_at: string;
  sent_at?: string | null;
  delivered_at?: string | null;
  read_at?: string | null;
  deliveries?: NotificationDelivery[];
  extra_data?: Record<string, any> | null;
}

export interface NotificationListResponse {
  total: number;
  page: number;
  limit: number;
  total_pages: number;
  items: NotificationItem[];
}

export interface NotificationSummaryStats {
  total_notifications: number;
  delivered_count: number;
  pending_count: number;
  failed_count: number;
  not_sent_count: number;
  not_configured_count: number;
  read_count: number;
  sms_count: number;
  email_count: number;
  in_app_count: number;
  today_count: number;
  missing_contact_students: number;
}

export interface SingleNotificationPayload {
  student_id: number;
  notification_type: string;
  title: string;
  message: string;
  channel: string;
  custom_guardian_phone?: string;
  custom_guardian_email?: string;
}

export interface BulkNotificationPayload {
  target_type: 'ALL_ACTIVE' | 'CLASS' | 'SELECTED_STUDENTS';
  class_id?: number;
  student_ids?: number[];
  academic_year?: string;
  notification_type: string;
  title: string;
  message: string;
  channel: string;
}

export interface BulkNotificationResponse {
  success: boolean;
  message: string;
  target_type: string;
  total_targeted: number;
  eligible_count: number;
  missing_contact_count: number;
  created_count: number;
  skipped_duplicates_count: number;
  notifications: NotificationItem[];
}

export interface NotificationSettings {
  notify_attendance_absent_enabled: boolean;
  notify_result_release_enabled: boolean;
  default_channel: string;
  school_name: string;
  sms_sender_id: string;
}

export interface ChannelConfigItem {
  channel: string;
  name?: string;
  provider_name?: string;
  is_configured: boolean;
  status_code?: string;
  status_label: string;
  sender_id?: string;
  base_url?: string;
  account_username?: string;
  details: string;
}

export interface ChannelConfigResponse {
  channels: ChannelConfigItem[];
}

export interface HormuudConnectionTestResult {
  success: boolean;
  status: 'CONNECTED' | 'NOT_CONFIGURED' | 'AUTHENTICATION_ERROR' | 'UNAVAILABLE';
  message: string;
  response_time_ms: number;
  sender_id?: string;
  base_url?: string;
  balance?: any;
  http_status?: number | null;
  endpoint?: string;
  reason?: string;
  checked_at: string;
}

export interface HormuudBalanceResult {
  success: boolean;
  is_configured: boolean;
  balance: any;
  service?: string;
  sender_id?: string;
  message?: string;
  http_status?: number | null;
  endpoint?: string;
  last_checked: string;
}

export interface MissingContactStudent {
  student_id: number;
  admission_number: string;
  full_name: string;
  class_name?: string | null;
  guardian_name?: string | null;
  guardian_relationship?: string | null;
  has_phone: boolean;
  has_email: boolean;
  status: string;
}

export interface MissingContactsResponse {
  total_missing: number;
  class_id?: number | null;
  students: MissingContactStudent[];
}

export interface AttendanceAlertStudentItem {
  student_id: number;
  student_name: string;
  admission_number: string;
  attendance_id: number;
  attendance_date: string;
  attendance_status: string;
  guardian_id?: number | null;
  guardian_name?: string | null;
  guardian_phone?: string | null;
  has_valid_contact: boolean;
  is_already_notified: boolean;
  notified_at?: string | null;
  notification_status?: string | null;
}

export interface AttendanceAlertClassGroup {
  class_id: number;
  class_name: string;
  total_absent: number;
  notified_count: number;
  pending_count: number;
  missing_contact_count: number;
  students: AttendanceAlertStudentItem[];
}

export interface AttendanceAlertsResponse {
  date: string;
  school_name: string;
  total_absent_students: number;
  total_already_notified: number;
  total_pending_notification: number;
  total_missing_contact: number;
  classes: AttendanceAlertClassGroup[];
}

export interface AttendanceAlertNotifyRequest {
  date: string;
  class_id?: number | null;
  student_ids?: number[] | null;
}

export interface AttendanceAlertNotifyResponse {
  success: boolean;
  date: string;
  total_targeted: number;
  sent_or_queued: number;
  missing_contact_count: number;
  already_notified_count: number;
  failed_count: number;
  not_configured_count: number;
  message: string;
}

export interface ResultAlertStudentItem {
  student_id: number;
  student_name: string;
  admission_number: string;
  result_id: number;
  status: string;
  guardian_id?: number | null;
  guardian_name?: string | null;
  guardian_phone?: string | null;
  has_valid_contact: boolean;
  is_already_notified: boolean;
  notified_at?: string | null;
}

export interface ResultAlertGroup {
  release_batch_id: number;
  batch_name: string;
  exam_id: number;
  exam_name: string;
  academic_year: string;
  class_id: number;
  class_name: string;
  released_at?: string | null;
  total_released: number;
  pending_notification_count: number;
  already_notified_count: number;
  missing_contact_count: number;
  students: ResultAlertStudentItem[];
}

export interface ResultAlertsResponse {
  academic_year?: string | null;
  total_unnotified_results: number;
  total_batches: number;
  groups: ResultAlertGroup[];
}

export interface ResultAlertNotifyRequest {
  release_batch_id?: number | null;
  class_id?: number | null;
  student_ids?: number[] | null;
}

export interface ResultAlertNotifyResponse {
  success: boolean;
  total_targeted: number;
  sent_or_queued: number;
  missing_contact_count: number;
  already_notified_count: number;
  failed_count: number;
  not_configured_count: number;
  message: string;
}

export interface MessagePreviewItem {
  student_id: number;
  student_name: string;
  admission_number: string;
  guardian_name: string;
  guardian_phone?: string | null;
  has_valid_contact: boolean;
  is_already_notified: boolean;
  class_name: string;
  title: string;
  rendered_message: string;
}

export interface MessagePreviewResponse {
  total: number;
  valid_contacts: number;
  missing_contacts: number;
  already_notified: number;
  sample_previews: MessagePreviewItem[];
}

export interface NotificationCountersResponse {
  absent_today_count: number;
  absent_pending_notify_count: number;
  released_results_pending_notify_count: number;
  missing_contacts_count: number;
  today_sent_count: number;
  failed_count: number;
}

export interface NotificationTemplateUpdate {
  title_template?: string;
  body_template?: string;
  is_active?: boolean;
}
