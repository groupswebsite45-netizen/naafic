<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useNotificationStore } from '../../../stores/notification';
import { notificationService } from '../../../services/notificationService';
import { studentService } from '../../../services/studentService';
import { classService } from '../../../services/classService';
import type {
  NotificationItem,
  NotificationType,
  NotificationStatus,
  SingleNotificationPayload,
  BulkNotificationPayload,
  NotificationSettings,
  NotificationTemplate,
  MessagePreviewResponse,
  MessagePreviewItem,
  HormuudConnectionTestResult,
  HormuudBalanceResult,
} from '../../../types/notification';
import type { Student, SchoolClass } from '../../../types/school';

const store = useNotificationStore();

// Top-Level Main Navigation Tab
type MainNavTab = 'OVERVIEW' | 'ATTENDANCE_ALERTS' | 'RESULT_NOTIFICATIONS' | 'SEND' | 'HISTORY' | 'TEMPLATES' | 'SETTINGS';
const activeMainTab = ref<MainNavTab>('OVERVIEW');

// Attendance Alerts Tab State
const attendanceDate = ref<string>(new Date().toISOString().split('T')[0]);
const selectedAttendanceStudentIds = ref<number[]>([]);
const expandedAttendanceClasses = ref<Record<number, boolean>>({});

// Result Alerts Tab State
const resultAcademicYear = ref<string>('2026/2027');
const selectedResultStudentIds = ref<number[]>([]);
const selectedResultBatchId = ref<number | null>(null);

// Confirmation & Live Preview Modal State
const isPreviewModalOpen = ref<boolean>(false);
const previewModalTitle = ref<string>('');
const previewActionType = ref<'ATTENDANCE_BULK' | 'ATTENDANCE_SELECTED' | 'RESULT_BULK' | 'RESULT_SELECTED'>('ATTENDANCE_BULK');
const previewSelectedClassId = ref<number | null>(null);
const previewData = ref<MessagePreviewResponse | null>(null);
const currentPreviewIndex = ref<number>(0);
const isExecutingSend = ref<boolean>(false);

// Template Management State
const editingTemplateCode = ref<string | null>(null);
const templateEditForm = reactive<{ title_template: string; body_template: string; is_active: boolean }>({
  title_template: '',
  body_template: '',
  is_active: true,
});

// History / Filter State
const historyStatusFilter = ref<string>('ALL');
const historyTypeFilter = ref<string>('ALL');
const historyChannelFilter = ref<string>('ALL');
const historyClassId = ref<number | undefined>(undefined);
const historySearchQuery = ref<string>('');

// Modals
const isDetailModalOpen = ref<boolean>(false);
const activeDetailNotification = ref<NotificationItem | null>(null);

// Somali Message Templates Constants
interface SomaliTemplateInfo {
  type: string;
  name: string;
  title: string;
  body: string;
  variables: string[];
}

const SOMALI_TEMPLATES: Record<string, SomaliTemplateInfo> = {
  ATTENDANCE_ABSENT: {
    type: 'ATTENDANCE_ABSENT',
    name: 'Attendance Absence',
    title: 'Ogeysiis Maqnaansho - {{student_name}}',
    body: 'Asc {{guardian_name}}, waxaan ku ogeysiinaynaa in ardaygaaga {{student_name}} maanta uusan imaan dugsiga. Fadlan la soco xaalkiisa. — {{school_name}}',
    variables: ['{{guardian_name}}', '{{student_name}}', '{{class_name}}', '{{date}}', '{{school_name}}'],
  },
  RESULT_RELEASED: {
    type: 'RESULT_RELEASED',
    name: 'Exam Result Released',
    title: 'Natiijada Imtixaanka - {{student_name}}',
    body: 'Asc {{guardian_name}}, waxaan ku ogeysiinaynaa in natiijada {{student_name}} ee {{exam_name}} la sii daayay. Fadlan gal Student Portal si aad u aragto natiijada. — {{school_name}}',
    variables: ['{{guardian_name}}', '{{student_name}}', '{{class_name}}', '{{exam_name}}', '{{academic_year}}', '{{school_name}}'],
  },
  FEE_REMINDER: {
    type: 'FEE_REMINDER',
    name: 'Fee Reminder',
    title: 'Xasuusin Lacagta Dugsiga - {{student_name}}',
    body: 'Asc {{guardian_name}}, waxaan ku xasuusinaynaa in ardaygaaga {{student_name}} uu leeyahay lacag dugsi oo dhan {{fee_balance}} oo harsan. Fadlan gal Student Portal si aad u hubiso faahfaahinta. — {{school_name}}',
    variables: ['{{guardian_name}}', '{{student_name}}', '{{class_name}}', '{{fee_balance}}', '{{school_name}}'],
  },
  GENERAL_ANNOUNCEMENT: {
    type: 'GENERAL_ANNOUNCEMENT',
    name: 'General Notice',
    title: 'Ogeysiis Muhiim ah - {{school_name}}',
    body: 'Asc {{guardian_name}}, waxaa jira ogeysiis cusub oo ka yimid {{school_name}}. Fadlan gal Student Portal si aad u akhrido faahfaahinta ogeysiiska.',
    variables: ['{{guardian_name}}', '{{school_name}}'],
  },
  CUSTOM: {
    type: 'CUSTOM',
    name: 'Custom Notification',
    title: '',
    body: '',
    variables: ['{{guardian_name}}', '{{student_name}}', '{{class_name}}', '{{fee_balance}}', '{{school_name}}'],
  },
};

// Send Form State
const sendMode = ref<'SINGLE' | 'CLASS' | 'SELECTED' | 'ALL'>('SINGLE');
const singleForm = reactive<SingleNotificationPayload>({
  student_id: 0,
  notification_type: 'ATTENDANCE_ABSENT',
  title: SOMALI_TEMPLATES.ATTENDANCE_ABSENT.title,
  message: SOMALI_TEMPLATES.ATTENDANCE_ABSENT.body,
  channel: 'SMS',
  custom_guardian_phone: '',
  custom_guardian_email: '',
});

const bulkForm = reactive<BulkNotificationPayload>({
  target_type: 'CLASS',
  class_id: undefined,
  student_ids: [],
  notification_type: 'ATTENDANCE_ABSENT',
  title: SOMALI_TEMPLATES.ATTENDANCE_ABSENT.title,
  message: SOMALI_TEMPLATES.ATTENDANCE_ABSENT.body,
  channel: 'SMS',
});

// Settings form
const settingsForm = reactive<NotificationSettings>({
  notify_attendance_absent_enabled: true,
  notify_result_release_enabled: true,
  default_channel: 'SMS',
  school_name: 'Education Management System',
  sms_sender_id: 'EMS',
});

// Available Data
const availableClasses = ref<SchoolClass[]>([]);
const availableStudents = ref<Student[]>([]);

// Alerts & Feedback
const successMessage = ref<string>('');
const errorMessage = ref<string>('');

function showSuccess(msg: string) {
  successMessage.value = msg;
  setTimeout(() => { successMessage.value = ''; }, 6000);
}

function showError(msg: string) {
  errorMessage.value = msg;
  setTimeout(() => { errorMessage.value = ''; }, 7000);
}

// Active variables computed for current notification type
const currentActiveVariables = computed(() => {
  const currentType = sendMode.value === 'SINGLE' ? singleForm.notification_type : bulkForm.notification_type;
  return SOMALI_TEMPLATES[currentType]?.variables || ['{{guardian_name}}', '{{student_name}}', '{{class_name}}', '{{school_name}}'];
});

// Handle Notification Type dropdown change
function onNotificationTypeChange(newType: string) {
  const tmpl = SOMALI_TEMPLATES[newType];
  if (sendMode.value === 'SINGLE') {
    singleForm.notification_type = newType;
    if (newType === 'CUSTOM') {
      singleForm.title = '';
      singleForm.message = '';
    } else if (tmpl) {
      singleForm.title = tmpl.title;
      singleForm.message = tmpl.body;
    }
  } else {
    bulkForm.notification_type = newType;
    if (newType === 'CUSTOM') {
      bulkForm.title = '';
      bulkForm.message = '';
    } else if (tmpl) {
      bulkForm.title = tmpl.title;
      bulkForm.message = tmpl.body;
    }
  }
}

// Insert Variable helper
function insertVariable(variable: string) {
  if (sendMode.value === 'SINGLE') {
    singleForm.message = (singleForm.message ? singleForm.message + ' ' : '') + variable;
  } else {
    bulkForm.message = (bulkForm.message ? bulkForm.message + ' ' : '') + variable;
  }
}

// Live Resolved Preview in Single Mode
const selectedSingleStudentPreview = computed(() => {
  if (!singleForm.student_id) return null;
  return availableStudents.value.find((s) => s.id === singleForm.student_id) || null;
});

const renderedSinglePreviewMessage = computed(() => {
  if (!selectedSingleStudentPreview.value || !singleForm.message) return '';
  const s = selectedSingleStudentPreview.value;
  const schoolName = store.settings?.school_name || 'Education Management System';
  let msg = singleForm.message;
  msg = msg.replace(/\{\{guardian_name\}\}/g, s.guardian_name || 'Waalidka');
  msg = msg.replace(/\{\{student_name\}\}/g, s.full_name || '');
  msg = msg.replace(/\{\{class_name\}\}/g, s.current_class?.name || '');
  msg = msg.replace(/\{\{school_name\}\}/g, schoolName);
  msg = msg.replace(/\{\{date\}\}/g, new Date().toLocaleDateString('so-SO', { day: 'numeric', month: 'long', year: 'numeric' }));
  msg = msg.replace(/\{\{exam_name\}\}/g, 'Imtixaanka Guud');
  msg = msg.replace(/\{\{academic_year\}\}/g, '2026/2027');
  msg = msg.replace(/\{\{fee_balance\}\}/g, '$50.00');
  return msg;
});

// Search debounce
let searchDebounceTimer: any = null;
function onSearchInput() {
  clearTimeout(searchDebounceTimer);
  searchDebounceTimer = setTimeout(() => {
    loadHistory(1);
  }, 350);
}

// Data Loaders
async function loadInitialData() {
  await Promise.allSettled([
    store.fetchCounters(),
    store.fetchStats(),
    store.fetchTemplates(),
    store.fetchSettings(),
    store.fetchChannelConfigs(),
    loadDropdowns(),
  ]);
  if (store.settings) {
    settingsForm.notify_attendance_absent_enabled = store.settings.notify_attendance_absent_enabled;
    settingsForm.notify_result_release_enabled = store.settings.notify_result_release_enabled;
    settingsForm.default_channel = store.settings.default_channel;
    settingsForm.school_name = store.settings.school_name;
    settingsForm.sms_sender_id = store.settings.sms_sender_id;
  }
}

async function loadDropdowns() {
  try {
    const classesRes = await classService.getClasses({ page: 1, page_size: 100 });
    const classList = Array.isArray(classesRes) ? classesRes : (classesRes as any)?.items || (classesRes as any)?.data || [];
    availableClasses.value = classList;
  } catch (err) {
    console.error('Error loading classes dropdown', err);
  }

  try {
    const studentsRes = await studentService.getStudents({ page: 1, page_size: 300, status: 'ACTIVE' });
    const studentList = Array.isArray(studentsRes) ? studentsRes : (studentsRes as any)?.items || (studentsRes as any)?.data || [];
    availableStudents.value = studentList;
  } catch (err) {
    console.error('Error loading students dropdown', err);
  }
}

