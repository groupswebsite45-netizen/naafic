<script setup lang="ts">
import { ref, onMounted, computed, watch, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import { resultWorkflowService } from '../../services/resultWorkflowService';
import { teacherPortalService } from '../../services/teacherPortalService';
import { TeacherExamAssignmentItem } from '../../types/resultWorkflow';
import ResultStatusBadge from '../../components/results/ResultStatusBadge.vue';
import TeacherCreateExamModal from './components/TeacherCreateExamModal.vue';

const route = useRoute();

interface RosterStudent {
  student_id: number;
  student_name: string;
  admission_number: string;
  attendance_status: 'PRESENT' | 'ABSENT' | 'EXCUSED';
  absence_reason?: string | null;
  complaint?: string | null;
  marks_obtained: number | null;
  max_marks: number;
  grade?: string | null;
  remarks?: string;
  status: string;
  paper_file_path?: string | null;
  paper_original_name?: string | null;
  paper_mime_type?: string | null;
  paper_file_size?: number | null;
  paper_uploaded_at?: string | null;
  isUploadingPaper?: boolean;
}

const assignments = ref<TeacherExamAssignmentItem[]>([]);
const isLoading = ref(true);
const notification = ref<{ type: 'success' | 'error'; message: string } | null>(null);

// Filters
const selectedYear = ref<string>('ALL');
const selectedClass = ref<string>('ALL');
const selectedSubject = ref<string>('ALL');

// Modal & Roster State
const isCreateModalOpen = ref(false);
const isModalOpen = ref(false);
const isRosterLoading = ref(false);
const isSaving = ref(false);
const isSubmitting = ref(false);
const isConfirmSubmitOpen = ref(false);

const activeAssignment = ref<TeacherExamAssignmentItem | null>(null);
const rosterStudents = ref<RosterStudent[]>([]);
const teacherNotes = ref('');

// Paper Preview Modal
const isPreviewModalOpen = ref(false);
const previewStudent = ref<RosterStudent | null>(null);
const previewBlobUrl = ref<string | null>(null);

// Lock background scrolling when modal is open
watch(isModalOpen, (open) => {
  if (typeof document !== 'undefined') {
    document.body.style.overflow = open ? 'hidden' : '';
  }
});

watch(isConfirmSubmitOpen, (open) => {
  if (typeof document !== 'undefined') {
    if (open) document.body.style.overflow = 'hidden';
    else if (!isModalOpen.value) document.body.style.overflow = '';
  }
});

watch(isPreviewModalOpen, (open) => {
  if (typeof document !== 'undefined') {
    if (open) document.body.style.overflow = 'hidden';
    else if (!isModalOpen.value) document.body.style.overflow = '';
  }
});

onUnmounted(() => {
  if (typeof document !== 'undefined') {
    document.body.style.overflow = '';
  }
});

function showNotification(type: 'success' | 'error', message: string) {
  notification.value = { type, message };
  setTimeout(() => {
    notification.value = null;
  }, 6000);
}

// Filtered Streams
const availableYears = computed(() => {
  return Array.from(new Set(assignments.value.map((a) => a.academic_year))).sort().reverse();
});

const availableClasses = computed(() => {
  const filtered = selectedYear.value === 'ALL'
    ? assignments.value
    : assignments.value.filter((a) => a.academic_year === selectedYear.value);
  return Array.from(new Set(filtered.map((a) => a.class_name))).sort();
});

const availableSubjects = computed(() => {
  let filtered = assignments.value;
  if (selectedYear.value !== 'ALL') {
    filtered = filtered.filter((a) => a.academic_year === selectedYear.value);
  }
  if (selectedClass.value !== 'ALL') {
    filtered = filtered.filter((a) => a.class_name === selectedClass.value);
  }
  return Array.from(new Set(filtered.map((a) => a.subject_name))).sort();
});

const activeTab = ref<'active' | 'history'>('active');

const filteredAssignments = computed(() => {
  return assignments.value.filter((a) => {
    if (selectedYear.value !== 'ALL' && a.academic_year !== selectedYear.value) return false;
    if (selectedClass.value !== 'ALL' && a.class_name !== selectedClass.value) return false;
    if (selectedSubject.value !== 'ALL' && a.subject_name !== selectedSubject.value) return false;
    return true;
  });
});

const activeAssignments = computed(() => {
  return filteredAssignments.value.filter(
    (a) => a.status !== 'SUBMITTED' && a.status !== 'UNDER_REVIEW' && a.status !== 'APPROVED' && a.status !== 'RELEASED'
  );
});

const historyAssignments = computed(() => {
  return filteredAssignments.value.filter(
    (a) => a.status === 'SUBMITTED' || a.status === 'UNDER_REVIEW' || a.status === 'APPROVED' || a.status === 'RELEASED'
  );
});

const displayedAssignments = computed(() => {
  return activeTab.value === 'active' ? activeAssignments.value : historyAssignments.value;
});

// Check submission & lock status
const isSubmittedOrApproved = computed(() => {
  if (!activeAssignment.value) return false;
  const s = activeAssignment.value.status;
  return s === 'SUBMITTED' || s === 'UNDER_REVIEW' || s === 'APPROVED' || s === 'RELEASED';
});

const isOverdue = computed(() => {
  if (!activeAssignment.value) return false;
  return !!activeAssignment.value.is_overdue;
});

const isClosed = computed(() => {
  if (!activeAssignment.value) return false;
  return activeAssignment.value.deadline_status === 'CLOSED' || (activeAssignment.value as any).exam_status === 'CLOSED';
});

const isLocked = computed(() => {
  if (!activeAssignment.value) return false;
  return isSubmittedOrApproved.value || (isOverdue.value && !isSubmittedOrApproved.value) || isClosed.value;
});

function formatDeadline(val?: string) {
  if (!val) return 'No deadline set';
  const d = new Date(val);
  if (isNaN(d.getTime())) return val;
  return d.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
}

// Completion Stats
const completedCount = computed(() => {
  return rosterStudents.value.filter((s) => {
    if (s.attendance_status === 'ABSENT' || s.attendance_status === 'EXCUSED') return true;
    return s.marks_obtained !== null && s.marks_obtained !== undefined;
  }).length;
});

const pendingCount = computed(() => {
  return rosterStudents.value.length - completedCount.value;
});

const absentStudentsCount = computed(() => {
  return rosterStudents.value.filter((s) => s.attendance_status === 'ABSENT' || s.attendance_status === 'EXCUSED').length;
});

const recordedReasonsCount = computed(() => {
  return rosterStudents.value.filter((s) => (s.attendance_status === 'ABSENT' || s.attendance_status === 'EXCUSED') && s.absence_reason && s.absence_reason.trim()).length;
});

const recordedComplaintsCount = computed(() => {
  return rosterStudents.value.filter((s) => s.complaint && s.complaint.trim()).length;
});

const isReadyToSubmit = computed(() => {
  return rosterStudents.value.length > 0 && pendingCount.value === 0;
});

// Grade calculation preview
function computeGradePreview(score: number | null, maxMarks: number): string {
  if (score === null || score === undefined) return '—';
  const pct = (score / maxMarks) * 100;
  if (pct >= 90) return 'A+';
  if (pct >= 80) return 'A';
  if (pct >= 70) return 'B';
  if (pct >= 60) return 'C';
  if (pct >= 50) return 'D';
  return 'F';
}

function getProgressPercentage(item: TeacherExamAssignmentItem): number {
  if (!item.expected_students || item.expected_students <= 0) return 0;
  return Math.min(100, Math.round((item.completed_students / item.expected_students) * 100));
}

async function loadAssignments() {
  isLoading.value = true;
  try {
    const list = await resultWorkflowService.getTeacherAssignments();
    assignments.value = list;

    const queryYear = route.query.academic_year as string;
    const queryClass = (route.query.class_name as string) || (route.query.class_id ? list.find((a) => a.class_id === Number(route.query.class_id))?.class_name : undefined);
    const querySub = (route.query.subject_name as string) || (route.query.subject_id ? list.find((a) => a.subject_id === Number(route.query.subject_id))?.subject_name : undefined);

    if (queryYear && list.some((a) => a.academic_year === queryYear)) {
      selectedYear.value = queryYear;
    }
    if (queryClass && list.some((a) => a.class_name === queryClass)) {
      selectedClass.value = queryClass;
    }
    if (querySub && list.some((a) => a.subject_name === querySub)) {
      selectedSubject.value = querySub;
    }
  } catch (err: any) {
    showNotification('error', err?.response?.data?.error?.message || err?.response?.data?.detail || 'Failed to load assigned streams.');
  } finally {
    isLoading.value = false;
  }
}

async function openRosterModal(item: TeacherExamAssignmentItem) {
  activeAssignment.value = item;
  isModalOpen.value = true;
  isRosterLoading.value = true;
  teacherNotes.value = '';
  try {
    const data = await resultWorkflowService.getTeacherExamRoster(item.exam_id);
    rosterStudents.value = (data.students || []).map((std: any) => ({
      student_id: std.student_id,
      student_name: std.student_name,
      admission_number: std.admission_number,
      attendance_status: std.attendance_status || 'PRESENT',
      absence_reason: std.absence_reason || '',
      complaint: std.complaint || '',
      marks_obtained: std.marks_obtained !== null ? Number(std.marks_obtained) : null,
      max_marks: Number(std.max_marks || item.max_marks || 100),
      grade: std.grade || null,
      remarks: std.remarks || '',
      status: std.status || 'DRAFT',
      paper_file_path: std.paper_file_path || null,
      paper_original_name: std.paper_original_name || null,
      paper_mime_type: std.paper_mime_type || null,
      paper_file_size: std.paper_file_size || null,
      paper_uploaded_at: std.paper_uploaded_at || null,
      isUploadingPaper: false,
    }));
  } catch (err: any) {
    showNotification('error', err?.response?.data?.error?.message || err?.response?.data?.detail || 'Failed to load class roster.');
    isModalOpen.value = false;
  } finally {
    isRosterLoading.value = false;
  }
}

function handleAttendanceChange(std: RosterStudent) {
  if (std.attendance_status === 'ABSENT' || std.attendance_status === 'EXCUSED') {
    std.marks_obtained = null;
    std.grade = std.attendance_status;
  } else {
    if (std.marks_obtained !== null) {
      std.grade = computeGradePreview(std.marks_obtained, std.max_marks);
    } else {
      std.grade = null;
    }
  }
}

function handleMarksInput(std: RosterStudent) {
  if (std.attendance_status === 'PRESENT') {
    if (std.marks_obtained !== null && !isNaN(std.marks_obtained)) {
      if (std.marks_obtained > std.max_marks) std.marks_obtained = std.max_marks;
      if (std.marks_obtained < 0) std.marks_obtained = 0;
      std.grade = computeGradePreview(std.marks_obtained, std.max_marks);
    } else {
      std.grade = null;
    }
  }
}

// Paper Upload Handler
async function handlePaperUpload(std: RosterStudent, event: Event) {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file || !activeAssignment.value) return;

  std.isUploadingPaper = true;
  try {
    const res = await teacherPortalService.uploadExamPaper(activeAssignment.value.exam_id, std.student_id, file);
    std.paper_file_path = res.filename;
    std.paper_original_name = res.filename;
    std.paper_mime_type = res.mime_type;
    std.paper_file_size = res.file_size;
    std.paper_uploaded_at = res.uploaded_at;
    showNotification('success', `Exam document uploaded for ${std.student_name}.`);
  } catch (err: any) {
    showNotification('error', err?.response?.data?.error?.message || err?.response?.data?.detail || 'Failed to upload paper.');
  } finally {
    std.isUploadingPaper = false;
    target.value = '';
  }
}