async function loadAttendanceAlerts() {
  try {
    const res = await store.fetchAttendanceAlerts(attendanceDate.value);
    if (res && res.classes) {
      res.classes.forEach(c => {
        if (expandedAttendanceClasses.value[c.class_id] === undefined) {
          expandedAttendanceClasses.value[c.class_id] = true;
        }
      });
    }
    selectedAttendanceStudentIds.value = [];
  } catch (err: any) {
    showError(err.message || 'Failed to load attendance alerts.');
  }
}

async function loadResultAlerts() {
  try {
    await store.fetchResultAlerts(resultAcademicYear.value || undefined);
    selectedResultStudentIds.value = [];
  } catch (err: any) {
    showError(err.message || 'Failed to load result notifications.');
  }
}

async function loadHistory(page = 1) {
  let statusFilter: string | undefined = historyStatusFilter.value !== 'ALL' ? historyStatusFilter.value : undefined;
  let typeFilter: string | undefined = historyTypeFilter.value !== 'ALL' ? historyTypeFilter.value : undefined;

  try {
    await store.fetchNotifications({
      page,
      limit: store.pageSize,
      status: statusFilter,
      notification_type: typeFilter,
      channel: historyChannelFilter.value !== 'ALL' ? historyChannelFilter.value : undefined,
      class_id: historyClassId.value,
      search: historySearchQuery.value.trim() || undefined,
    });
  } catch (err: any) {
    showError(err.message || 'Failed to load notification history.');
  }
}

// Attendance Alert Selections
function toggleAttendanceClassExpand(classId: number) {
  expandedAttendanceClasses.value[classId] = !expandedAttendanceClasses.value[classId];
}

function isStudentSelected(studentId: number): boolean {
  return selectedAttendanceStudentIds.value.includes(studentId);
}

function toggleStudentSelection(studentId: number) {
  const idx = selectedAttendanceStudentIds.value.indexOf(studentId);
  if (idx > -1) {
    selectedAttendanceStudentIds.value.splice(idx, 1);
  } else {
    selectedAttendanceStudentIds.value.push(studentId);
  }
}

function isClassAllSelected(classGroup: { students: { student_id: number }[] }): boolean {
  if (!classGroup.students.length) return false;
  return classGroup.students.every(s => selectedAttendanceStudentIds.value.includes(s.student_id));
}

function toggleSelectAllClass(classGroup: { students: { student_id: number }[] }) {
  const allSelected = isClassAllSelected(classGroup);
  if (allSelected) {
    const studentIds = new Set(classGroup.students.map(s => s.student_id));
    selectedAttendanceStudentIds.value = selectedAttendanceStudentIds.value.filter(id => !studentIds.has(id));
  } else {
    classGroup.students.forEach(s => {
      if (!selectedAttendanceStudentIds.value.includes(s.student_id)) {
        selectedAttendanceStudentIds.value.push(s.student_id);
      }
    });
  }
}

function selectAllAbsentStudents() {
  if (!store.attendanceAlerts) return;
  const allIds: number[] = [];
  store.attendanceAlerts.classes.forEach(c => {
    c.students.forEach(s => {
      allIds.push(s.student_id);
    });
  });
  selectedAttendanceStudentIds.value = allIds;
}

function clearAllAttendanceSelection() {
  selectedAttendanceStudentIds.value = [];
}

// Preview & Dispatch Workflows
async function openAttendanceBulkPreview(classId?: number) {
  try {
    previewActionType.value = classId ? 'ATTENDANCE_SELECTED' : 'ATTENDANCE_BULK';
    previewSelectedClassId.value = classId || null;
    previewModalTitle.value = classId ? 'Notify Class Absent Guardians' : 'Notify ALL Absent Guardians';

    const payload = {
      date: attendanceDate.value,
      class_id: classId || undefined,
      student_ids: selectedAttendanceStudentIds.value.length > 0 && !classId ? selectedAttendanceStudentIds.value : undefined,
    };

    const res = await store.previewAttendanceAlerts(payload);
    previewData.value = res;
    currentPreviewIndex.value = 0;
    isPreviewModalOpen.value = true;
  } catch (err: any) {
    showError(err.message || 'Failed to generate attendance message preview.');
  }
}

async function openAttendanceSelectedPreview() {
  if (selectedAttendanceStudentIds.value.length === 0) {
    showError('Please select at least one absent student.');
    return;
  }
  try {
    previewActionType.value = 'ATTENDANCE_SELECTED';
    previewSelectedClassId.value = null;
    previewModalTitle.value = `Notify Selected Guardians (${selectedAttendanceStudentIds.value.length} students)`;

    const payload = {
      date: attendanceDate.value,
      student_ids: selectedAttendanceStudentIds.value,
    };

    const res = await store.previewAttendanceAlerts(payload);
    previewData.value = res;
    currentPreviewIndex.value = 0;
    isPreviewModalOpen.value = true;
  } catch (err: any) {
    showError(err.message || 'Failed to generate attendance message preview.');
  }
}

async function openResultBulkPreview(batchId?: number, classId?: number) {
  try {
    previewActionType.value = 'RESULT_BULK';
    selectedResultBatchId.value = batchId || null;
    previewModalTitle.value = 'Notify Released Exam Result Guardians';

    const payload = {
      release_batch_id: batchId || undefined,
      class_id: classId || undefined,
      student_ids: selectedResultStudentIds.value.length > 0 ? selectedResultStudentIds.value : undefined,
    };

    const res = await store.previewResultAlerts(payload);
    previewData.value = res;
    currentPreviewIndex.value = 0;
    isPreviewModalOpen.value = true;
  } catch (err: any) {
    showError(err.message || 'Failed to generate result message preview.');
  }
}

async function openResultSelectedPreview(batchId: number) {
  if (selectedResultStudentIds.value.length === 0) {
    showError('Please select at least one student result.');
    return;
  }
  try {
    previewActionType.value = 'RESULT_SELECTED';
    selectedResultBatchId.value = batchId;
    previewModalTitle.value = `Notify Selected Result Guardians (${selectedResultStudentIds.value.length} students)`;

    const payload = {
      release_batch_id: batchId,
      student_ids: selectedResultStudentIds.value,
    };

    const res = await store.previewResultAlerts(payload);
    previewData.value = res;
    currentPreviewIndex.value = 0;
    isPreviewModalOpen.value = true;
  } catch (err: any) {
    showError(err.message || 'Failed to generate result message preview.');
  }
}

async function executeConfirmSend() {
  isExecutingSend.value = true;
  try {
    if (previewActionType.value === 'ATTENDANCE_BULK' || previewActionType.value === 'ATTENDANCE_SELECTED') {
      const payload = {
        date: attendanceDate.value,
        class_id: previewSelectedClassId.value || undefined,
        student_ids: selectedAttendanceStudentIds.value.length > 0 && previewActionType.value === 'ATTENDANCE_SELECTED'
          ? selectedAttendanceStudentIds.value
          : undefined,
      };
      const res = await store.notifyAttendanceAlerts(payload);
      isPreviewModalOpen.value = false;
      showSuccess(res.message);
      selectedAttendanceStudentIds.value = [];
    } else {
      const payload = {
        release_batch_id: selectedResultBatchId.value || undefined,
        student_ids: selectedResultStudentIds.value.length > 0 && previewActionType.value === 'RESULT_SELECTED'
          ? selectedResultStudentIds.value
          : undefined,
      };
      const res = await store.notifyResultAlerts(payload);
      isPreviewModalOpen.value = false;
      showSuccess(res.message);
      selectedResultStudentIds.value = [];
    }
  } catch (err: any) {
    showError(err.message || 'Failed to dispatch notifications.');
  } finally {
    isExecutingSend.value = false;
  }
}

// Carousel Navigation
function prevPreview() {
  if (currentPreviewIndex.value > 0) {
    currentPreviewIndex.value--;
  }
}

function nextPreview() {
  if (previewData.value && currentPreviewIndex.value < previewData.value.sample_previews.length - 1) {
    currentPreviewIndex.value++;
  }
}

const currentSamplePreview = computed<MessagePreviewItem | null>(() => {
  if (!previewData.value || !previewData.value.sample_previews.length) return null;
  return previewData.value.sample_previews[currentPreviewIndex.value] || null;
});

// Result Selection helpers
function toggleResultStudentSelection(studentId: number) {
  const idx = selectedResultStudentIds.value.indexOf(studentId);
  if (idx > -1) {
    selectedResultStudentIds.value.splice(idx, 1);
  } else {
    selectedResultStudentIds.value.push(studentId);
  }
}

function isResultStudentSelected(studentId: number): boolean {
  return selectedResultStudentIds.value.includes(studentId);
}

function isResultGroupAllSelected(group: { students: { student_id: number }[] }): boolean {
  if (!group.students.length) return false;
  return group.students.every(s => selectedResultStudentIds.value.includes(s.student_id));
}

function toggleSelectAllResultGroup(group: { students: { student_id: number }[] }) {
  const allSelected = isResultGroupAllSelected(group);
  if (allSelected) {
    const studentIds = new Set(group.students.map(s => s.student_id));
    selectedResultStudentIds.value = selectedResultStudentIds.value.filter(id => !studentIds.has(id));
  } else {
    group.students.forEach(s => {
      if (!selectedResultStudentIds.value.includes(s.student_id)) {
        selectedResultStudentIds.value.push(s.student_id);
      }
    });
  }
}

// Template Actions
function startEditTemplate(tmpl: NotificationTemplate) {
  editingTemplateCode.value = tmpl.code;
  templateEditForm.title_template = tmpl.title_template;
  templateEditForm.body_template = tmpl.body_template;
  templateEditForm.is_active = tmpl.is_active;
}

function cancelEditTemplate() {
  editingTemplateCode.value = null;
}

async function saveEditedTemplate() {
  if (!editingTemplateCode.value) return;
  try {
    await store.updateTemplate(editingTemplateCode.value, templateEditForm);
    editingTemplateCode.value = null;
    showSuccess('Notification template updated successfully in PostgreSQL.');
  } catch (err: any) {
    showError(err.message || 'Failed to update template.');
  }
}

// Hormuud Provider Status & Diagnostics
const isTestingConnection = ref(false);
const connectionTestResult = ref<HormuudConnectionTestResult | null>(null);
const isCheckingBalance = ref(false);
const hormuudBalanceInfo = ref<HormuudBalanceResult | null>(null);

async function handleTestHormuudConnection() {
  isTestingConnection.value = true;
  connectionTestResult.value = null;
  try {
    const res = await notificationService.testHormuudConnection();
    connectionTestResult.value = res;
    if (res.success) {
      showSuccess(res.message);
    } else {
      showError(res.message);
    }
  } catch (err: any) {
    const httpStatus = err.response?.status || null;
    const reqUrl = err.config?.url || '/notifications/providers/hormuud/test-connection';
    const endpoint = `POST ${err.config?.baseURL || '/api/v1'}${reqUrl.startsWith('/') ? reqUrl : '/' + reqUrl}`;
    const reason = httpStatus === 404 ? 'Hormuud endpoint was not found.' : (err.response?.data?.detail || err.message || 'Connection request failed.');
    const displayMsg = httpStatus === 404
      ? `Connection failed. HTTP Status: 404. Endpoint: ${endpoint}. Reason: ${reason}`
      : `Connection failed: ${err.message || 'Unable to connect to backend service.'}`;
    
    showError(displayMsg);
    connectionTestResult.value = {
      success: false,
      status: 'UNAVAILABLE',
      message: displayMsg,
      http_status: httpStatus,
      endpoint: endpoint,
      reason: reason,
      response_time_ms: 0,
      checked_at: new Date().toISOString(),
    };
  } finally {
    isTestingConnection.value = false;
  }
}

async function handleCheckHormuudBalance() {
  isCheckingBalance.value = true;
  try {
    const res = await notificationService.getHormuudBalance();
    hormuudBalanceInfo.value = res;
    if (res.success && res.balance !== null) {
      showSuccess(`Current SMS Balance: ${res.balance}`);
    } else {
      showError(res.message || 'Unable to retrieve SMS balance.');
    }
  } catch (err: any) {
    showError(err.message || 'Failed to check balance.');
  } finally {
    isCheckingBalance.value = false;
  }
}

// Settings Actions
async function saveSettings() {
  try {
    await store.updateSettings(settingsForm);
    showSuccess('Notification settings updated in PostgreSQL.');
  } catch (err: any) {
    showError(err.message || 'Failed to save settings.');
  }
}

// Manual Send Actions
async function submitManualSend() {
  try {
    if (sendMode.value === 'SINGLE') {
      if (!singleForm.student_id) {
        showError('Please select a student recipient.');
        return;
      }
      if (!singleForm.title.trim() || !singleForm.message.trim()) {
        showError('Title and message cannot be empty.');
        return;
      }
      const res = await store.sendSingleNotification(singleForm);
      showSuccess(`Notification dispatched for ${res.student_name || 'student'}. Status: ${res.status}`);
      activeMainTab.value = 'HISTORY';
      loadHistory(1);
    } else {
      bulkForm.target_type = sendMode.value === 'CLASS' ? 'CLASS' : sendMode.value === 'SELECTED' ? 'SELECTED_STUDENTS' : 'ALL_ACTIVE';
      if (bulkForm.target_type === 'CLASS' && !bulkForm.class_id) {
        showError('Please select a target class.');
        return;
      }
      if (bulkForm.target_type === 'SELECTED_STUDENTS' && (!bulkForm.student_ids || bulkForm.student_ids.length === 0)) {
        showError('Please select at least one student.');
        return;
      }
      if (!bulkForm.title.trim() || !bulkForm.message.trim()) {
        showError('Title and message cannot be empty.');
        return;
      }
      const res = await store.sendBulkNotifications(bulkForm);
      showSuccess(res.message);
      activeMainTab.value = 'HISTORY';
      loadHistory(1);
    }
  } catch (err: any) {
    showError(err.message || 'Failed to dispatch manual notification.');
  }
}