async function handleDeletePaper(std: RosterStudent) {
  if (!activeAssignment.value) return;
  if (!confirm(`Are you sure you want to remove the exam paper for ${std.student_name}?`)) return;

  try {
    await teacherPortalService.deleteExamPaper(activeAssignment.value.exam_id, std.student_id);
    std.paper_file_path = null;
    std.paper_original_name = null;
    std.paper_mime_type = null;
    std.paper_file_size = null;
    std.paper_uploaded_at = null;
    showNotification('success', 'Exam document removed.');
  } catch (err: any) {
    showNotification('error', err?.response?.data?.error?.message || err?.response?.data?.detail || 'Failed to delete paper.');
  }
}

async function handlePreviewPaper(std: RosterStudent) {
  if (!activeAssignment.value) return;
  previewStudent.value = std;
  isPreviewModalOpen.value = true;
  try {
    const { blob } = await teacherPortalService.getExamPaperBlob(activeAssignment.value.exam_id, std.student_id);
    previewBlobUrl.value = URL.createObjectURL(blob);
  } catch (err: any) {
    showNotification('error', 'Failed to preview exam paper file.');
    isPreviewModalOpen.value = false;
  }
}

function closePreviewModal() {
  isPreviewModalOpen.value = false;
  if (previewBlobUrl.value) {
    URL.revokeObjectURL(previewBlobUrl.value);
    previewBlobUrl.value = null;
  }
  previewStudent.value = null;
}

// Save Draft
async function handleSaveDraft() {
  if (!activeAssignment.value) return;
  isSaving.value = true;
  try {
    const payload = {
      exam_id: activeAssignment.value.exam_id,
      class_id: activeAssignment.value.class_id,
      subject_id: activeAssignment.value.subject_id,
      marks: rosterStudents.value.map((s) => ({
        student_id: s.student_id,
        attendance_status: s.attendance_status,
        marks_obtained: s.attendance_status === 'PRESENT' ? s.marks_obtained : null,
        absence_reason: s.attendance_status !== 'PRESENT' ? (s.absence_reason || 'Reason not provided') : (s.absence_reason || undefined),
        complaint: s.complaint || undefined,
        remarks: s.remarks || undefined,
      })),
    };
    const res = await resultWorkflowService.saveTeacherDraft(payload);
    showNotification('success', res.message || 'Draft saved successfully in PostgreSQL.');
    await loadAssignments();
  } catch (err: any) {
    showNotification('error', err?.response?.data?.error?.message || err?.response?.data?.detail || 'Failed to save draft.');
  } finally {
    isSaving.value = false;
  }
}

function triggerSubmit() {
  if (!isReadyToSubmit.value) {
    showNotification('error', `${pendingCount.value} student(s) still require marks or attendance.`);
    return;
  }
  isConfirmSubmitOpen.value = true;
}

async function handleConfirmSubmit() {
  if (!activeAssignment.value) return;
  isSubmitting.value = true;
  try {
    const payload = {
      exam_id: activeAssignment.value.exam_id,
      class_id: activeAssignment.value.class_id,
      subject_id: activeAssignment.value.subject_id,
      marks: rosterStudents.value.map((s) => ({
        student_id: s.student_id,
        attendance_status: s.attendance_status,
        marks_obtained: s.attendance_status === 'PRESENT' ? s.marks_obtained : null,
        absence_reason: s.attendance_status !== 'PRESENT' ? (s.absence_reason || 'Reason not provided') : (s.absence_reason || undefined),
        complaint: s.complaint || undefined,
        remarks: s.remarks || undefined,
      })),
      notes: teacherNotes.value || undefined,
    };
    const res = await resultWorkflowService.submitTeacherResults(payload);
    showNotification('success', res.message || 'Results submitted to administration for review.');
    isConfirmSubmitOpen.value = false;
    isModalOpen.value = false;
    await loadAssignments();
    // Switch to history tab to show the submitted result
    activeTab.value = 'history';
  } catch (err: any) {
    showNotification('error', err?.response?.data?.error?.message || err?.response?.data?.detail || 'Failed to submit results.');
  } finally {
    isSubmitting.value = false;
  }
}

async function handleExamCreated(newExam: any) {
  showNotification('success', `Exam "${newExam.name}" created successfully.`);
  await loadAssignments();
  const createdItem = assignments.value.find((a) => a.exam_id === newExam.id);
  if (createdItem) {
    openRosterModal(createdItem);
  }
}

onMounted(() => {
  loadAssignments();
});
</script>

<template>
  <div class="portal-page">
    <!-- Notification Toast -->
    <div v-if="notification" class="toast-banner" :class="notification.type">
      <div class="toast-content">
        <span>{{ notification.message }}</span>
        <button class="toast-close" aria-label="Dismiss notification" @click="notification = null">&times;</button>
      </div>
    </div>

    <!-- Page Header -->
    <div class="page-header">
      <div class="header-titles">
        <h1 class="page-title">Exams & Marks Entry Portal</h1>
        <p class="page-subtitle">
          Create examinations for your assigned classes, enter student marks, attach papers, and submit results to Administration.
        </p>
      </div>
      <div class="header-actions">
        <button
          type="button"
          class="btn-create-exam"
          @click="isCreateModalOpen = true"
        >
          <svg class="btn-create-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
          </svg>
          <span>Create New Exam</span>
        </button>
      </div>
    </div>

    <!-- Filters Bar -->
    <div class="filters-card card">
      <div class="filters-grid">
        <div class="form-group">
          <label class="form-label">Academic Year</label>
          <select v-model="selectedYear" class="form-select">
            <option value="ALL">All Academic Years ({{ availableYears.length }})</option>
            <option v-for="yr in availableYears" :key="yr" :value="yr">{{ yr }}</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Class</label>
          <select v-model="selectedClass" class="form-select">
            <option value="ALL">All Assigned Classes ({{ availableClasses.length }})</option>
            <option v-for="c in availableClasses" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Subject</label>
          <select v-model="selectedSubject" class="form-select">
            <option value="ALL">All Assigned Subjects ({{ availableSubjects.length }})</option>
            <option v-for="s in availableSubjects" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Workflow Tabs (Active Tasks vs Submission History) -->
    <div class="workflow-tabs-container">
      <button
        type="button"
        class="workflow-tab-btn"
        :class="{ active: activeTab === 'active' }"
        @click="activeTab = 'active'"
      >
        <svg class="tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
        <span>Active Result Entry Tasks</span>
        <span class="tab-badge" :class="activeAssignments.length > 0 ? 'badge-primary' : 'badge-empty'">
          {{ activeAssignments.length }}
        </span>
      </button>
      <button
        type="button"
        class="workflow-tab-btn"
        :class="{ active: activeTab === 'history' }"
        @click="activeTab = 'history'"
      >
        <svg class="tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>Submission History</span>
        <span class="tab-badge badge-neutral">
          {{ historyAssignments.length }}
        </span>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-box card">
      <div class="spinner" />
      <span>Loading examination streams from PostgreSQL...</span>
    </div>

    <!-- Empty State -->
    <div v-else-if="displayedAssignments.length === 0" class="card empty-box">
      <svg class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <p class="empty-title">{{ activeTab === 'active' ? 'No Pending Result Entry Tasks' : 'No Submitted Result Sheets' }}</p>
      <p class="empty-desc">
        {{ activeTab === 'active' ? 'All your assigned subject results have been completed and submitted to Administration.' : 'Submitted exam result sheets and admin reviews will be preserved here permanently.' }}
      </p>
      <button
        v-if="activeTab === 'active'"
        type="button"
        class="btn btn-primary"
        style="margin-top: 1rem;"
        @click="isCreateModalOpen = true"
      >
        + Create New Exam
      </button>
    </div>

    <!-- Streams Grid (Responsive Cards) -->
    <div v-else class="streams-grid">
      <div
        v-for="item in displayedAssignments"
        :key="item.exam_id"
        class="stream-card card"
        :class="{ 'card-overdue': item.is_overdue && item.status !== 'SUBMITTED' && item.status !== 'APPROVED' && item.status !== 'RELEASED' }"
      >
        <div class="stream-header">
          <div class="stream-title-col">
            <div class="stream-type-line">
              <span class="exam-type-pill" :class="item.exam_type">{{ item.exam_type }}</span>
              <span v-if="item.remaining_time_human" class="deadline-countdown-chip" :class="item.deadline_status">
                <svg v-if="item.is_overdue" class="chip-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
                <svg v-else class="chip-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
                </svg>
                {{ item.remaining_time_human }}
              </span>
            </div>
            <span class="exam-title">{{ item.exam_name }}</span>
            <span class="exam-scope">
              {{ item.class_name }}<template v-if="item.class_section"> ({{ item.class_section }})</template> • {{ item.subject_name }}
            </span>
          </div>
          <ResultStatusBadge :status="item.status" />
        </div>

        <!-- Overdue Notice in Card -->
        <div v-if="item.is_overdue && item.status !== 'SUBMITTED' && item.status !== 'APPROVED' && item.status !== 'RELEASED'" class="alert-box-small danger">
          <strong>⚠️ Submissions Overdue:</strong> Deadline passed ({{ item.remaining_time_human }}). Contact School Admin to request an extension.
        </div>

        <!-- Returned Warning Alert -->
        <div v-else-if="item.status === 'RETURNED'" class="alert-box-small warning">
          <strong>Returned for Correction:</strong> {{ item.return_reason || 'Please review scores and resubmit.' }}
        </div>

        <!-- Deadline row -->
        <div v-if="item.result_submission_deadline" class="stream-deadline-bar">
          <span class="deadline-title">Submission Deadline:</span>
          <span class="deadline-time">{{ formatDeadline(item.result_submission_deadline) }}</span>
        </div>

        <!-- Progress Bar -->
        <div class="progress-section">
          <div class="progress-labels">
            <span>Score Entry Progress</span>
            <strong>{{ item.completed_students }} / {{ item.expected_students }} ({{ getProgressPercentage(item) }}%)</strong>
          </div>
          <div class="progress-bar-bg">
            <div class="progress-bar-fill" :style="{ width: `${getProgressPercentage(item)}%` }" />
          </div>
        </div>

        <div class="stream-meta-row">
          <span>Max Marks: <strong>{{ item.max_marks }}</strong></span>
          <span>Pass Marks: <strong>{{ item.pass_marks }}</strong></span>
        </div>

        <div class="stream-actions">
          <button
            class="btn btn-primary btn-touch btn-block"
            :class="{ 'btn-overdue': item.is_overdue && item.status !== 'SUBMITTED' && item.status !== 'APPROVED' && item.status !== 'RELEASED' }"
            @click="openRosterModal(item)"
          >
            {{
              item.status === 'SUBMITTED' || item.status === 'APPROVED' || item.status === 'RELEASED'
                ? 'View Submitted Results (Read-Only)'
                : (item.is_overdue
                    ? 'View Marks (Overdue / Locked)'
                    : (item.status === 'RETURNED'
                        ? 'Correct & Resubmit to Admin'
                        : 'Enter / Edit Marks'))
            }}
          </button>
        </div>
      </div>
    </div>

    <!-- =================================================================== -->
    <!-- ROSTER ENTRY MODAL (FIXED & FULLY OPTIMIZED FOR MOBILE)             -->
    <!-- =================================================================== -->
    <div v-if="isModalOpen && activeAssignment" class="modal-backdrop" @click="isModalOpen = false">
      <div class="modal-card full-modal" @click.stop>
        <!-- Modal Header (Fixed / Sticky at Top) -->
        <header class="modal-header">
          <div class="header-main-col">
            <div class="header-tag-line">
              <span class="class-badge">{{ activeAssignment.class_name }}</span>
              <span class="subject-badge">{{ activeAssignment.subject_name }}</span>
              <ResultStatusBadge :status="activeAssignment.status" />
            </div>
            <h2 class="modal-exam-name">{{ activeAssignment.exam_name }}</h2>
          </div>
          <button
            class="modal-close-btn"
            aria-label="Close exam details modal"
            @click="isModalOpen = false"
          >
            &times;
          </button>
        </header>

        <!-- Modal Scrollable Content Area -->
        <div class="modal-scroll-body">
          <!-- Deadline & Instructions Banner -->
          <div v-if="activeAssignment.result_submission_deadline || activeAssignment.instructions" class="deadline-instructions-card" :class="{ 'is-overdue': activeAssignment.is_overdue }">
            <div class="deadline-header-row">
              <div class="deadline-info">
                <span class="meta-label">Result Submission Deadline:</span>
                <span class="meta-date">{{ formatDeadline(activeAssignment.result_submission_deadline) }}</span>
              </div>
              <div v-if="activeAssignment.remaining_time_human" class="deadline-countdown-badge" :class="activeAssignment.deadline_status">
                {{ activeAssignment.remaining_time_human }}
              </div>
            </div>
            <div v-if="activeAssignment.instructions" class="instructions-block">
              <span class="instructions-title">Admin Instructions:</span>
              <p class="instructions-content">{{ activeAssignment.instructions }}</p>
            </div>
          </div>

          <!-- Returned Message Alert -->
          <div v-if="activeAssignment.status === 'RETURNED' && activeAssignment.return_reason" class="alert-box-compact warning">
            <div class="alert-compact-title">⚠️ Returned by Administration for Correction</div>
            <p class="alert-compact-desc">{{ activeAssignment.return_reason }}</p>
          </div>

          <!-- Overdue Alert -->
          <div v-if="isOverdue && !isSubmittedOrApproved" class="alert-box-compact danger">
            <div class="alert-compact-title">⚠️ Result Submission Deadline Passed</div>
            <p class="alert-compact-desc">
              The result submission deadline for this examination has passed ({{ activeAssignment.remaining_time_human }}). Mark modifications and submissions are locked. Please contact the School Administrator to request an extension or reopen access.
            </p>
          </div>

          <!-- Submission Locked Compact Alert -->
          <div v-else-if="isSubmittedOrApproved" class="alert-box-compact info">
            <div class="alert-compact-title">🔒 Submission Locked</div>
            <p class="alert-compact-desc">
              Marks have been submitted to Administration. Scores can only be modified if Administration returns them for correction.
            </p>
          </div>

          <!-- KPI / Summary Grid (Multi-Col Responsive) -->
          <div class="roster-summary-grid">
            <div class="kpi-box">
              <span class="kpi-label">TOTAL</span>
              <span class="kpi-value">{{ rosterStudents.length }}</span>
            </div>
            <div class="kpi-box">
              <span class="kpi-label">COMPLETED</span>
              <span class="kpi-value text-emerald">{{ completedCount }}</span>
            </div>
            <div class="kpi-box">
              <span class="kpi-label">PENDING</span>
              <span class="kpi-value text-rose">{{ pendingCount }}</span>
            </div>
            <div class="kpi-box">
              <span class="kpi-label">ABSENT</span>
              <span class="kpi-value text-amber">{{ absentStudentsCount }}</span>
            </div>
            <div class="kpi-box">
              <span class="kpi-label">REASONS</span>
              <span class="kpi-value text-amber">{{ recordedReasonsCount }}</span>
            </div>
            <div class="kpi-box">
              <span class="kpi-label">COMPLAINTS</span>
              <span class="kpi-value text-rose">{{ recordedComplaintsCount }}</span>
            </div>
            <div class="kpi-box kpi-max-box">
              <span class="kpi-label">MAX MARKS</span>
              <span class="kpi-value">{{ activeAssignment.max_marks }}</span>
            </div>
          </div>

          <!-- Loading Indicator -->
          <div v-if="isRosterLoading" class="loading-state">
            <div class="spinner" />
            <span>Loading student roster and scores from database...</span>
          </div>

          <div v-else class="roster-data-wrap">
            <!-- 1. Desktop Table View (>= 769px) -->
            <div class="desktop-table-container">
              <table class="roster-table">
                <thead>
                  <tr>
                    <th style="width: 40px;">#</th>
                    <th>Student Name</th>
                    <th>Admission #</th>
                    <th style="width: 120px;">Attendance</th>
                    <th style="width: 110px;">Marks (/{{ activeAssignment.max_marks }})</th>
                    <th style="width: 70px; text-align: center;">Grade</th>
                    <th style="width: 170px;">Absence Reason</th>
                    <th style="width: 170px;">Student Complaint</th>
                    <th>Remarks</th>
                    <th>Exam Paper</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(std, idx) in rosterStudents" :key="std.student_id">
                    <td class="text-muted font-mono">{{ idx + 1 }}</td>
                    <td class="font-bold">{{ std.student_name }}</td>
                    <td><code>{{ std.admission_number }}</code></td>
                    <td>
                      <select
                        v-model="std.attendance_status"
                        class="roster-select"
                        :disabled="isLocked"
                        @change="handleAttendanceChange(std)"
                      >
                        <option value="PRESENT">Present</option>
                        <option value="ABSENT">Absent</option>
                        <option value="EXCUSED">Excused</option>
                      </select>
                    </td>
                    <td>
                      <input
                        v-if="std.attendance_status === 'PRESENT'"
                        v-model.number="std.marks_obtained"
                        type="number"
                        inputmode="decimal"
                        class="roster-mark-input"
                        :min="0"
                        :max="std.max_marks"
                        placeholder="Score"
                        :disabled="isLocked"
                        @input="handleMarksInput(std)"
                      />
                      <span v-else class="text-muted status-tag">{{ std.attendance_status }}</span>
                    </td>
                    <td style="text-align: center;">
                      <span
                        class="grade-pill"
                        :class="std.grade ? std.grade.toLowerCase().replace('+', '-plus') : 'empty'"
                      >
                        {{ std.grade || '—' }}
                      </span>
                    </td>
                    <td>
                      <input
                        v-if="std.attendance_status !== 'PRESENT'"
                        v-model="std.absence_reason"
                        type="text"
                        class="roster-remark-input"
                        placeholder="e.g. Medical / Unwell"
                        :disabled="isLocked"
                      />
                      <span v-else class="text-muted" style="font-size: 0.8rem; text-align: center; display: block;">—</span>
                    </td>
                    <td>
                      <input
                        v-model="std.complaint"
                        type="text"
                        class="roster-remark-input"
                        placeholder="Optional complaint..."
                        :disabled="isLocked"
                      />
                    </td>
                    <td>
                      <input
                        v-model="std.remarks"
                        type="text"
                        class="roster-remark-input"
                        placeholder="Optional notes"
                        :disabled="isLocked"
                      />
                    </td>
                    <td>
                      <div class="paper-upload-cell">
                        <div v-if="std.paper_file_path" class="uploaded-paper-tag">
                          <svg class="paper-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                          <button type="button" class="paper-name-btn" @click="handlePreviewPaper(std)">
                            {{ std.paper_original_name || 'View Paper' }}
                          </button>
                          <button
                            v-if="!isLocked"
                            type="button"
                            class="paper-del-btn"
                            title="Remove Paper"
                            @click="handleDeletePaper(std)"
                          >
                            &times;
                          </button>
                        </div>
                        <label v-else-if="!isLocked" class="upload-paper-btn" :class="{ disabled: std.isUploadingPaper }">
                          <input
                            type="file"
                            accept=".jpg,.jpeg,.png,.pdf"
                            style="display: none;"
                            @change="handlePaperUpload(std, $event)"
                          />
                          <span>{{ std.isUploadingPaper ? 'Uploading...' : '+ Attach Paper' }}</span>
                        </label>
                        <span v-else class="text-muted" style="font-size: 0.75rem;">No Paper Attached</span>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- 2. Mobile Student Cards View (<= 768px) -->
            <div class="mobile-student-cards-list">
              <article
                v-for="(std, idx) in rosterStudents"
                :key="std.student_id"
                class="mobile-student-entry-card"
              >
                <!-- Card Header -->
                <div class="m-card-header">
                  <span class="m-student-index">#{{ idx + 1 }}</span>
                  <div class="m-student-identity">
                    <h4 class="m-student-name">{{ std.student_name }}</h4>
                    <span class="m-student-adm">Admission: <code>{{ std.admission_number }}</code></span>
                  </div>
                </div>

                <div class="m-card-divider" />

                <!-- Attendance Row -->
                <div class="m-field-group">
                  <label class="m-field-label">ATTENDANCE</label>
                  <select
                    v-model="std.attendance_status"
                    class="m-select-input"
                    :disabled="isLocked"
                    @change="handleAttendanceChange(std)"
                  >
                    <option value="PRESENT">Present</option>
                    <option value="ABSENT">Absent</option>
                    <option value="EXCUSED">Excused</option>
                  </select>
                </div>

                <!-- Marks Row -->
                <div class="m-field-group">
                  <label class="m-field-label">MARKS</label>
                  <div v-if="std.attendance_status === 'PRESENT'" class="m-marks-input-row">
                    <input
                      v-model.number="std.marks_obtained"
                      type="number"
                      inputmode="decimal"
                      class="m-marks-input"
                      :min="0"
                      :max="std.max_marks"
                      placeholder="0"
                      :disabled="isLocked"
                      @input="handleMarksInput(std)"
                    />
                    <span class="m-max-marks-label">/ {{ std.max_marks }}</span>
                  </div>
                  <div v-else class="m-absent-notice">
                    <span>Student marked <strong>{{ std.attendance_status }}</strong> (Scores disabled)</span>
                  </div>
                </div>

                <!-- Absence Reason Row (when Absent or Excused) -->
                <div v-if="std.attendance_status !== 'PRESENT'" class="m-field-group">
                  <label class="m-field-label">ABSENCE REASON</label>
                  <input
                    v-model="std.absence_reason"
                    type="text"
                    class="m-marks-input"
                    style="text-align: left; font-size: 0.85rem;"
                    placeholder="e.g. Medical / Unwell"
                    :disabled="isLocked"
                  />
                </div>

                <!-- Complaint Row -->
                <div class="m-field-group">
                  <label class="m-field-label">STUDENT COMPLAINT / INQUIRY</label>
                  <input
                    v-model="std.complaint"
                    type="text"
                    class="m-marks-input"
                    style="text-align: left; font-size: 0.85rem;"
                    placeholder="Optional student complaint..."
                    :disabled="isLocked"
                  />
                </div>

                <!-- Grade Row -->
                <div class="m-field-group">
                  <label class="m-field-label">GRADE</label>
                  <div class="m-grade-display">
                    <span
                      class="grade-pill lg"
                      :class="std.grade ? std.grade.toLowerCase().replace('+', '-plus') : 'empty'"
                    >
                      {{ std.grade ? `${std.grade}` : '—' }}
                    </span>
                    <span v-if="std.grade && std.attendance_status === 'PRESENT'" class="m-grade-subtext">
                      {{ (std.marks_obtained || 0) >= (activeAssignment.pass_marks || 50) ? 'Pass' : 'Needs Improvement' }}
                    </span>
                  </div>
                </div>

                <!-- Exam Paper Row -->
                <div class="m-field-group">
                  <label class="m-field-label">EXAM PAPER</label>
                  <div v-if="std.paper_file_path" class="m-paper-attached-row">
                    <div class="m-paper-info">
                      <span class="m-paper-title">📄 {{ std.paper_original_name || 'Exam Paper Attached' }}</span>
                    </div>
                    <div class="m-paper-actions">
                      <button type="button" class="btn btn-xs btn-outline" @click="handlePreviewPaper(std)">
                        View
                      </button>
                      <button
                        v-if="!isLocked"
                        type="button"
                        class="btn btn-xs btn-outline-danger"
                        @click="handleDeletePaper(std)"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                  <div v-else class="m-no-paper-row">
                    <span class="m-no-paper-text">No Paper Attached</span>
                    <label v-if="!isLocked" class="btn btn-xs btn-outline m-upload-btn" :class="{ disabled: std.isUploadingPaper }">
                      <input
                        type="file"
                        accept=".jpg,.jpeg,.png,.pdf"
                        style="display: none;"
                        @change="handlePaperUpload(std, $event)"
                      />
                      <span>{{ std.isUploadingPaper ? 'Uploading...' : '📎 Upload Paper' }}</span>
                    </label>
                  </div>
                </div>

                <!-- Remarks Row -->
                <div class="m-field-group">
                  <label class="m-field-label">REMARKS</label>
                  <textarea
                    v-model="std.remarks"
                    class="m-textarea"
                    rows="2"
                    placeholder="Enter teacher feedback or observations..."
                    :disabled="isLocked"
                  />
                </div>
              </article>
            </div>
          </div>
        </div>

        <!-- Modal Footer (Fixed / Sticky at Bottom) -->
        <footer class="modal-footer">
          <div class="footer-status-msg">
            <span v-if="!isReadyToSubmit && !isLocked" class="pending-warning">
              ⚠️ {{ pendingCount }} student(s) still require marks entry.
            </span>
            <span v-else-if="isLocked" class="locked-indicator-pill">
              🔒 Results {{ activeAssignment.status === 'RELEASED' ? 'Published to Students' : (activeAssignment.status === 'APPROVED' ? 'Approved by Administration' : 'Submitted to Administration (Read-Only)') }}
            </span>
          </div>
          <div class="footer-action-buttons">
            <button class="btn btn-outline btn-touch btn-footer-item" @click="isModalOpen = false">
              Close
            </button>
            <button
              v-if="!isLocked"
              class="btn btn-outline btn-touch btn-footer-item"
              :disabled="isSaving"
              @click="handleSaveDraft"
            >
              {{ isSaving ? 'Saving Draft...' : 'Save Draft' }}
            </button>
            <button
              v-if="!isLocked"
              class="btn btn-primary btn-touch btn-footer-item btn-footer-submit"
              :disabled="!isReadyToSubmit || isSubmitting"
              @click="triggerSubmit"
            >
              Submit Results to Admin
            </button>
          </div>
        </footer>
      </div>
    </div>

    <!-- =================================================================== -->
    <!-- SUBMIT CONFIRMATION MODAL                                           -->
    <!-- =================================================================== -->
    <div v-if="isConfirmSubmitOpen && activeAssignment" class="modal-backdrop" @click="isConfirmSubmitOpen = false">
      <div class="modal-card small-modal" @click.stop>
        <header class="modal-header">
          <h3 class="modal-title">Submit Results to Administration</h3>
          <button class="modal-close-btn" aria-label="Close modal" @click="isConfirmSubmitOpen = false">&times;</button>
        </header>
        <div class="modal-scroll-body">
          <p class="confirm-intro">You are about to formally submit completed marks for administrative review:</p>
          <div class="confirm-box">
            <div><strong>Exam:</strong> {{ activeAssignment.exam_name }}</div>
            <div><strong>Class:</strong> {{ activeAssignment.class_name }}</div>
            <div><strong>Subject:</strong> {{ activeAssignment.subject_name }}</div>
            <div><strong>Completed Records:</strong> {{ completedCount }} / {{ rosterStudents.length }}</div>
          </div>
          <div class="form-group" style="margin-top: 1rem;">
            <label class="form-label">Optional Submission Notes for Admin</label>
            <textarea
              v-model="teacherNotes"
              class="form-input"
              rows="2"
              placeholder="e.g., All scores entered and verified against physical answer sheets."
            />
          </div>
        </div>
        <footer class="modal-footer">
          <button class="btn btn-outline btn-touch" :disabled="isSubmitting" @click="isConfirmSubmitOpen = false">
            Cancel
          </button>
          <button class="btn btn-primary btn-touch" :disabled="isSubmitting" @click="handleConfirmSubmit">
            {{ isSubmitting ? 'Submitting to Admin...' : 'Confirm Submission' }}
          </button>
        </footer>
      </div>
    </div>

    <!-- =================================================================== -->
    <!-- EXAM PAPER PREVIEW MODAL                                            -->
    <!-- =================================================================== -->
    <div v-if="isPreviewModalOpen && previewStudent" class="modal-backdrop" @click="closePreviewModal">
      <div class="modal-card preview-modal" @click.stop>
        <header class="modal-header">
          <div>
            <h3 class="modal-title">Exam Document Preview</h3>
            <span class="adm-code">{{ previewStudent.student_name }} ({{ previewStudent.admission_number }})</span>
          </div>
          <button class="modal-close-btn" aria-label="Close preview" @click="closePreviewModal">&times;</button>
        </header>
        <div class="modal-scroll-body preview-scroll-body">
          <div v-if="!previewBlobUrl" class="loading-state">
            <div class="spinner" />
            <span>Loading exam paper file...</span>
          </div>
          <div v-else-if="previewStudent.paper_mime_type === 'application/pdf'" class="pdf-preview-box">
            <iframe :src="previewBlobUrl" class="pdf-iframe" title="Exam Document Preview" />
          </div>
          <div v-else class="image-preview-box">
            <img :src="previewBlobUrl" alt="Exam Sheet Preview" class="preview-img" />
          </div>
        </div>
        <footer class="modal-footer">
          <button class="btn btn-primary btn-touch btn-block" @click="closePreviewModal">Close Preview</button>
        </footer>
      </div>
    </div>

    <!-- =================================================================== -->
    <!-- TEACHER CREATE EXAM MODAL                                           -->
    <!-- =================================================================== -->
    <TeacherCreateExamModal
      :is-open="isCreateModalOpen"
      @close="isCreateModalOpen = false"
      @created="handleExamCreated"
    />
  </div>