// Helpers
function formatDate(dtStr?: string | null): string {
  if (!dtStr) return '—';
  const d = new Date(dtStr);
  return d.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function getStatusBadgeClass(status: NotificationStatus): string {
  switch (status) {
    case 'DELIVERED':
    case 'READ':
      return 'status-delivered';
    case 'SENT':
      return 'status-sent';
    case 'PENDING':
    case 'QUEUED':
      return 'status-pending';
    case 'FAILED':
      return 'status-failed';
    case 'NOT_CONFIGURED':
    case 'NOT_SENT':
      return 'status-unconfigured';
    default:
      return 'status-default';
  }
}

function getTypeBadgeLabel(type: NotificationType): string {
  switch (type) {
    case 'ATTENDANCE_ABSENT':
      return 'Attendance Alert';
    case 'RESULT_RELEASED':
      return 'Exam Results';
    case 'FEE_REMINDER':
      return 'Fee Reminder';
    case 'GENERAL_ANNOUNCEMENT':
      return 'General Notice';
    case 'CUSTOM':
      return 'Custom Notice';
    default:
      return type;
  }
}

async function handleRetryNotification(item: NotificationItem) {
  try {
    const updated = await store.retryNotification(item.id);
    showSuccess(`Notification #${item.id} retried. New status: ${updated.status}`);
  } catch (err: any) {
    showError(err.message || `Failed to retry notification #${item.id}`);
  }
}

async function handleRetryAllFailed() {
  if (!confirm('Are you sure you want to retry all failed/unconfigured notifications?')) return;
  try {
    const res = await store.retryAllFailed();
    showSuccess(res.message);
  } catch (err: any) {
    showError(err.message || 'Failed to retry failed notifications.');
  }
}

function openDetailModal(item: NotificationItem) {
  activeDetailNotification.value = item;
  isDetailModalOpen.value = true;
}

// Lifecycle and Tab Watcher
onMounted(async () => {
  await loadInitialData();
  await loadAttendanceAlerts();
  await loadResultAlerts();
  await loadHistory(1);
});

watch(activeMainTab, (tab) => {
  if (tab === 'ATTENDANCE_ALERTS') loadAttendanceAlerts();
  else if (tab === 'RESULT_NOTIFICATIONS') loadResultAlerts();
  else if (tab === 'HISTORY') loadHistory(1);
  else if (tab === 'OVERVIEW') store.fetchCounters();
  else if (tab === 'SEND') {
    if (availableClasses.value.length === 0 || availableStudents.value.length === 0) {
      loadDropdowns();
    }
  }
});

watch(attendanceDate, () => {
  if (activeMainTab.value === 'ATTENDANCE_ALERTS') {
    loadAttendanceAlerts();
  }
});

watch(resultAcademicYear, () => {
  if (activeMainTab.value === 'RESULT_NOTIFICATIONS') {
    loadResultAlerts();
  }
});
</script>

<template>
  <div class="notifications-page">
    <!-- Feedback Alerts -->
    <div v-if="successMessage" class="alert-banner alert-success">
      <svg class="alert-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
      </svg>
      <span>{{ successMessage }}</span>
      <button class="alert-close" @click="successMessage = ''">&times;</button>
    </div>

    <div v-if="errorMessage" class="alert-banner alert-danger">
      <svg class="alert-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span>{{ errorMessage }}</span>
      <button class="alert-close" @click="errorMessage = ''">&times;</button>
    </div>

    <!-- Header Section -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-title-row">
          <div class="header-icon-wrap">
            <svg class="header-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
          </div>
          <div>
            <h1 class="page-title">Guardian Communication & Alerts</h1>
            <p class="page-subtitle">
              Automated attendance absence notifications, exam result releases, Somali SMS templates, and audit logs.
            </p>
          </div>
        </div>
      </div>

      <div class="header-actions">
        <button
          type="button"
          class="btn btn-secondary"
          :disabled="store.isLoading"
          @click="loadInitialData()"
        >
          <svg class="btn-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>Refresh</span>
        </button>

        <button
          type="button"
          class="btn btn-primary"
          @click="activeMainTab = 'SEND'"
        >
          <svg class="btn-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
          <span>New Notification</span>
        </button>
      </div>
    </div>

    <!-- Navigation Sub-Tabs -->
    <div class="main-subtabs">
      <button
        type="button"
        class="nav-tab-btn"
        :class="{ active: activeMainTab === 'OVERVIEW' }"
        @click="activeMainTab = 'OVERVIEW'"
      >
        <svg class="tab-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
        </svg>
        <span>Overview</span>
      </button>

      <button
        type="button"
        class="nav-tab-btn"
        :class="{ active: activeMainTab === 'ATTENDANCE_ALERTS' }"
        @click="activeMainTab = 'ATTENDANCE_ALERTS'"
      >
        <svg class="tab-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>Attendance Alerts</span>
        <span v-if="(store.counters?.absent_pending_notify_count ?? 0) > 0" class="badge-counter-alert">
          {{ store.counters?.absent_pending_notify_count }} New
        </span>
      </button>

      <button
        type="button"
        class="nav-tab-btn"
        :class="{ active: activeMainTab === 'RESULT_NOTIFICATIONS' }"
        @click="activeMainTab = 'RESULT_NOTIFICATIONS'"
      >
        <svg class="tab-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <span>Result Notifications</span>
        <span v-if="(store.counters?.released_results_pending_notify_count ?? 0) > 0" class="badge-counter-alert">
          {{ store.counters?.released_results_pending_notify_count }} New
        </span>
      </button>

      <button
        type="button"
        class="nav-tab-btn"
        :class="{ active: activeMainTab === 'SEND' }"
        @click="activeMainTab = 'SEND'"
      >
        <svg class="tab-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
        </svg>
        <span>Send Notification</span>
      </button>

      <button
        type="button"
        class="nav-tab-btn"
        :class="{ active: activeMainTab === 'HISTORY' }"
        @click="activeMainTab = 'HISTORY'"
      >
        <svg class="tab-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>History</span>
      </button>

      <button
        type="button"
        class="nav-tab-btn"
        :class="{ active: activeMainTab === 'TEMPLATES' }"
        @click="activeMainTab = 'TEMPLATES'"
      >
        <svg class="tab-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
        <span>Templates</span>
      </button>

      <button
        type="button"
        class="nav-tab-btn"
        :class="{ active: activeMainTab === 'SETTINGS' }"
        @click="activeMainTab = 'SETTINGS'"
      >
        <svg class="tab-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <span>Settings</span>
      </button>
    </div>

    <!-- TAB 1: OVERVIEW -->
    <div v-if="activeMainTab === 'OVERVIEW'" class="tab-content">
      <!-- Operational Metric Cards -->
      <div class="metrics-grid">
        <div class="metric-card" @click="activeMainTab = 'ATTENDANCE_ALERTS'" style="cursor: pointer;">
          <div class="metric-info">
            <span class="metric-label">Absent Students Today</span>
            <span class="metric-value">{{ store.counters?.absent_today_count ?? 0 }}</span>
            <span class="metric-subtext">{{ store.counters?.absent_pending_notify_count ?? 0 }} pending guardian alert</span>
          </div>
          <div class="metric-badge warning">Attendance</div>
        </div>

        <div class="metric-card" @click="activeMainTab = 'RESULT_NOTIFICATIONS'" style="cursor: pointer;">
          <div class="metric-info">
            <span class="metric-label">Unnotified Released Results</span>
            <span class="metric-value text-indigo">{{ store.counters?.released_results_pending_notify_count ?? 0 }}</span>
            <span class="metric-subtext">Awaiting guardian dispatch</span>
          </div>
          <div class="metric-badge primary">Results</div>
        </div>

        <div class="metric-card">
          <div class="metric-info">
            <span class="metric-label">Delivered Today</span>
            <span class="metric-value text-emerald">{{ store.counters?.today_sent_count ?? 0 }}</span>
            <span class="metric-subtext">Across SMS & In-App</span>
          </div>
          <div class="metric-badge success">Dispatched</div>
        </div>

        <div class="metric-card" @click="activeMainTab = 'HISTORY'" style="cursor: pointer;">
          <div class="metric-info">
            <span class="metric-label">Missing Contacts</span>
            <span class="metric-value text-rose">{{ store.counters?.missing_contacts_count ?? 0 }}</span>
            <span class="metric-subtext">Guardians with no phone</span>
          </div>
          <div class="metric-badge danger">Action Needed</div>
        </div>
      </div>

      <!-- Quick Action Cards Grid -->
      <div class="overview-grid">
        <div class="overview-panel">
          <div class="panel-header">
            <h3>Attendance Absence Communications</h3>
            <span class="panel-tag">Somali SMS Automated</span>
          </div>
          <p class="panel-desc">
            Instantly alert parents when their child is recorded absent in today's attendance roster.
            The system resolves Somali guardian names, student names, and school information dynamically.
          </p>
          <div class="panel-actions">
            <button type="button" class="btn btn-primary" @click="activeMainTab = 'ATTENDANCE_ALERTS'">
              Open Attendance Alerts
            </button>
          </div>
        </div>

        <div class="overview-panel">
          <div class="panel-header">
            <h3>Exam Result Broadcasts</h3>
            <span class="panel-tag">Portal Ready</span>
          </div>
          <p class="panel-desc">
            Only officially released results are eligible. Send personalized notices directing guardians to check the Student Portal securely.
          </p>
          <div class="panel-actions">
            <button type="button" class="btn btn-secondary" @click="activeMainTab = 'RESULT_NOTIFICATIONS'">
              Review Released Results
            </button>
          </div>
        </div>
      </div>

      <!-- Gateway Status Summary -->
      <div class="card channel-status-card">
        <div class="card-header-clean">
          <h3 class="card-clean-title">Live Provider Channels</h3>
          <span class="card-clean-subtitle">PostgreSQL & SMS Gateway Integration Status</span>
        </div>
        <div class="channel-list-grid">
          <div v-for="ch in store.channelConfigs" :key="ch.channel" class="channel-status-item">
            <div class="ch-left">
              <span class="ch-indicator" :class="ch.is_configured ? 'online' : 'unconfigured'" />
              <div>
                <div class="ch-name">{{ ch.name }}</div>
                <div class="ch-details">{{ ch.details }}</div>
              </div>
            </div>
            <span class="ch-badge" :class="ch.is_configured ? 'configured' : 'unconfigured'">
              {{ ch.status_label }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: ATTENDANCE ALERTS -->
    <div v-if="activeMainTab === 'ATTENDANCE_ALERTS'" class="tab-content">
      <!-- Top Action Control Bar -->
      <div class="alerts-control-bar">
        <div class="control-left">
          <div class="control-date-wrap">
            <label class="control-label">Attendance Date:</label>
            <input v-model="attendanceDate" type="date" class="date-input" />
          </div>

          <div class="selection-summary" v-if="store.attendanceAlerts">
            <span class="summary-pill">
              <strong>{{ store.attendanceAlerts.total_absent_students }}</strong> Total Absent
            </span>
            <span class="summary-pill pending">
              <strong>{{ store.attendanceAlerts.total_pending_notification }}</strong> Pending
            </span>
            <span class="summary-pill missing">
              <strong>{{ store.attendanceAlerts.total_missing_contact }}</strong> Missing Contact
            </span>
            <span class="summary-pill notified">
              <strong>{{ store.attendanceAlerts.total_already_notified }}</strong> Notified
            </span>
          </div>
        </div>

        <div class="control-right">
          <button
            v-if="selectedAttendanceStudentIds.length > 0"
            type="button"
            class="btn btn-secondary btn-sm"
            @click="clearAllAttendanceSelection"
          >
            Clear Selected ({{ selectedAttendanceStudentIds.length }})
          </button>

          <button
            type="button"
            class="btn btn-secondary btn-sm"
            @click="selectAllAbsentStudents"
          >
            Select All Absent
          </button>

          <button
            v-if="selectedAttendanceStudentIds.length > 0"
            type="button"
            class="btn btn-primary"
            :disabled="store.isActionLoading"
            @click="openAttendanceSelectedPreview"
          >
            Notify Selected ({{ selectedAttendanceStudentIds.length }})
          </button>

          <button
            type="button"
            class="btn btn-primary-highlight"
            :disabled="store.isActionLoading || (store.attendanceAlerts?.total_pending_notification ?? 0) === 0"
            @click="openAttendanceBulkPreview()"
          >
            Notify ALL Absent Guardians
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!store.isLoading && (!store.attendanceAlerts || store.attendanceAlerts.classes.length === 0)" class="empty-state">
        <div class="empty-icon-wrap">
          <svg class="empty-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3>No Attendance Alerts Today</h3>
        <p>There are no students marked absent for {{ attendanceDate }}.</p>
      </div>

      <!-- Class Grouping Accordions -->
      <div v-else class="class-groups-container">
        <div
          v-for="cGroup in store.attendanceAlerts?.classes"
          :key="cGroup.class_id"
          class="class-group-card"
        >
          <!-- Class Header -->
          <div class="class-group-header" @click="toggleAttendanceClassExpand(cGroup.class_id)">
            <div class="class-title-left">
              <button
                type="button"
                class="btn-expand"
                :class="{ rotated: expandedAttendanceClasses[cGroup.class_id] }"
              >
                ▼
              </button>
              <h3 class="class-name">{{ cGroup.class_name }}</h3>
              <span class="badge-count">{{ cGroup.total_absent }} Absent</span>
              <span v-if="cGroup.pending_count > 0" class="badge-pending-tag">{{ cGroup.pending_count }} Pending</span>
            </div>

            <div class="class-header-actions" @click.stop>
              <button
                type="button"
                class="btn btn-secondary btn-xs"
                @click="toggleSelectAllClass(cGroup)"
              >
                {{ isClassAllSelected(cGroup) ? 'Deselect Class' : 'Select Class' }}
              </button>
              <button
                type="button"
                class="btn btn-primary btn-xs"
                :disabled="cGroup.pending_count === 0"
                @click="openAttendanceBulkPreview(cGroup.class_id)"
              >
                Notify Class Guardians
              </button>
            </div>
          </div>

          <!-- Class Absent Students List (Collapsible) -->
          <div v-if="expandedAttendanceClasses[cGroup.class_id]" class="class-students-list">
            <div
              v-for="s in cGroup.students"
              :key="s.student_id"
              class="student-alert-item"
              :class="{ selected: isStudentSelected(s.student_id) }"
              @click="toggleStudentSelection(s.student_id)"
            >
              <div class="checkbox-col" @click.stop>
                <input
                  type="checkbox"
                  :checked="isStudentSelected(s.student_id)"
                  @change="toggleStudentSelection(s.student_id)"
                />
              </div>

              <div class="student-info-col">
                <div class="student-name">{{ s.student_name }}</div>
                <div class="student-adm font-mono">{{ s.admission_number }}</div>
              </div>

              <div class="guardian-info-col">
                <div class="guardian-name">Guardian: <strong>{{ s.guardian_name || 'No Name' }}</strong></div>
                <div class="guardian-contact font-mono">
                  <span v-if="s.guardian_phone" class="phone-tag">{{ s.guardian_phone }}</span>
                  <span v-else class="missing-contact-tag">MISSING CONTACT</span>
                </div>
              </div>

              <div class="status-col">
                <span v-if="s.is_already_notified" class="status-badge status-delivered">
                  Already Notified
                </span>
                <span v-else-if="!s.has_valid_contact" class="status-badge status-unconfigured">
                  Not Sent (No Phone)
                </span>
                <span v-else class="status-badge status-pending">
                  Ready to Notify
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 3: RESULT NOTIFICATIONS -->
    <div v-if="activeMainTab === 'RESULT_NOTIFICATIONS'" class="tab-content">
      <!-- Result Control Bar -->
      <div class="alerts-control-bar">
        <div class="control-left">
          <div class="control-date-wrap">
            <label class="control-label">Academic Year:</label>
            <input v-model="resultAcademicYear" type="text" class="date-input" placeholder="2026/2027" />
          </div>

          <div class="selection-summary" v-if="store.resultAlerts">
            <span class="summary-pill">
              <strong>{{ store.resultAlerts.total_unnotified_results }}</strong> Unnotified Released Results
            </span>
          </div>
        </div>

        <div class="control-right">
          <button
            v-if="selectedResultStudentIds.length > 0"
            type="button"
            class="btn btn-secondary btn-sm"
            @click="selectedResultStudentIds = []"
          >
            Clear Selected ({{ selectedResultStudentIds.length }})
          </button>

          <button
            v-if="selectedResultStudentIds.length > 0"
            type="button"
            class="btn btn-primary"
            :disabled="store.isActionLoading"
            @click="openResultSelectedPreview(store.resultAlerts?.groups[0]?.release_batch_id || 0)"
          >
            Notify Selected ({{ selectedResultStudentIds.length }})
          </button>

          <button
            type="button"
            class="btn btn-primary-highlight"
            :disabled="store.isActionLoading || (store.resultAlerts?.total_unnotified_results ?? 0) === 0"
            @click="openResultBulkPreview()"
          >
            Notify ALL Released Result Guardians
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!store.isLoading && (!store.resultAlerts || store.resultAlerts.groups.length === 0)" class="empty-state">
        <div class="empty-icon-wrap">
          <svg class="empty-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3>All Released Results Communicated</h3>
        <p>All released results have been communicated to eligible guardians, or no results have been released yet.</p>
      </div>

      <!-- Results Groups -->
      <div v-else class="class-groups-container">
        <div
          v-for="rGroup in store.resultAlerts?.groups"
          :key="`${rGroup.release_batch_id}-${rGroup.class_id}`"
          class="class-group-card"
        >
          <div class="class-group-header">
            <div class="class-title-left">
              <div>
                <h3 class="class-name">{{ rGroup.exam_name }} — {{ rGroup.class_name }}</h3>
                <div class="cell-sub font-mono">Academic Year: {{ rGroup.academic_year }} | Released: {{ formatDate(rGroup.released_at) }}</div>
              </div>
              <span class="badge-count">{{ rGroup.pending_notification_count }} Pending Guardian Alert</span>
            </div>

            <div class="class-header-actions">
              <button
                type="button"
                class="btn btn-secondary btn-xs"
                @click="toggleSelectAllResultGroup(rGroup)"
              >
                {{ isResultGroupAllSelected(rGroup) ? 'Deselect Batch' : 'Select Batch' }}
              </button>
              <button
                type="button"
                class="btn btn-primary btn-xs"
                @click="openResultBulkPreview(rGroup.release_batch_id, rGroup.class_id)"
              >
                Notify Batch Guardians
              </button>
            </div>
          </div>

          <div class="class-students-list">
            <div
              v-for="s in rGroup.students"
              :key="s.student_id"
              class="student-alert-item"
              :class="{ selected: isResultStudentSelected(s.student_id) }"
              @click="toggleResultStudentSelection(s.student_id)"
            >
              <div class="checkbox-col" @click.stop>
                <input
                  type="checkbox"
                  :checked="isResultStudentSelected(s.student_id)"
                  @change="toggleResultStudentSelection(s.student_id)"
                />
              </div>

              <div class="student-info-col">
                <div class="student-name">{{ s.student_name }}</div>
                <div class="student-adm font-mono">{{ s.admission_number }}</div>
              </div>

              <div class="guardian-info-col">
                <div class="guardian-name">Guardian: <strong>{{ s.guardian_name || 'No Name' }}</strong></div>
                <div class="guardian-contact font-mono">
                  <span v-if="s.guardian_phone" class="phone-tag">{{ s.guardian_phone }}</span>
                  <span v-else class="missing-contact-tag">MISSING CONTACT</span>
                </div>
              </div>

              <div class="status-col">
                <span v-if="s.is_already_notified" class="status-badge status-delivered">
                  Already Notified
                </span>
                <span v-else-if="!s.has_valid_contact" class="status-badge status-unconfigured">
                  Missing Phone
                </span>
                <span v-else class="status-badge status-pending">
                  Ready
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 4: SEND NOTIFICATION (Manual / Custom) -->
    <div v-if="activeMainTab === 'SEND'" class="tab-content">
      <div class="send-wizard-card">
        <div class="wizard-header">
          <h2 class="wizard-title">Compose Direct Guardian Notification</h2>
          <p class="wizard-desc">
            The backend dynamically resolves guardian contacts and names directly from PostgreSQL.
          </p>
        </div>

        <div class="mode-tabs">
          <button
            type="button"
            class="mode-tab-btn"
            :class="{ active: sendMode === 'SINGLE' }"
            @click="sendMode = 'SINGLE'"
          >
            Single Student Guardian
          </button>
          <button
            type="button"
            class="mode-tab-btn"
            :class="{ active: sendMode === 'CLASS' }"
            @click="sendMode = 'CLASS'"
          >
            Entire Class
          </button>
          <button
            type="button"
            class="mode-tab-btn"
            :class="{ active: sendMode === 'SELECTED' }"
            @click="sendMode = 'SELECTED'"
          >
            Selected Students
          </button>
          <button
            type="button"
            class="mode-tab-btn"
            :class="{ active: sendMode === 'ALL' }"
            @click="sendMode = 'ALL'"
          >
            All Active Students
          </button>
        </div>

        <!-- Target Choosers -->
        <div v-if="sendMode === 'SINGLE'" class="form-group">
          <label class="form-label">Select Student *</label>
          <select v-model="singleForm.student_id" class="form-select">
            <option :value="0" disabled>-- Choose Active Student --</option>
            <option v-for="s in availableStudents" :key="s.id" :value="s.id">
              {{ s.full_name }} ({{ s.admission_number }}) - Guardian: {{ s.guardian_name || 'N/A' }}
            </option>
          </select>

          <!-- Resolved Guardian Info Box -->
          <div v-if="selectedSingleStudentPreview" class="guardian-preview-card">
            <div class="preview-title">PostgreSQL Resolved Guardian Relationship</div>
            <div class="preview-row">
              <span><strong>Guardian:</strong> {{ selectedSingleStudentPreview.guardian_name || 'Not on file' }}</span>
              <span><strong>Phone:</strong> {{ selectedSingleStudentPreview.guardian_phone || 'MISSING PHONE' }}</span>
              <span><strong>Class:</strong> {{ selectedSingleStudentPreview.current_class?.name || 'N/A' }}</span>
            </div>
          </div>
        </div>

        <div v-else-if="sendMode === 'CLASS'" class="form-group">
          <label class="form-label">Select Target Class *</label>
          <select v-model="bulkForm.class_id" class="form-select">
            <option :value="undefined" disabled>-- Choose Class --</option>
            <option v-for="c in availableClasses" :key="c.id" :value="c.id">
              {{ c.name }} {{ c.code ? `(${c.code})` : '' }}
            </option>
          </select>
        </div>

        <!-- Template Shortcut Picker -->
        <div class="template-shortcuts">
          <span class="shortcut-label">Load Somali Template:</span>
          <button
            type="button"
            class="shortcut-btn"
            :class="{ 'shortcut-active': (sendMode === 'SINGLE' ? singleForm.notification_type : bulkForm.notification_type) === 'ATTENDANCE_ABSENT' }"
            @click="onNotificationTypeChange('ATTENDANCE_ABSENT')"
          >
            Attendance Absence
          </button>
          <button
            type="button"
            class="shortcut-btn"
            :class="{ 'shortcut-active': (sendMode === 'SINGLE' ? singleForm.notification_type : bulkForm.notification_type) === 'RESULT_RELEASED' }"
            @click="onNotificationTypeChange('RESULT_RELEASED')"
          >
            Exam Results
          </button>
          <button
            type="button"
            class="shortcut-btn"
            :class="{ 'shortcut-active': (sendMode === 'SINGLE' ? singleForm.notification_type : bulkForm.notification_type) === 'FEE_REMINDER' }"
            @click="onNotificationTypeChange('FEE_REMINDER')"
          >
            Fee Reminder
          </button>
          <button
            type="button"
            class="shortcut-btn"
            :class="{ 'shortcut-active': (sendMode === 'SINGLE' ? singleForm.notification_type : bulkForm.notification_type) === 'GENERAL_ANNOUNCEMENT' }"
            @click="onNotificationTypeChange('GENERAL_ANNOUNCEMENT')"
          >
            General Notice
          </button>
          <button
            type="button"
            class="shortcut-btn custom-btn"
            :class="{ 'shortcut-active': (sendMode === 'SINGLE' ? singleForm.notification_type : bulkForm.notification_type) === 'CUSTOM' }"
            @click="onNotificationTypeChange('CUSTOM')"
          >
            Custom Message
          </button>
        </div>

        <!-- Channel & Type -->
        <div class="form-grid-2">
          <div class="form-group">
            <label class="form-label">Notification Type *</label>
            <select
              v-if="sendMode === 'SINGLE'"
              :value="singleForm.notification_type"
              class="form-select"
              @change="onNotificationTypeChange(($event.target as HTMLSelectElement).value)"
            >
              <option value="ATTENDANCE_ABSENT">Attendance Absence</option>
              <option value="RESULT_RELEASED">Exam Result Released</option>
              <option value="FEE_REMINDER">Fee Reminder</option>
              <option value="GENERAL_ANNOUNCEMENT">General Notice</option>
              <option value="CUSTOM">Custom Notification</option>
            </select>
            <select
              v-else
              :value="bulkForm.notification_type"
              class="form-select"
              @change="onNotificationTypeChange(($event.target as HTMLSelectElement).value)"
            >
              <option value="ATTENDANCE_ABSENT">Attendance Absence</option>
              <option value="RESULT_RELEASED">Exam Result Released</option>
              <option value="FEE_REMINDER">Fee Reminder</option>
              <option value="GENERAL_ANNOUNCEMENT">General Notice</option>
              <option value="CUSTOM">Custom Notification</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Delivery Channel</label>
            <select
              v-if="sendMode === 'SINGLE'"
              v-model="singleForm.channel"
              class="form-select"
            >
              <option value="SMS">SMS Gateway</option>
              <option value="EMAIL">Email</option>
              <option value="IN_APP">Portal In-App</option>
            </select>
            <select
              v-else
              v-model="bulkForm.channel"
              class="form-select"
            >
              <option value="SMS">SMS Gateway</option>
              <option value="EMAIL">Email</option>
              <option value="IN_APP">Portal In-App</option>
            </select>
          </div>
        </div>

        <!-- Title & Message -->
        <div class="form-group">
          <label class="form-label">Message Title *</label>
          <input
            v-if="sendMode === 'SINGLE'"
            v-model="singleForm.title"
            type="text"
            class="form-input"
            placeholder="e.g., Ogeysiis Maqnaansho - {{student_name}}"
          />
          <input
            v-else
            v-model="bulkForm.title"
            type="text"
            class="form-input"
            placeholder="e.g., Ogeysiis Maqnaansho - {{student_name}}"
          />
        </div>

        <!-- Somali Message Textarea with required header and sub-label -->
        <div class="form-group">
          <label class="form-label font-bold text-slate-800">Fariinta Ogeysiiska</label>
          <p class="form-sub-label">
            Fariintan waa template-ka la isticmaali doono. Magaca ardayga iyo guardian-ka waxaa si automatic ah looga soo qaadan doonaa database-ka marka fariinta la diro.
          </p>
          <textarea
            v-if="sendMode === 'SINGLE'"
            v-model="singleForm.message"
            rows="4"
            class="form-textarea"
            placeholder="Qor ama dooro nooca ogeysiiska si aad template-ka u hesho..."
          />
          <textarea
            v-else
            v-model="bulkForm.message"
            rows="4"
            class="form-textarea"
            placeholder="Qor ama dooro nooca ogeysiiska si aad template-ka u hesho..."
          />

          <!-- Template Variables UI Chips -->
          <div class="available-variables-container">
            <div class="var-header">
              <span class="var-title">Available variables:</span>
              <span class="var-hint">(Guji si aad ugu darto fariinta)</span>
            </div>
            <div class="var-chips-grid">
              <button
                v-for="v in currentActiveVariables"
                :key="v"
                type="button"
                class="var-chip-btn"
                :title="`Click to insert ${v}`"
                @click="insertVariable(v)"
              >
                <code>{{ v }}</code>
              </button>
            </div>
          </div>

          <!-- Live Database Personalization Preview for Single Mode -->
          <div v-if="sendMode === 'SINGLE' && selectedSingleStudentPreview && singleForm.message" class="live-rendered-preview-box">
            <div class="live-preview-header">
              <span class="live-preview-badge">Live Database Personalization Preview</span>
              <span class="live-preview-recipient">
                To: <strong>{{ selectedSingleStudentPreview.guardian_name || 'Waalidka' }}</strong> ({{ selectedSingleStudentPreview.guardian_phone || 'No phone' }})
              </span>
            </div>
            <div class="live-preview-content font-mono">
              "{{ renderedSinglePreviewMessage }}"
            </div>
          </div>
        </div>

        <div class="wizard-actions">
          <button
            type="button"
            class="btn btn-primary btn-lg"
            :disabled="store.isActionLoading"
            @click="submitManualSend"
          >
            <span>{{ store.isActionLoading ? 'Dispatching...' : 'Send Notification' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- TAB 5: HISTORY -->
    <div v-if="activeMainTab === 'HISTORY'" class="tab-content">
      <!-- Toolbar Filters -->
      <div class="toolbar-card">
        <div class="filters-row">
          <div class="search-wrap">
            <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              v-model="historySearchQuery"
              type="text"
              class="search-input"
              placeholder="Search by student, guardian, phone or title..."
              @input="onSearchInput"
            />
          </div>

          <select v-model="historyStatusFilter" class="select-input" @change="loadHistory(1)">
            <option value="ALL">All Statuses</option>
            <option value="PENDING">Pending</option>
            <option value="SENT">Sent</option>
            <option value="DELIVERED">Delivered</option>
            <option value="FAILED">Failed</option>
            <option value="NOT_CONFIGURED">Not Configured</option>
            <option value="NOT_SENT">Missing Contact (Not Sent)</option>
          </select>

          <select v-model="historyTypeFilter" class="select-input" @change="loadHistory(1)">
            <option value="ALL">All Notification Types</option>
            <option value="ATTENDANCE_ABSENT">Attendance Absence</option>
            <option value="RESULT_RELEASED">Exam Results</option>
            <option value="GENERAL_ANNOUNCEMENT">General Announcement</option>
            <option value="FEE_REMINDER">Fee Reminder</option>
          </select>

          <select v-model="historyChannelFilter" class="select-input" @change="loadHistory(1)">
            <option value="ALL">All Channels</option>
            <option value="SMS">SMS Gateway</option>
            <option value="EMAIL">Email</option>
            <option value="IN_APP">In-App</option>
          </select>

          <button
            v-if="store.stats && (store.stats.failed_count > 0 || store.stats.not_configured_count > 0)"
            type="button"
            class="btn btn-warning btn-sm"
            @click="handleRetryAllFailed"
          >
            Retry Failed ({{ (store.stats.failed_count || 0) + (store.stats.not_configured_count || 0) }})
          </button>
        </div>
      </div>

      <!-- History Table Container -->
      <div class="table-container">
        <div v-if="store.isLoading" class="loading-state">
          <div class="spinner" />
          <span>Loading PostgreSQL communication history...</span>
        </div>

        <div v-else-if="store.notifications.length === 0" class="empty-state">
          <div class="empty-icon-wrap">
            <svg class="empty-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
            </svg>
          </div>
          <h3>No Notifications Found</h3>
          <p>No communications recorded with the current filters.</p>
        </div>

        <div v-else class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Student & Class</th>
                <th>Guardian / Recipient</th>
                <th>Type</th>
                <th>Channel</th>
                <th>Message Content</th>
                <th>Status</th>
                <th>Date & Time</th>
                <th class="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="n in store.notifications" :key="n.id">
                <td class="font-mono text-muted">#{{ n.id }}</td>
                <td>
                  <div class="cell-main">{{ n.student_name || '—' }}</div>
                  <div class="cell-sub font-mono">{{ n.student_admission_number || n.class_name || 'N/A' }}</div>
                </td>
                <td>
                  <div class="cell-main">{{ n.guardian_name || 'Guardian' }}</div>
                  <div class="cell-sub font-mono">{{ n.guardian_phone || n.guardian_email || 'No contact' }}</div>
                </td>
                <td>
                  <span class="type-pill">{{ getTypeBadgeLabel(n.notification_type) }}</span>
                </td>
                <td>
                  <span class="channel-tag">{{ n.channel }}</span>
                </td>
                <td class="message-preview-cell" :title="n.message">
                  <div class="message-title">{{ n.title }}</div>
                  <div class="message-snippet">{{ n.message }}</div>
                </td>
                <td>
                  <span class="status-badge" :class="getStatusBadgeClass(n.status)">
                    {{ n.status }}
                  </span>
                  <div v-if="n.failure_reason" class="failure-hint" :title="n.failure_reason">
                    {{ n.failure_reason }}
                  </div>
                </td>
                <td class="text-nowrap text-muted font-mono">
                  {{ formatDate(n.created_at) }}
                </td>
                <td class="text-right">
                  <div class="row-actions">
                    <button
                      type="button"
                      class="action-btn"
                      title="View Details & Timeline"
                      @click="openDetailModal(n)"
                    >
                      <svg class="action-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </button>

                    <button
                      v-if="n.status === 'FAILED' || n.status === 'NOT_CONFIGURED'"
                      type="button"
                      class="action-btn retry"
                      title="Retry Delivery"
                      @click="handleRetryNotification(n)"
                    >
                      <svg class="action-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="store.totalNotifications > 0" class="pagination-footer">
          <div class="pagination-info">
            Showing <strong>{{ (store.currentPage - 1) * store.pageSize + 1 }}</strong> to
            <strong>{{ Math.min(store.currentPage * store.pageSize, store.totalNotifications) }}</strong> of
            <strong>{{ store.totalNotifications }}</strong> records
          </div>

          <div class="pagination-controls">
            <button
              type="button"
              class="page-btn"
              :disabled="store.currentPage <= 1 || store.isLoading"
              @click="loadHistory(store.currentPage - 1)"
            >
              Previous
            </button>
            <span class="page-current">Page {{ store.currentPage }} of {{ store.totalPages }}</span>
            <button
              type="button"
              class="page-btn"
              :disabled="store.currentPage >= store.totalPages || store.isLoading"
              @click="loadHistory(store.currentPage + 1)"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 6: TEMPLATES -->
    <div v-if="activeMainTab === 'TEMPLATES'" class="tab-content">
      <div class="templates-grid">
        <div v-for="tmpl in store.templates" :key="tmpl.id" class="template-card">
          <div class="template-card-header">
            <div>
              <h3 class="template-name">{{ tmpl.name }}</h3>
              <span class="template-code font-mono">{{ tmpl.code }}</span>
            </div>
            <span class="template-category">{{ tmpl.category }}</span>
          </div>

          <!-- Read-only View -->
          <div v-if="editingTemplateCode !== tmpl.code" class="template-card-body">
            <div class="tmpl-row">
              <span class="tmpl-lbl">Title:</span>
              <span class="tmpl-val">{{ tmpl.title_template }}</span>
            </div>
            <div class="tmpl-row">
              <span class="tmpl-lbl">Somali / English Template:</span>
              <p class="tmpl-body-val font-mono">{{ tmpl.body_template }}</p>
            </div>
            <div class="tmpl-footer">
              <span class="tmpl-status" :class="tmpl.is_active ? 'active' : 'inactive'">
                {{ tmpl.is_active ? '● Active' : '○ Inactive' }}
              </span>
              <button type="button" class="btn btn-secondary btn-sm" @click="startEditTemplate(tmpl)">
                Edit Template
              </button>
            </div>
          </div>

          <!-- Edit Form View -->
          <div v-else class="template-edit-box">
            <div class="form-group">
              <label class="form-label">Title Template</label>
              <input v-model="templateEditForm.title_template" type="text" class="form-input" />
            </div>

            <div class="form-group">
              <label class="form-label">Body Template</label>
              <textarea v-model="templateEditForm.body_template" rows="4" class="form-textarea font-mono" />
              <span class="form-help">
                Supported: <code>&#123;&#123;guardian_name&#125;&#125;</code>, <code>&#123;&#123;student_name&#125;&#125;</code>, <code>&#123;&#123;class_name&#125;&#125;</code>, <code>&#123;&#123;date&#125;&#125;</code>, <code>&#123;&#123;fee_balance&#125;&#125;</code>, <code>&#123;&#123;school_name&#125;&#125;</code>, <code>&#123;&#123;exam_name&#125;&#125;</code>
              </span>
            </div>

            <div class="edit-actions">
              <button type="button" class="btn btn-secondary btn-sm" @click="cancelEditTemplate">
                Cancel
              </button>
              <button type="button" class="btn btn-primary btn-sm" :disabled="store.isActionLoading" @click="saveEditedTemplate">
                Save to PostgreSQL
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 7: SETTINGS -->
    <div v-if="activeMainTab === 'SETTINGS'" class="tab-content">
      <div class="settings-container-card">
        <h2 class="settings-title">Notification & Automated Triggers Settings</h2>
        <p class="settings-desc">
          Configure automated event hooks for attendance absence and exam result release transactions in PostgreSQL.
        </p>

        <form class="settings-form" @submit.prevent="saveSettings">
          <div class="setting-toggle-group">
            <div class="toggle-info">
              <label class="toggle-title">Automatic Attendance Absence Notifications</label>
              <p class="toggle-sub">
                Automatically generate and trigger SMS alerts to parents when a student is saved as ABSENT in attendance roster.
              </p>
            </div>
            <label class="switch">
              <input v-model="settingsForm.notify_attendance_absent_enabled" type="checkbox" />
              <span class="slider round" />
            </label>
          </div>

          <div class="setting-toggle-group">
            <div class="toggle-info">
              <label class="toggle-title">Automatic Result Release Notifications</label>
              <p class="toggle-sub">
                Automatically notify guardians when Admin approves and releases an exam result batch.
              </p>
            </div>
            <label class="switch">
              <input v-model="settingsForm.notify_result_release_enabled" type="checkbox" />
              <span class="slider round" />
            </label>
          </div>

          <div class="form-group">
            <label class="form-label">School Name in SMS Signature</label>
            <input v-model="settingsForm.school_name" type="text" class="form-input" />
          </div>

          <div class="form-group">
            <label class="form-label">SMS Sender ID</label>
            <input v-model="settingsForm.sms_sender_id" type="text" class="form-input font-mono" />
          </div>

          <div class="settings-save-row">
            <button type="submit" class="btn btn-primary" :disabled="store.isActionLoading">
              <span>{{ store.isActionLoading ? 'Saving...' : 'Save Settings' }}</span>
            </button>
          </div>
        </form>
      </div>

      <!-- Hormuud SMS Gateway Configuration & Health Card -->
      <div class="settings-container-card hormuud-gateway-card">
        <div class="hormuud-card-header">
          <div class="hormuud-title-group">
            <div class="hormuud-icon-badge">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
              </svg>
            </div>
            <div>
              <h2 class="settings-title">Hormuud SMS REST Gateway</h2>
              <p class="settings-desc">Official telecom REST API integration for automated & bulk school guardian communications.</p>
            </div>
          </div>

          <div class="hormuud-header-badges">
            <span
              class="provider-status-badge"
              :class="connectionTestResult?.status === 'CONNECTED' ? 'status-connected' : connectionTestResult?.status === 'AUTHENTICATION_ERROR' ? 'status-auth-error' : connectionTestResult?.status === 'UNAVAILABLE' ? 'status-unavailable' : 'status-not-configured'"
            >
              {{ connectionTestResult ? connectionTestResult.status : 'Hormuud Ready' }}
            </span>
          </div>
        </div>

        <div class="hormuud-meta-grid">
          <div class="meta-item">
            <span class="meta-label">GATEWAY BASE URL</span>
            <span class="meta-value font-mono">https://smsapi.hormuud.com/</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">SENDER ID</span>
            <span class="meta-value font-mono">{{ settingsForm.sms_sender_id || 'EMS' }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">TOKEN AUTHENTICATION</span>
            <span class="meta-value">Bearer OAuth2 (Server-Side Cached)</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">SMS BALANCE</span>
            <div class="meta-balance-row">
              <span class="meta-value font-mono font-bold text-indigo">
                {{ hormuudBalanceInfo?.balance !== undefined && hormuudBalanceInfo?.balance !== null ? hormuudBalanceInfo.balance : '—' }}
              </span>
              <button
                type="button"
                class="btn-icon-refresh"
                :disabled="isCheckingBalance"
                title="Check Live Balance"
                @click="handleCheckHormuudBalance"
              >
                <svg :class="{ 'spin-anim': isCheckingBalance }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Diagnostic Feedback Box -->
        <div v-if="connectionTestResult" class="diagnostic-box" :class="connectionTestResult.success ? 'diag-success' : 'diag-error'">
          <div class="diag-header">
            <strong>{{ connectionTestResult.success ? 'Connection Verified' : 'Connection Failed' }}</strong>
            <span class="diag-time font-mono">{{ connectionTestResult.response_time_ms }} ms</span>
          </div>

          <!-- Structured Diagnostic Details -->
          <div v-if="!connectionTestResult.success && (connectionTestResult.http_status || connectionTestResult.endpoint || connectionTestResult.reason)" class="diag-meta-details">
            <div v-if="connectionTestResult.http_status" class="diag-detail-row">
              <span class="diag-detail-label">HTTP Status:</span>
              <span class="diag-detail-val font-mono font-bold">{{ connectionTestResult.http_status }}</span>
            </div>
            <div v-if="connectionTestResult.endpoint" class="diag-detail-row">
              <span class="diag-detail-label">Endpoint:</span>
              <span class="diag-detail-val font-mono">{{ connectionTestResult.endpoint }}</span>
            </div>
            <div v-if="connectionTestResult.reason" class="diag-detail-row">
              <span class="diag-detail-label">Reason:</span>
              <span class="diag-detail-val">{{ connectionTestResult.reason }}</span>
            </div>
          </div>

          <p class="diag-msg">{{ connectionTestResult.message }}</p>
        </div>

        <div class="hormuud-actions-bar">
          <button
            type="button"
            class="btn btn-secondary"
            :disabled="isTestingConnection"
            @click="handleTestHormuudConnection"
          >
            <svg v-if="isTestingConnection" class="spin-anim" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67" />
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
            </svg>
            <span>{{ isTestingConnection ? 'Testing Connection...' : 'Test Hormuud Connection' }}</span>
          </button>

          <button
            type="button"
            class="btn btn-secondary"
            :disabled="isCheckingBalance"
            @click="handleCheckHormuudBalance"
          >
            <svg v-if="isCheckingBalance" class="spin-anim" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67" />
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="4" width="20" height="16" rx="2" />
              <line x1="12" y1="8" x2="12" y2="16" />
              <line x1="8" y1="12" x2="16" y2="12" />
            </svg>
            <span>{{ isCheckingBalance ? 'Checking Balance...' : 'Check SMS Balance' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- CONFIRMATION & LIVE MESSAGE PREVIEW MODAL -->
    <div v-if="isPreviewModalOpen" class="modal-backdrop" @click.self="isPreviewModalOpen = false">
      <div class="modal-box modal-lg">
        <div class="modal-header">
          <h3 class="modal-title">{{ previewModalTitle }}</h3>
          <button type="button" class="modal-close" @click="isPreviewModalOpen = false">&times;</button>
        </div>

        <div class="modal-body" v-if="previewData">
          <!-- Verification Summary Counters -->
          <div class="preview-stats-bar">
            <div class="p-stat">
              <span class="p-lbl">Total Students:</span>
              <span class="p-val font-mono">{{ previewData.total }}</span>
            </div>
            <div class="p-stat">
              <span class="p-lbl">Valid Contacts:</span>
              <span class="p-val font-mono text-emerald">{{ previewData.valid_contacts }}</span>
            </div>
            <div class="p-stat">
              <span class="p-lbl">Missing Contact:</span>
              <span class="p-val font-mono text-rose">{{ previewData.missing_contacts }}</span>
            </div>
            <div class="p-stat">
              <span class="p-lbl">Already Notified:</span>
              <span class="p-val font-mono text-amber">{{ previewData.already_notified }}</span>
            </div>
          </div>

          <!-- Live Carousel Preview of Dynamic Personalized Message -->
          <div v-if="currentSamplePreview" class="carousel-preview-card">
            <div class="carousel-header">
              <span class="carousel-title">
                Personalized Message Preview ({{ currentPreviewIndex + 1 }} of {{ previewData.sample_previews.length }})
              </span>
              <span class="font-mono text-xs">
                To: {{ currentSamplePreview.guardian_name }} ({{ currentSamplePreview.guardian_phone || 'NO PHONE' }})
              </span>
            </div>

            <div class="preview-target-details">
              <span><strong>Student:</strong> {{ currentSamplePreview.student_name }}</span>
              <span><strong>Class:</strong> {{ currentSamplePreview.class_name }}</span>
              <span v-if="currentSamplePreview.is_already_notified" class="text-amber font-semibold">
                ⚠️ Already Notified (Duplicate Protected)
              </span>
              <span v-else-if="!currentSamplePreview.has_valid_contact" class="text-rose font-semibold">
                ❌ Missing Contact (Will be recorded as NOT_SENT)
              </span>
              <span v-else class="text-emerald font-semibold">
                ✓ Ready for Delivery
              </span>
            </div>

            <!-- Rendered Dynamic Somali SMS -->
            <div class="sms-preview-screen">
              <div class="sms-bubble">
                {{ currentSamplePreview.rendered_message }}
              </div>
            </div>

            <!-- Carousel Controls -->
            <div class="carousel-controls">
              <button
                type="button"
                class="btn btn-secondary btn-xs"
                :disabled="currentPreviewIndex <= 0"
                @click="prevPreview"
              >
                ◀ Previous
              </button>
              <span class="carousel-pos font-mono">{{ currentPreviewIndex + 1 }} / {{ previewData.sample_previews.length }}</span>
              <button
                type="button"
                class="btn btn-secondary btn-xs"
                :disabled="currentPreviewIndex >= previewData.sample_previews.length - 1"
                @click="nextPreview"
              >
                Next ▶
              </button>
            </div>
          </div>

          <div v-else class="empty-preview-note">
            <p>No sample messages to display for the selected criteria.</p>
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="isPreviewModalOpen = false">
            Cancel
          </button>
          <button
            type="button"
            class="btn btn-primary"
            :disabled="isExecutingSend || (previewData?.valid_contacts ?? 0) === 0"
            @click="executeConfirmSend"
          >
            <span>{{ isExecutingSend ? 'Dispatching...' : 'Confirm & Send Notifications' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- NOTIFICATION DETAIL MODAL -->
    <div v-if="isDetailModalOpen && activeDetailNotification" class="modal-backdrop" @click.self="isDetailModalOpen = false">
      <div class="modal-box">
        <div class="modal-header">
          <h3 class="modal-title">Notification Audit Record #{{ activeDetailNotification.id }}</h3>
          <button type="button" class="modal-close" @click="isDetailModalOpen = false">&times;</button>
        </div>

        <div class="modal-body">
          <div class="detail-section">
            <div class="detail-row">
              <span class="detail-label">Status:</span>
              <span class="status-badge" :class="getStatusBadgeClass(activeDetailNotification.status)">
                {{ activeDetailNotification.status }}
              </span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Type:</span>
              <span class="type-pill">{{ getTypeBadgeLabel(activeDetailNotification.notification_type) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Student:</span>
              <span>{{ activeDetailNotification.student_name || 'N/A' }} ({{ activeDetailNotification.student_admission_number || '—' }})</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Guardian:</span>
              <span>{{ activeDetailNotification.guardian_name || 'Guardian' }} ({{ activeDetailNotification.guardian_phone || 'No phone' }})</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Idempotency Key:</span>
              <span class="font-mono text-xs">{{ activeDetailNotification.idempotency_key || 'N/A' }}</span>
            </div>
            <div v-if="activeDetailNotification.failure_reason" class="detail-row">
              <span class="detail-label text-rose">Failure / Reason:</span>
              <span class="text-rose font-mono">{{ activeDetailNotification.failure_reason }}</span>
            </div>
          </div>

          <div class="detail-message-box">
            <div class="msg-title">{{ activeDetailNotification.title }}</div>
            <p class="msg-content">{{ activeDetailNotification.message }}</p>
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="isDetailModalOpen = false">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Core Page Layout */
.notifications-page {
  padding: 1.5rem;
  max-width: 1600px;
  margin: 0 auto;
  min-height: 100vh;
  box-sizing: border-box;
  overflow-x: hidden;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.header-title-row {
  display: flex;
  align-items: center;
  gap: 0.875rem;
}

.header-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
}

.header-icon {
  width: 24px;
  height: 24px;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.page-subtitle {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0.25rem 0 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

/* Alert Banner */
.alert-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem 1.25rem;
  border-radius: 8px;
  margin-bottom: 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.alert-success {
  background-color: #ecfdf5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.alert-danger {
  background-color: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.alert-icon {
  width: 20px;
  height: 20px;
  margin-right: 0.5rem;
  flex-shrink: 0;
}

.alert-close {
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  color: inherit;
}

/* Navigation Sub-Tabs */
.main-subtabs {
  display: flex;
  gap: 0.5rem;
  border-bottom: 2px solid #e2e8f0;
  margin-bottom: 1.5rem;
  overflow-x: auto;
  padding-bottom: 2px;
}

.nav-tab-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
}

.nav-tab-btn:hover {
  color: #1e293b;
}

.nav-tab-btn.active {
  color: #2563eb;
  border-bottom-color: #2563eb;
}

.tab-svg {
  width: 18px;
  height: 18px;
}

.badge-counter-alert {
  padding: 0.15rem 0.45rem;
  background-color: #ef4444;
  color: #ffffff;
  border-radius: 9999px;
  font-size: 0.7rem;
  font-weight: 700;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.65; }
}

/* Metric Cards */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.metric-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.06);
}

.metric-info {
  display: flex;
  flex-direction: column;
}

.metric-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: #64748b;
  margin-bottom: 0.25rem;
}

.metric-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #0f172a;
}

.metric-subtext {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 0.25rem;
}

.metric-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
}

.metric-badge.primary { background: #eff6ff; color: #1d4ed8; }
.metric-badge.success { background: #ecfdf5; color: #047857; }
.metric-badge.warning { background: #fffbeb; color: #b45309; }
.metric-badge.danger { background: #fef2f2; color: #b91c1c; }

.text-emerald { color: #059669 !important; }
.text-indigo { color: #4f46e5 !important; }
.text-rose { color: #e11d48 !important; }
.text-amber { color: #d97706 !important; }

/* Control Bars & Toolbars */
.alerts-control-bar, .toolbar-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1rem 1.25rem;
  margin-bottom: 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.control-left, .control-right {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  flex-wrap: wrap;
}

.control-date-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.control-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #334155;
}

.date-input, .select-input, .search-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #0f172a;
  background: #fff;
  outline: none;
}

.date-input:focus, .select-input:focus, .search-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15);
}

.selection-summary {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.summary-pill {
  font-size: 0.75rem;
  padding: 0.25rem 0.6rem;
  border-radius: 9999px;
  background: #f1f5f9;
  color: #475569;
}

.summary-pill.pending { background: #fef3c7; color: #92400e; }
.summary-pill.missing { background: #fee2e2; color: #991b1b; }
.summary-pill.notified { background: #d1fae5; color: #065f46; }

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.btn-primary { background: #2563eb; color: #ffffff; }
.btn-primary:hover:not(:disabled) { background: #1d4ed8; }

.btn-primary-highlight {
  background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(37, 99, 235, 0.3);
}
.btn-primary-highlight:hover:not(:disabled) {
  background: linear-gradient(135deg, #1d4ed8 0%, #1e3a8a 100%);
}

.btn-secondary { background: #ffffff; border-color: #cbd5e1; color: #334155; }
.btn-secondary:hover:not(:disabled) { background: #f8fafc; border-color: #94a3b8; }

.btn-warning { background: #f59e0b; color: #ffffff; }
.btn-warning:hover:not(:disabled) { background: #d97706; }

.btn-sm { padding: 0.35rem 0.75rem; font-size: 0.8125rem; }
.btn-xs { padding: 0.25rem 0.5rem; font-size: 0.75rem; }
.btn-lg { padding: 0.75rem 1.5rem; font-size: 1rem; }

.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-icon { width: 16px; height: 16px; }

/* Class Grouping Accordions */
.class-groups-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.class-group-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.class-group-header {
  background: #f8fafc;
  padding: 0.875rem 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  border-bottom: 1px solid #e2e8f0;
  user-select: none;
}

.class-title-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-expand {
  background: none;
  border: none;
  font-size: 0.75rem;
  color: #64748b;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.btn-expand.rotated {
  transform: rotate(0deg);
}

.class-name {
  font-size: 1rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.badge-count {
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  border-radius: 9999px;
  background: #e2e8f0;
  color: #334155;
  font-weight: 600;
}

.badge-pending-tag {
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  border-radius: 9999px;
  background: #fef3c7;
  color: #92400e;
  font-weight: 600;
}

.class-header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Students List in Group */
.class-students-list {
  display: flex;
  flex-direction: column;
}

.student-alert-item {
  display: grid;
  grid-template-columns: 40px 1.5fr 2fr 1fr;
  align-items: center;
  padding: 0.75rem 1.25rem;
  border-bottom: 1px solid #f1f5f9;
  cursor: pointer;
  transition: background 0.15s ease;
}

.student-alert-item:last-child {
  border-bottom: none;
}

.student-alert-item:hover {
  background: #f8fafc;
}

.student-alert-item.selected {
  background: #eff6ff;
}

.student-name {
  font-weight: 600;
  color: #0f172a;
}

.student-adm {
  font-size: 0.75rem;
  color: #64748b;
}

.guardian-name {
  font-size: 0.875rem;
  color: #334155;
}

.phone-tag {
  font-size: 0.75rem;
  color: #0284c7;
  background: #e0f2fe;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.missing-contact-tag {
  font-size: 0.75rem;
  color: #b91c1c;
  background: #fee2e2;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  font-weight: 700;
}

/* Status Badges */
.status-badge {
  display: inline-block;
  padding: 0.25rem 0.6rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-delivered { background: #d1fae5; color: #065f46; }
.status-sent { background: #e0f2fe; color: #0369a1; }
.status-pending { background: #fef3c7; color: #92400e; }
.status-failed { background: #fee2e2; color: #991b1b; }
.status-unconfigured { background: #f1f5f9; color: #475569; }

.type-pill {
  font-size: 0.75rem;
  background: #ede9fe;
  color: #6d28d9;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-weight: 600;
}

.channel-tag {
  font-size: 0.75rem;
  background: #f1f5f9;
  color: #334155;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: monospace;
}

/* Tables */
.table-container {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.table-responsive {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.875rem;
}

.data-table th {
  background: #f8fafc;
  color: #475569;
  font-weight: 600;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.data-table td {
  padding: 0.875rem 1rem;
  border-bottom: 1px solid #f1f5f9;
  color: #1e293b;
  vertical-align: middle;
}

.message-preview-cell {
  max-width: 280px;
}

.message-title {
  font-weight: 600;
  color: #0f172a;
}

.message-snippet {
  font-size: 0.75rem;
  color: #64748b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.action-btn {
  background: none;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  padding: 0.35rem;
  color: #475569;
  cursor: pointer;
  margin-left: 0.25rem;
}

.action-btn:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.action-btn.retry:hover {
  background: #fef3c7;
  color: #b45309;
  border-color: #fcd34d;
}

.action-icon {
  width: 16px;
  height: 16px;
}

/* Pagination */
.pagination-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.875rem 1.25rem;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-btn {
  padding: 0.35rem 0.75rem;
  border: 1px solid #cbd5e1;
  background: #fff;
  border-radius: 4px;
  font-size: 0.8125rem;
  cursor: pointer;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Send Wizard & Forms */
.send-wizard-card, .settings-container-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1.5rem;
  max-width: 900px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.wizard-title, .settings-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.wizard-desc, .settings-desc {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0.25rem 0 1.25rem;
}

.mode-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
}

.mode-tab-btn {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  border: 1px solid #cbd5e1;
  background: #f8fafc;
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
}

.mode-tab-btn.active {
  background: #2563eb;
  color: #ffffff;
  border-color: #2563eb;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #334155;
  margin-bottom: 0.35rem;
}

.form-sub-label {
  font-size: 0.8125rem;
  color: #64748b;
  margin: 0 0 0.5rem 0;
  line-height: 1.4;
}

.form-input, .form-select, .form-textarea {
  width: 100%;
  padding: 0.6rem 0.875rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #0f172a;
  background: #fff;
  box-sizing: border-box;
}

.form-input:focus, .form-select:focus, .form-textarea:focus {
  border-color: #3b82f6;
  outline: none;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15);
}

.form-grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-help {
  display: block;
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 0.35rem;
}

.guardian-preview-card {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 6px;
  padding: 0.75rem 1rem;
  margin-top: 0.5rem;
}

.preview-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: #166534;
  margin-bottom: 0.25rem;
}

.preview-row {
  display: flex;
  gap: 1.5rem;
  font-size: 0.8125rem;
  color: #14532d;
  flex-wrap: wrap;
}

.template-shortcuts {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
}

.shortcut-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
}

.shortcut-btn {
  font-size: 0.75rem;
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  color: #334155;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.15s ease;
}

.shortcut-btn:hover {
  background: #eff6ff;
  border-color: #93c5fd;
  color: #1d4ed8;
}

.shortcut-btn.shortcut-active {
  background: #eff6ff;
  border-color: #3b82f6;
  color: #1d4ed8;
  font-weight: 600;
}

.shortcut-btn.custom-btn {
  border-style: dashed;
}

/* Available Variables Container */
.available-variables-container {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin-top: 0.5rem;
}

.var-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.var-title {
  font-size: 0.8125rem;
  font-weight: 700;
  color: #334155;
}

.var-hint {
  font-size: 0.75rem;
  color: #64748b;
}

.var-chips-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.var-chip-btn {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  padding: 0.2rem 0.5rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.var-chip-btn:hover {
  background: #eff6ff;
  border-color: #3b82f6;
  transform: translateY(-1px);
}

.var-chip-btn code {
  font-size: 0.75rem;
  color: #2563eb;
  font-weight: 600;
}

/* Live Database Preview Box */
.live-rendered-preview-box {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  padding: 0.875rem 1rem;
  margin-top: 0.75rem;
}

.live-preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.4rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.live-preview-badge {
  font-size: 0.75rem;
  font-weight: 700;
  color: #1d4ed8;
  background: #dbeafe;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.live-preview-recipient {
  font-size: 0.75rem;
  color: #1e40af;
}

.live-preview-content {
  font-size: 0.875rem;
  color: #1e3a8a;
  line-height: 1.45;
  background: #ffffff;
  padding: 0.6rem 0.875rem;
  border-radius: 6px;
  border: 1px solid #dbeafe;
}

/* Templates Tab */
.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1rem;
}

.template-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1.25rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.template-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.template-name {
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.template-code {
  font-size: 0.75rem;
  color: #64748b;
}

.template-category {
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  background: #f1f5f9;
  color: #334155;
  font-weight: 600;
}

.tmpl-row {
  margin-bottom: 0.5rem;
}

.tmpl-lbl {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  display: block;
}

.tmpl-val {
  font-size: 0.875rem;
  color: #0f172a;
}

.tmpl-body-val {
  font-size: 0.8125rem;
  color: #1e293b;
  background: #f8fafc;
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
  margin-top: 0.25rem;
  word-break: break-word;
}

.tmpl-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
}

.tmpl-status.active { color: #16a34a; font-size: 0.75rem; font-weight: 600; }
.tmpl-status.inactive { color: #94a3b8; font-size: 0.75rem; }

/* Settings Switch */
.setting-toggle-group {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid #f1f5f9;
}

.toggle-title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #0f172a;
}

.toggle-sub {
  font-size: 0.8125rem;
  color: #64748b;
  margin: 0.15rem 0 0;
}

.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
  flex-shrink: 0;
}

.switch input { opacity: 0; width: 0; height: 0; }

.slider {
  position: absolute;
  cursor: pointer;
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: #cbd5e1;
  transition: 0.3s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .slider { background-color: #2563eb; }
input:checked + .slider:before { transform: translateX(20px); }

/* Modals & Carousel */
.modal-backdrop {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(15, 23, 42, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
}

.modal-box {
  background: #ffffff;
  border-radius: 12px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.modal-lg {
  max-width: 760px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #64748b;
  cursor: pointer;
}

.modal-body {
  padding: 1.25rem 1.5rem;
  overflow-y: auto;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

/* Live Preview Verification Bar */
.preview-stats-bar {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
}

.p-stat {
  display: flex;
  flex-direction: column;
}

.p-lbl {
  font-size: 0.75rem;
  color: #64748b;
}

.p-val {
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
}

.carousel-preview-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
}

.carousel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.carousel-title {
  font-size: 0.875rem;
  font-weight: 700;
  color: #1e293b;
}

.preview-target-details {
  display: flex;
  gap: 1rem;
  font-size: 0.8125rem;
  color: #475569;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
}

.sms-preview-screen {
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  padding: 1.25rem;
  margin: 0.75rem 0;
}

.sms-bubble {
  background: #2563eb;
  color: #ffffff;
  padding: 0.875rem 1.125rem;
  border-radius: 16px 16px 16px 4px;
  font-size: 0.9375rem;
  line-height: 1.45;
  box-shadow: 0 2px 5px rgba(37, 99, 235, 0.2);
  word-break: break-word;
}

.carousel-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.75rem;
}

.channel-status-card {
  margin-top: 1.5rem;
  padding: 1.25rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}

.channel-list-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.channel-status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
}

.ch-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.ch-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.ch-indicator.online { background: #10b981; box-shadow: 0 0 6px #10b981; }
.ch-indicator.unconfigured { background: #94a3b8; }

.ch-name { font-weight: 600; font-size: 0.875rem; color: #1e293b; }
.ch-details { font-size: 0.75rem; color: #64748b; }
.ch-badge.configured { color: #047857; font-weight: 600; font-size: 0.75rem; }
.ch-badge.unconfigured { color: #64748b; font-size: 0.75rem; }

.overview-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}

.overview-panel {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.panel-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
}

.panel-tag {
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  background: #eff6ff;
  color: #1d4ed8;
  font-weight: 600;
}

.panel-desc {
  font-size: 0.875rem;
  color: #64748b;
  line-height: 1.5;
  margin-bottom: 1.25rem;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 3rem 1.5rem;
  background: #ffffff;
  border: 1px dashed #cbd5e1;
  border-radius: 10px;
}

.empty-icon-wrap {
  width: 48px;
  height: 48px;
  background: #f1f5f9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  color: #64748b;
}

.empty-icon {
  width: 24px;
  height: 24px;
}

/* Hormuud SMS Gateway Card Styles */
.hormuud-gateway-card {
  margin-top: 1.5rem;
  border-left: 4px solid #4f46e5;
  background: #ffffff;
}

.hormuud-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
}

.hormuud-title-group {
  display: flex;
  align-items: center;
  gap: 0.875rem;
}

.hormuud-icon-badge {
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 0.5rem;
  background: #eef2ff;
  color: #4f46e5;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.hormuud-icon-badge svg {
  width: 1.35rem;
  height: 1.35rem;
}

.provider-status-badge {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.625rem;
  border-radius: 9999px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.status-connected {
  background: #ecfdf5;
  color: #047857;
  border: 1px solid #a7f3d0;
}

.status-auth-error {
  background: #fef2f2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}

.status-unavailable {
  background: #fff1f2;
  color: #be123c;
  border: 1px solid #fecdd3;
}

.status-not-configured {
  background: #f8fafc;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.hormuud-meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border: 1px solid #f1f5f9;
  border-radius: 0.5rem;
  margin-bottom: 1.25rem;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.meta-label {
  font-size: 0.6875rem;
  font-weight: 700;
  color: #64748b;
  letter-spacing: 0.05em;
}

.meta-value {
  font-size: 0.875rem;
  color: #1e293b;
}

.meta-balance-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.text-indigo {
  color: #4f46e5;
}

.btn-icon-refresh {
  background: transparent;
  border: none;
  color: #64748b;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem;
  border-radius: 4px;
}

.btn-icon-refresh:hover {
  color: #4f46e5;
  background: #eef2ff;
}

.btn-icon-refresh svg {
  width: 1rem;
  height: 1rem;
}

.diagnostic-box {
  padding: 0.875rem 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1.25rem;
  font-size: 0.8125rem;
}

.diag-success {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #166534;
}

.diag-error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
}

.diag-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.35rem;
}

.diag-time {
  font-size: 0.75rem;
  opacity: 0.85;
}

.diag-msg {
  margin: 0;
  line-height: 1.4;
}

.diag-meta-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin: 0.5rem 0 0.6rem 0;
  padding: 0.5rem 0.75rem;
  background: rgba(255, 255, 255, 0.65);
  border-radius: 4px;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.diag-detail-row {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  font-size: 0.8rem;
}

.diag-detail-label {
  font-weight: 600;
  min-width: 85px;
  color: #7f1d1d;
}

.diag-detail-val {
  color: #991b1b;
  word-break: break-all;
}

.hormuud-actions-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.spin-anim {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .notifications-page {
    padding: 1rem;
  }

  .overview-grid {
    grid-template-columns: 1fr;
  }

  .form-grid-2 {
    grid-template-columns: 1fr;
  }

  .preview-stats-bar {
    grid-template-columns: 1fr 1fr;
  }

  .student-alert-item {
    grid-template-columns: 32px 1fr;
    gap: 0.5rem;
  }

  .guardian-info-col, .status-col {
    grid-column: 2;
  }
}
</style>