</template>

<style scoped>
.portal-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 1300px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

/* Toast Notification */
.toast-banner {
  padding: 0.85rem 1.25rem;
  border-radius: 8px;
  animation: fadeIn 0.3s ease;
}
.toast-banner.success { background: #ecfdf5; border: 1px solid #a7f3d0; color: #065f46; }
.toast-banner.error { background: #fef2f2; border: 1px solid #fecaca; color: #991b1b; }
.toast-content { display: flex; justify-content: space-between; align-items: center; font-size: 0.9rem; font-weight: 500; }
.toast-close { background: none; border: none; font-size: 1.4rem; cursor: pointer; color: inherit; line-height: 1; }

/* Page Header */
.page-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }
.header-titles { min-width: 0; flex: 1; }
.page-title { font-size: 1.5rem; font-weight: 800; color: var(--text-primary, #0f172a); margin: 0; word-break: break-word; }
.page-subtitle { font-size: 0.85rem; color: var(--text-muted, #64748b); margin-top: 0.2rem; }

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-create-exam {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 700;
  color: #ffffff;
  background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
  border: 1px solid #4338ca;
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.25);
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-create-exam:hover {
  background: linear-gradient(135deg, #4338ca 0%, #3730a3 100%);
  box-shadow: 0 6px 12px -1px rgba(79, 70, 229, 0.35);
  transform: translateY(-1px);
}

.btn-create-icon {
  width: 18px;
  height: 18px;
}

@media (max-width: 640px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }
  .header-actions {
    width: 100%;
  }
  .btn-create-exam {
    width: 100%;
    justify-content: center;
  }
}

/* Filters Bar */
.filters-card { padding: 1.25rem; width: 100%; box-sizing: border-box; }
.filters-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
.form-group { display: flex; flex-direction: column; gap: 0.35rem; }
.form-label { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: var(--text-muted, #64748b); letter-spacing: 0.03em; }
.form-select, .form-input {
  padding: 0.55rem 0.75rem;
  border: 1px solid var(--border-medium, #cbd5e1);
  border-radius: 6px;
  background: var(--bg-surface, #ffffff);
  font-size: 0.88rem;
  color: var(--text-primary, #0f172a);
  width: 100%;
  box-sizing: border-box;
  min-height: 40px;
}

/* Workflow Tabs */
.workflow-tabs-container {
  display: flex;
  gap: 0.75rem;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 0.25rem;
}

.workflow-tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1.15rem;
  font-size: 0.9rem;
  font-weight: 700;
  color: #64748b;
  background: transparent;
  border: none;
  border-radius: 8px 8px 0 0;
  cursor: pointer;
  position: relative;
  transition: all 0.2s ease;
}

.workflow-tab-btn:hover {
  color: #1e293b;
  background: #f8fafc;
}

.workflow-tab-btn.active {
  color: #1e40af;
  background: #eff6ff;
  border-bottom: 3px solid #1e40af;
}

.workflow-tab-btn .tab-icon {
  width: 18px;
  height: 18px;
}

.tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 800;
}

.tab-badge.badge-primary {
  background: #3b82f6;
  color: #ffffff;
}

.tab-badge.badge-empty {
  background: #e2e8f0;
  color: #64748b;
}

.tab-badge.badge-neutral {
  background: #e2e8f0;
  color: #334155;
}

.locked-indicator-pill {
  display: inline-flex;
  align-items: center;
  font-size: 0.8rem;
  font-weight: 700;
  color: #1e40af;
  background: #dbeafe;
  border: 1px solid #bfdbfe;
  padding: 0.25rem 0.65rem;
  border-radius: 6px;
}

/* Streams Grid */
.streams-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.25rem;
  width: 100%;
}
.stream-card {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 1rem;
  border-top: 4px solid #0284c7;
  transition: transform 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}
.stream-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.stream-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; }
.stream-title-col { display: flex; flex-direction: column; min-width: 0; }
.exam-title { font-size: 1.15rem; font-weight: 800; color: var(--text-primary, #0f172a); word-break: break-word; }
.exam-scope { font-size: 0.82rem; color: var(--text-muted, #64748b); display: block; margin-top: 0.15rem; }

.stream-card.card-overdue {
  border-top-color: #ef4444;
  border-left: 3px solid #ef4444;
}

.stream-type-line {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.35rem;
  flex-wrap: wrap;
}

.exam-type-pill {
  font-size: 0.6875rem;
  font-weight: 800;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  background: #f1f5f9;
  color: #475569;
}

.exam-type-pill.FINAL { background: #fee2e2; color: #991b1b; }
.exam-type-pill.MID_TERM { background: #e0e7ff; color: #3730a3; }
.exam-type-pill.MONTHLY { background: #dcfce7; color: #166534; }
.exam-type-pill.QUIZ { background: #fef3c7; color: #92400e; }

.deadline-countdown-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  background: #f1f5f9;
  color: #475569;
}

.deadline-countdown-chip.OVERDUE {
  background: #fef2f2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}

.deadline-countdown-chip.APPROACHING {
  background: #fffbeb;
  color: #b45309;
  border: 1px solid #fde68a;
}

.deadline-countdown-chip.ON_TRACK {
  background: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
}

.chip-icon {
  width: 12px;
  height: 12px;
}

.stream-deadline-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8fafc;
  padding: 0.45rem 0.65rem;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  font-size: 0.775rem;
}

.deadline-title {
  color: #64748b;
  font-weight: 500;
}

.deadline-time {
  color: #0f172a;
  font-weight: 600;
}

.btn-overdue {
  background: #dc2626 !important;
  border-color: #b91c1c !important;
}

.btn-overdue:hover {
  background: #b91c1c !important;
}

.progress-section { display: flex; flex-direction: column; gap: 0.35rem; }
.progress-labels { display: flex; justify-content: space-between; font-size: 0.78rem; color: var(--text-secondary, #475569); }
.progress-bar-bg { width: 100%; height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden; }
.progress-bar-fill { height: 100%; background: #0284c7; border-radius: 4px; }
.stream-meta-row { display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--text-muted, #64748b); }

/* =================================================================== */
/* MODAL ARCHITECTURE: FIXED HEADER + SCROLLABLE CONTENT + FIXED FOOTER */
/* =================================================================== */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  padding: 10px;
  box-sizing: border-box;
}

.modal-card {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden;
}

.modal-card.full-modal {
  width: calc(100% - 20px);
  max-width: 1080px;
  max-height: calc(100vh - 20px);
  height: auto;
}

.modal-card.small-modal {
  width: calc(100% - 20px);
  max-width: 520px;
  max-height: calc(100vh - 20px);
}

.modal-card.preview-modal {
  width: calc(100% - 20px);
  max-width: 800px;
  max-height: calc(100vh - 20px);
}

/* Modal Header: Fixed/Sticky */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border-subtle, #e2e8f0);
  background: #ffffff;
  flex-shrink: 0;
  gap: 0.75rem;
}

.header-main-col {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-width: 0;
  flex: 1;
}

.header-tag-line {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.class-badge {
  background: #e0f2fe;
  color: #0369a1;
  font-weight: 700;
  font-size: 0.78rem;
  padding: 0.2rem 0.55rem;
  border-radius: 4px;
}

.subject-badge {
  background: #f1f5f9;
  color: #334155;
  font-size: 0.78rem;
  font-weight: 600;
  padding: 0.2rem 0.55rem;
  border-radius: 4px;
}

.modal-exam-name {
  font-size: 1.25rem;
  font-weight: 800;
  margin: 0;
  color: var(--text-primary, #0f172a);
  word-break: break-word;
  line-height: 1.3;
}

.modal-close-btn {
  background: none;
  border: none;
  font-size: 1.8rem;
  line-height: 1;
  cursor: pointer;
  color: var(--text-muted, #64748b);
  min-width: 44px;
  min-height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  flex-shrink: 0;
  transition: background-color 0.2s, color 0.2s;
}

.modal-close-btn:hover {
  background-color: var(--bg-surface-secondary, #f8fafc);
  color: var(--text-primary, #0f172a);
}

/* Modal Content Area: Scrollable */
.modal-scroll-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 1.25rem;
  -webkit-overflow-scrolling: touch;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Compact Alerts */
.alert-box-compact {
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.85rem;
}
.alert-box-compact.info {
  background: #e0f2fe;
  border: 1px solid #bae6fd;
  color: #0369a1;
}
.alert-box-compact.warning {
  background: #fef3c7;
  border: 1px solid #fde68a;
  color: #92400e;
}
.alert-box-compact.danger {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
}
.alert-box-small.danger {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.78rem;
}
.overdue-text {
  color: #dc2626 !important;
  font-weight: 600;
}
.deadline-instructions-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.85rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}
.deadline-instructions-card.is-overdue {
  background: #fef2f2;
  border-color: #fecaca;
}
.deadline-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.deadline-info {
  display: flex;
  gap: 0.4rem;
  font-size: 0.85rem;
}
.meta-label {
  color: #64748b;
  font-weight: 500;
}
.meta-date {
  color: #0f172a;
  font-weight: 700;
}
.deadline-countdown-badge {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
}
.deadline-countdown-badge.OVERDUE {
  background: #fee2e2;
  color: #b91c1c;
}
.deadline-countdown-badge.APPROACHING {
  background: #fef3c7;
  color: #92400e;
}
.deadline-countdown-badge.ON_TRACK {
  background: #e0e7ff;
  color: #4338ca;
}
.instructions-block {
  border-top: 1px dashed #cbd5e1;
  padding-top: 0.5rem;
  font-size: 0.8125rem;
  line-height: 1.4;
}
.instructions-title {
  font-weight: 700;
  color: #334155;
  display: block;
  margin-bottom: 0.15rem;
}
.instructions-content {
  margin: 0;
  color: #475569;
}
.alert-compact-title {
  font-weight: 700;
  font-size: 0.9rem;
  margin-bottom: 0.2rem;
}
.alert-compact-desc {
  margin: 0;
  line-height: 1.4;
  word-break: break-word;
}

/* KPI Summary Grid */
.roster-summary-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0.5rem;
  background: var(--bg-surface-secondary, #f8fafc);
  border: 1px solid var(--border-subtle, #e2e8f0);
  padding: 0.75rem;
  border-radius: 8px;
}

.kpi-box {
  text-align: center;
  padding: 0.35rem 0.25rem;
}

.kpi-label {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted, #64748b);
  display: block;
}

.kpi-value {
  font-size: 1.25rem;
  font-weight: 800;
  display: block;
  margin-top: 0.1rem;
}

.roster-data-wrap {
  width: 100%;
}

/* Desktop Table View */
.desktop-table-container {
  display: block;
  width: 100%;
  overflow-x: auto;
  border: 1px solid var(--border-subtle, #e2e8f0);
  border-radius: 8px;
}

.roster-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.88rem;
  min-width: 720px;
}

.roster-table th {
  background: var(--bg-surface-secondary, #f8fafc);
  padding: 0.75rem 0.85rem;
  font-weight: 700;
  color: var(--text-secondary, #475569);
  border-bottom: 1px solid var(--border-subtle, #e2e8f0);
  position: sticky;
  top: 0;
  z-index: 5;
}

.roster-table td {
  padding: 0.75rem 0.85rem;
  border-bottom: 1px solid var(--border-subtle, #e2e8f0);
  vertical-align: middle;
}

.roster-select, .roster-mark-input, .roster-remark-input {
  padding: 0.45rem 0.65rem;
  border: 1px solid var(--border-medium, #cbd5e1);
  border-radius: 4px;
  font-size: 0.85rem;
  color: var(--text-primary, #0f172a);
  box-sizing: border-box;
}
.roster-mark-input { width: 90px; font-weight: 700; }
.roster-remark-input { width: 100%; max-width: 180px; }

/* Grade Badges */
.grade-pill {
  font-weight: 800;
  font-size: 0.82rem;
  padding: 0.2rem 0.55rem;
  border-radius: 4px;
  display: inline-block;
  letter-spacing: 0.03em;
}
.grade-pill.lg {
  font-size: 0.95rem;
  padding: 0.25rem 0.75rem;
}
.grade-pill.a-plus, .grade-pill.a { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
.grade-pill.b { background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; }
.grade-pill.c { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
.grade-pill.d { background: #ffedd5; color: #c2410c; border: 1px solid #fed7aa; }
.grade-pill.f, .grade-pill.absent { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }
.grade-pill.empty { background: #f1f5f9; color: #94a3b8; border: 1px solid #e2e8f0; }

.paper-upload-cell { display: flex; align-items: center; gap: 0.4rem; }
.uploaded-paper-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}
.paper-icon { width: 1rem; height: 1rem; color: #16a34a; flex-shrink: 0; }
.paper-name-btn {
  background: none;
  border: none;
  color: #15803d;
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
  text-decoration: underline;
}
.paper-del-btn {
  background: none;
  border: none;
  color: #ef4444;
  font-size: 1.1rem;
  cursor: pointer;
  line-height: 1;
}
.upload-paper-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.45rem 0.75rem;
  background: #f8fafc;
  border: 1px dashed #cbd5e1;
  border-radius: 6px;
  font-size: 0.78rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  box-sizing: border-box;
}

/* =================================================================== */
/* MOBILE STUDENT CARDS (<= 768px)                                     */
/* =================================================================== */
.mobile-student-cards-list {
  display: none;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
}

.mobile-student-entry-card {
  background: #ffffff;
  border: 1px solid var(--border-medium, #cbd5e1);
  border-radius: 10px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  box-sizing: border-box;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.m-card-header {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
}

.m-student-index {
  font-size: 0.78rem;
  font-weight: 800;
  background: #f1f5f9;
  color: #475569;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  flex-shrink: 0;
}

.m-student-identity {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.m-student-name {
  font-size: 1rem;
  font-weight: 800;
  color: var(--text-primary, #0f172a);
  margin: 0;
  word-break: break-word;
  line-height: 1.3;
}

.m-student-adm {
  font-size: 0.78rem;
  color: var(--text-muted, #64748b);
}

.m-student-adm code {
  font-family: monospace;
  background: #f8fafc;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  color: #334155;
  font-weight: 600;
}

.m-card-divider {
  height: 1px;
  background-color: var(--border-subtle, #e2e8f0);
}

.m-field-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.m-field-label {
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
  color: var(--text-muted, #64748b);
  letter-spacing: 0.04em;
}

.m-select-input {
  width: 100%;
  padding: 0.65rem 0.75rem;
  border: 1px solid var(--border-medium, #cbd5e1);
  border-radius: 6px;
  background: var(--bg-surface, #ffffff);
  font-size: 0.9rem;
  color: var(--text-primary, #0f172a);
  min-height: 44px;
  box-sizing: border-box;
}

.m-marks-input-row {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.m-marks-input {
  width: 120px;
  padding: 0.65rem 0.75rem;
  font-size: 1.1rem;
  font-weight: 800;
  border: 1px solid var(--border-medium, #cbd5e1);
  border-radius: 6px;
  background: #ffffff;
  color: var(--text-primary, #0f172a);
  min-height: 44px;
  box-sizing: border-box;
  text-align: center;
}

.m-max-marks-label {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-secondary, #475569);
}

.m-absent-notice {
  padding: 0.65rem 0.75rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  color: #991b1b;
  font-size: 0.85rem;
}

.m-grade-display {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.m-grade-subtext {
  font-size: 0.82rem;
  color: var(--text-muted, #64748b);
  font-weight: 600;
}

.m-paper-attached-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.65rem 0.75rem;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 6px;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.m-paper-info {
  display: flex;
  align-items: center;
  min-width: 0;
  flex: 1;
}

.m-paper-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: #15803d;
  word-break: break-all;
}

.m-paper-actions {
  display: flex;
  gap: 0.4rem;
}

.m-no-paper-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0.75rem;
  background: var(--bg-surface-secondary, #f8fafc);
  border: 1px dashed var(--border-medium, #cbd5e1);
  border-radius: 6px;
  gap: 0.5rem;
}

.m-no-paper-text {
  font-size: 0.82rem;
  color: var(--text-muted, #64748b);
}

.m-upload-btn {
  padding: 0.45rem 0.75rem;
  min-height: 38px;
  font-size: 0.82rem;
  cursor: pointer;
}

.m-textarea {
  width: 100%;
  padding: 0.65rem 0.75rem;
  border: 1px solid var(--border-medium, #cbd5e1);
  border-radius: 6px;
  font-size: 0.88rem;
  background: var(--bg-surface, #ffffff);
  color: var(--text-primary, #0f172a);
  resize: vertical;
  min-height: 60px;
  box-sizing: border-box;
  line-height: 1.4;
}

/* Modal Footer: Fixed/Sticky */
.modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.85rem 1.25rem;
  border-top: 1px solid var(--border-subtle, #e2e8f0);
  background: #ffffff;
  flex-shrink: 0;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.footer-status-msg {
  display: flex;
  align-items: center;
}

.footer-action-buttons {
  display: flex;
  gap: 0.65rem;
  flex-wrap: wrap;
}

.pending-warning {
  font-size: 0.85rem;
  color: #b91c1c;
  font-weight: 600;
}

.confirm-intro {
  font-size: 0.9rem;
  margin-top: 0;
}

.confirm-box {
  background: var(--bg-surface-secondary, #f8fafc);
  padding: 0.85rem;
  border-radius: 6px;
  border: 1px solid var(--border-subtle, #e2e8f0);
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.88rem;
}

.preview-scroll-body {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 280px;
  max-height: 520px;
}
.image-preview-box { max-width: 100%; text-align: center; }
.preview-img { max-width: 100%; max-height: 480px; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.pdf-iframe { width: 100%; height: 460px; border: 1px solid var(--border-medium, #cbd5e1); border-radius: 6px; }

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.55rem 1rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s;
}
.btn-touch { min-height: 44px; }
.btn-primary { background: #0284c7; color: #ffffff; }
.btn-primary:hover:not(:disabled) { background: #0369a1; }
.btn-outline { background: #ffffff; border-color: var(--border-medium, #cbd5e1); color: var(--text-primary, #0f172a); }
.btn-outline:hover:not(:disabled) { background: #f8fafc; }
.btn-outline-danger { background: #fff; border-color: #fca5a5; color: #dc2626; }
.btn-outline-danger:hover { background: #fef2f2; }
.btn-xs { padding: 0.3rem 0.55rem; font-size: 0.75rem; min-height: 32px; }
.btn-block { width: 100%; }
.btn:disabled { opacity: 0.55; cursor: not-allowed; }

.loading-box, .empty-box {
  padding: 3rem 1rem;
  text-align: center;
  color: var(--text-muted, #64748b);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}
.empty-icon { width: 48px; height: 48px; color: #94a3b8; }
.empty-title { font-size: 1.1rem; font-weight: 700; margin: 0; color: var(--text-primary, #0f172a); }
.empty-desc { font-size: 0.85rem; margin: 0; }
.loading-state {
  padding: 2.5rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.85rem;
  color: var(--text-muted, #64748b);
}
.spinner { width: 32px; height: 32px; border: 3px solid var(--border-subtle, #e2e8f0); border-top-color: #0284c7; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }

/* =================================================================== */
/* RESPONSIVE BREAKPOINTS (320px to 1920px)                            */
/* =================================================================== */
@media (max-width: 1024px) {
  .filters-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .desktop-table-container {
    display: none;
  }
  .mobile-student-cards-list {
    display: flex;
  }
  .roster-summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .kpi-max-box {
    grid-column: 1 / -1;
  }
  .modal-card.full-modal {
    width: calc(100% - 16px);
    max-height: calc(100dvh - 16px);
  }
  .modal-header {
    padding: 0.85rem 1rem;
  }
  .modal-scroll-body {
    padding: 1rem 0.85rem;
  }
  .modal-footer {
    padding: 0.85rem 1rem;
    flex-direction: column;
    align-items: stretch;
  }
  .footer-action-buttons {
    flex-direction: column;
    width: 100%;
  }
  .btn-footer-item {
    width: 100%;
  }
  .streams-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .filters-grid {
    grid-template-columns: 1fr;
  }
  .modal-exam-name {
    font-size: 1.1rem;
  }
}

@media (max-width: 380px) {
  .m-marks-input {
    width: 90px;
  }
}
</style>
