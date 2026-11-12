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
    showNotification('success', res.message || 'Draft saved successfully in database.');
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
        <svg v-if="notification.type === 'success'" class="toast-icon" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        <svg v-else class="toast-icon" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
        <span>{{ notification.message }}</span>
        <button class="toast-close" aria-label="Dismiss notification" @click="notification = null">&times;</button>
      </div>
    </div>

    <!-- Page Header -->
    <div class="page-header">
      <div class="header-titles">
        <div class="somroyal-tag">
          <svg class="crown-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M5 16L3 5l5.5 5L12 4l3.5 6L21 5l-2 11H5m14 3c0 .6-.4 1-1 1H6c-.6 0-1-.4-1-1v-1h14v1z"/>
          </svg>
          <span>EXAMINATIONS &amp; EVALUATIONS &bull; MARKS ENTRY</span>
        </div>
        <h1 class="page-title">Exams &amp; Marks Entry</h1>
        <p class="page-subtitle">
          Create quizzes for assigned classes, enter student marks, attach paper evidence, and submit official result sheets to Administration.
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
          <span>Create New Quiz</span>
        </button>
      </div>
    </div>

    <!-- Filters Bar -->
    <div class="filters-card">
      <div class="filters-grid">
        <div class="form-group">
          <label class="form-label">Academic Year</label>
          <select v-model="selectedYear" class="form-select">
            <option value="ALL">All Academic Years ({{ availableYears.length }})</option>
            <option v-for="yr in availableYears" :key="yr" :value="yr">{{ yr }}</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Assigned Class</label>
          <select v-model="selectedClass" class="form-select">
            <option value="ALL">All Assigned Classes ({{ availableClasses.length }})</option>
            <option v-for="c in availableClasses" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Assigned Subject</label>
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
        @click="activeTab === 'active'"
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
        @click="activeTab === 'history'"
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
    <div v-if="isLoading" class="state-card loading">
      <div class="spinner-ring" />
      <span class="loading-label">Loading examination streams from database...</span>
    </div>

    <!-- Empty State -->
    <div v-else-if="displayedAssignments.length === 0" class="state-card empty">
      <div class="empty-icon-circle">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>
      <h3 class="state-title">
        {{ activeTab === 'active' ? 'No Pending Result Entry Tasks' : 'No Submitted Result Sheets' }}
      </h3>
      <p class="state-desc">
        {{ activeTab === 'active' ? 'All your assigned subject results have been completed and submitted to Administration.' : 'Submitted exam result sheets and admin reviews will be preserved here permanently.' }}
      </p>
      <button
        v-if="activeTab === 'active'"
        type="button"
        class="btn-create-exam"
        style="margin-top: 0.5rem;"
        @click="isCreateModalOpen = true"
      >
        + Create New Quiz
      </button>
    </div>

    <!-- Streams Grid (Responsive Cards) -->
    <div v-else class="streams-grid">
      <div
        v-for="item in displayedAssignments"
        :key="item.exam_id"
        class="stream-card"
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
            <h3 class="exam-title">{{ item.exam_name }}</h3>
            <span class="exam-scope">
              {{ item.class_name }}<template v-if="item.class_section"> (Sec {{ item.class_section }})</template> &bull; {{ item.subject_name }}
            </span>
          </div>
          <ResultStatusBadge :status="item.status" />
        </div>

        <!-- Overdue Notice in Card -->
        <div v-if="item.is_overdue && item.status !== 'SUBMITTED' && item.status !== 'APPROVED' && item.status !== 'RELEASED'" class="alert-box-small danger">
          <strong>⚠️ Submissions Overdue:</strong> Deadline passed ({{ item.remaining_time_human }}). Contact School Admin for an extension.
        </div>

        <!-- Returned Warning Alert -->
        <div v-else-if="item.status === 'RETURNED'" class="alert-box-small warning">
          <strong>Returned for Correction:</strong> {{ item.return_reason || 'Please review scores and resubmit.' }}
        </div>

        <!-- Deadline row -->
        <div v-if="item.result_submission_deadline" class="stream-deadline-bar">
          <span class="deadline-title">Deadline:</span>
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
          <span>Passing Marks: <strong>{{ item.pass_marks }}</strong></span>
        </div>

        <div class="stream-actions">
          <button
            class="btn-open-roster"
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

    <!-- ROSTER ENTRY MODAL -->
    <div v-if="isModalOpen && activeAssignment" class="modal-backdrop" @click="isModalOpen = false">
      <div class="modal-card full-modal" @click.stop>
        <!-- Modal Header -->
        <header class="modal-header">
          <div class="header-main-col">
            <div class="header-tag-line">
              <span class="class-badge-pill">{{ activeAssignment.class_name }}</span>
              <span class="subject-badge-pill">{{ activeAssignment.subject_name }}</span>
              <ResultStatusBadge :status="activeAssignment.status" />
            </div>
            <h2 class="modal-exam-name">{{ activeAssignment.exam_name }}</h2>
          </div>
          <button
            class="modal-close"
            aria-label="Close modal"
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
                <span class="meta-label">Submission Deadline:</span>
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
            <div class="alert-compact-title">⚠️ Submission Deadline Passed</div>
            <p class="alert-compact-desc">
              The deadline for this assessment passed ({{ activeAssignment.remaining_time_human }}). Mark modifications and submissions are locked.
            </p>
          </div>

          <!-- Submission Locked Alert -->
          <div v-else-if="isSubmittedOrApproved" class="alert-box-compact info">
            <div class="alert-compact-title">🔒 Submission Locked</div>
            <p class="alert-compact-desc">
              Marks have been submitted to Administration. Scores can only be modified if Administration returns them for correction.
            </p>
          </div>

          <!-- KPI Summary Strip -->
          <div class="roster-summary-grid">
            <div class="kpi-box">
              <span class="kpi-label">TOTAL</span>
              <span class="kpi-value text-navy">{{ rosterStudents.length }}</span>
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
              <span class="kpi-value text-navy">{{ activeAssignment.max_marks }}</span>
            </div>
          </div>

          <!-- Loading Indicator -->
          <div v-if="isRosterLoading" class="state-container loading">
            <div class="spinner-ring" />
            <span class="loading-label">Loading student roster and scores from database...</span>
          </div>

          <div v-else class="roster-data-wrap">
            <!-- 1. Desktop Table View -->
            <div class="desktop-table-container">
              <table class="somroyal-table">
                <thead>
                  <tr>
                    <th style="width: 40px;">#</th>
                    <th>Student Name</th>
                    <th>Admission #</th>
                    <th style="width: 125px;">Attendance</th>
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
                    <td class="font-bold text-navy">{{ std.student_name }}</td>
                    <td><code class="adm-code">{{ std.admission_number }}</code></td>
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
                      <span v-else class="text-muted font-semibold">&ndash;</span>
                    </td>
                    <td style="text-align: center;">
                      <span
                        class="grade-pill"
                        :class="{
                          'grade-pass': ['A+', 'A', 'B', 'C', 'D'].includes(std.grade || ''),
                          'grade-fail': std.grade === 'F',
                          'grade-abs': std.grade === 'ABSENT' || std.grade === 'EXCUSED'
                        }"
                      >
                        {{ std.grade || '—' }}
                      </span>
                    </td>
                    <td>
                      <input
                        v-if="std.attendance_status !== 'PRESENT'"
                        v-model="std.absence_reason"
                        type="text"
                        class="roster-text-input"
                        placeholder="Reason for absence..."
                        :disabled="isLocked"
                      />
                      <span v-else class="text-muted font-normal">&ndash;</span>
                    </td>
                    <td>
                      <input
                        v-model="std.complaint"
                        type="text"
                        class="roster-text-input"
                        placeholder="Complaint / dispute..."
                        :disabled="isLocked"
                      />
                    </td>
                    <td>
                      <input
                        v-model="std.remarks"
                        type="text"
                        class="roster-text-input"
                        placeholder="Remarks..."
                        :disabled="isLocked"
                      />
                    </td>
                    <td>
                      <!-- Paper Upload / Preview -->
                      <div class="paper-action-cell">
                        <div v-if="std.paper_file_path" class="paper-badge-group">
                          <button
                            type="button"
                            class="btn-view-paper"
                            title="Preview uploaded exam paper"
                            @click="handlePreviewPaper(std)"
                          >
                            📄 View
                          </button>
                          <button
                            v-if="!isLocked"
                            type="button"
                            class="btn-delete-paper"
                            title="Delete exam paper"
                            @click="handleDeletePaper(std)"
                          >
                            &times;
                          </button>
                        </div>
                        <label v-else-if="!isLocked" class="btn-upload-paper">
                          <input
                            type="file"
                            accept=".pdf,.png,.jpg,.jpeg"
                            style="display: none;"
                            @change="handlePaperUpload(std, $event)"
                          />
                          <span>{{ std.isUploadingPaper ? '...' : '+ Paper' }}</span>
                        </label>
                        <span v-else class="text-muted">&ndash;</span>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- 2. Mobile Roster Cards -->
            <div class="mobile-roster-list">
              <div
                v-for="(std, idx) in rosterStudents"
                :key="std.student_id"
                class="mobile-std-card"
              >
                <div class="m-card-top-row">
                  <div class="m-std-info">
                    <span class="m-idx">#{{ idx + 1 }}</span>
                    <div>
                      <h4 class="m-name">{{ std.student_name }}</h4>
                      <code class="adm-code">{{ std.admission_number }}</code>
                    </div>
                  </div>
                  <span
                    class="grade-pill"
                    :class="{
                      'grade-pass': ['A+', 'A', 'B', 'C', 'D'].includes(std.grade || ''),
                      'grade-fail': std.grade === 'F',
                      'grade-abs': std.grade === 'ABSENT' || std.grade === 'EXCUSED'
                    }"
                  >
                    Grade: {{ std.grade || '—' }}
                  </span>
                </div>

                <div class="m-fields-grid">
                  <div class="m-field">
                    <label class="m-field-lbl">Attendance</label>
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
                  </div>

                  <div class="m-field">
                    <label class="m-field-lbl">Score (/{{ activeAssignment.max_marks }})</label>
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
                    <span v-else class="text-muted">&ndash;</span>
                  </div>
                </div>

                <div v-if="std.attendance_status !== 'PRESENT'" class="m-field">
                  <label class="m-field-lbl text-rose">Absence Reason</label>
                  <input
                    v-model="std.absence_reason"
                    type="text"
                    class="roster-text-input"
                    placeholder="Specify why student was absent..."
                    :disabled="isLocked"
                  />
                </div>

                <div class="m-fields-grid">
                  <div class="m-field">
                    <label class="m-field-lbl">Student Complaint</label>
                    <input
                      v-model="std.complaint"
                      type="text"
                      class="roster-text-input"
                      placeholder="Complaint notes..."
                      :disabled="isLocked"
                    />
                  </div>
                  <div class="m-field">
                    <label class="m-field-lbl">Remarks</label>
                    <input
                      v-model="std.remarks"
                      type="text"
                      class="roster-text-input"
                      placeholder="Remarks..."
                      :disabled="isLocked"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Notes Section for Admin Submission -->
            <div class="notes-section">
              <label class="notes-lbl">Teacher Remarks &amp; Submission Notes for School Administration</label>
              <textarea
                v-model="teacherNotes"
                class="notes-textarea"
                rows="2"
                placeholder="Optional notes or explanations submitted to Administration along with this result sheet..."
                :disabled="isLocked"
              />
            </div>
          </div>
        </div>

        <!-- Sticky Modal Footer -->
        <footer class="modal-footer">
          <button class="btn-cancel" @click="isModalOpen = false">
            Close
          </button>

          <button
            v-if="!isLocked"
            type="button"
            class="btn-save-draft"
            :disabled="isSaving"
            @click="handleSaveDraft"
          >
            {{ isSaving ? 'Saving Draft...' : 'Save Draft' }}
          </button>

          <button
            v-if="!isLocked"
            type="button"
            class="btn-submit-admin"
            :disabled="isSubmitting || !isReadyToSubmit"
            @click="triggerSubmit"
          >
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
            <span>Submit to Administration</span>
          </button>
        </footer>
      </div>
    </div>

    <!-- CONFIRM SUBMISSION MODAL -->
    <div v-if="isConfirmSubmitOpen" class="modal-backdrop" @click="isConfirmSubmitOpen = false">
      <div class="modal-card small" @click.stop>
        <div class="confirm-modal-header">
          <div class="confirm-icon-box">
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
          </div>
          <h3 class="confirm-title">Submit Results to Administration</h3>
          <p class="confirm-subtitle">Verify your marks entry before committing to official administrative review.</p>
        </div>

        <div class="confirm-modal-body">
          <div class="confirm-checklist">
            <div class="check-item">
              <span>Total Students:</span>
              <strong>{{ rosterStudents.length }}</strong>
            </div>
            <div class="check-item">
              <span>Completed Marks:</span>
              <strong class="text-emerald">{{ completedCount }}</strong>
            </div>
            <div class="check-item">
              <span>Absent Students:</span>
              <strong class="text-amber">{{ absentStudentsCount }}</strong>
            </div>
            <div class="check-item">
              <span>Student Complaints:</span>
              <strong class="text-rose">{{ recordedComplaintsCount }}</strong>
            </div>
          </div>

          <div class="warning-lock-note">
            🔒 <strong>Important:</strong> Once submitted, marks become locked and cannot be edited unless returned by School Administration.
          </div>
        </div>

        <div class="confirm-modal-footer">
          <button class="btn-cancel" @click="isConfirmSubmitOpen = false">Cancel</button>
          <button class="btn-confirm-submit" :disabled="isSubmitting" @click="handleConfirmSubmit">
            {{ isSubmitting ? 'Submitting...' : 'Yes, Submit Officially' }}
          </button>
        </div>
      </div>
    </div>

    <!-- PAPER PREVIEW MODAL -->
    <div v-if="isPreviewModalOpen" class="modal-backdrop" @click="closePreviewModal">
      <div class="modal-card" style="max-width: 800px;" @click.stop>
        <div class="modal-header">
          <h3 class="modal-exam-name">Exam Paper Document: {{ previewStudent?.student_name }}</h3>
          <button class="modal-close" @click="closePreviewModal">&times;</button>
        </div>
        <div class="modal-scroll-body" style="padding: 1.5rem; text-align: center;">
          <iframe
            v-if="previewBlobUrl && previewStudent?.paper_mime_type === 'application/pdf'"
            :src="previewBlobUrl"
            style="width: 100%; height: 500px; border: none; border-radius: 8px;"
          />
          <img
            v-else-if="previewBlobUrl"
            :src="previewBlobUrl"
            style="max-width: 100%; max-height: 500px; border-radius: 8px;"
            alt="Exam document"
          />
        </div>
      </div>
    </div>

    <!-- CREATE QUIZ MODAL COMPONENT -->
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
  max-width: 1360px;
  margin: 0 auto;
  width: 100%;
}

/* Toast */
.toast-banner {
  padding: 0.85rem 1.25rem;
  border-radius: 12px;
  font-size: 0.86rem;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.toast-banner.success {
  background: #ECFDF5;
  border: 1px solid #A7F3D0;
  color: #065F46;
}

.toast-banner.error {
  background: #FEF2F2;
  border: 1px solid #FCA5A5;
  color: #991B1B;
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.toast-icon { width: 18px; height: 18px; flex-shrink: 0; }
.toast-close { margin-left: auto; background: none; border: none; font-size: 1.2rem; cursor: pointer; color: inherit; }

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1.25rem;
  flex-wrap: wrap;
}

.somroyal-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #10B981;
  text-transform: uppercase;
  margin-bottom: 0.35rem;
}

.crown-icon { width: 14px; height: 14px; color: #F59E0B; }
.page-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 0.88rem;
  color: #64748B;
  margin-top: 0.25rem;
  line-height: 1.5;
  max-width: 780px;
}

.btn-create-exam {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  background: #1E3A8A;
  color: #FFFFFF;
  border: none;
  padding: 0.6rem 1.15rem;
  border-radius: 10px;
  font-size: 0.84rem;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(30, 58, 138, 0.3);
  transition: all 0.2s ease;
}

.btn-create-exam:hover { background: #1E40AF; }
.btn-create-icon { width: 16px; height: 16px; }

/* Filters */
.filters-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 1.25rem 1.5rem;
  box-shadow: 0 2px 6px rgba(10, 25, 47, 0.03);
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-label {
  font-size: 0.72rem;
  font-weight: 700;
  color: #64748B;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.form-select {
  background: #F8FAFC;
  border: 1px solid #CBD5E1;
  color: #0A192F;
  padding: 0.55rem 0.75rem;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 600;
  outline: none;
}

/* Workflow Tabs */
.workflow-tabs-container {
  display: flex;
  gap: 0.5rem;
  border-bottom: 2px solid #E2E8F0;
  padding-bottom: 0.2rem;
}

.workflow-tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1.15rem;
  font-size: 0.88rem;
  font-weight: 700;
  color: #64748B;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  margin-bottom: -2px;
  transition: all 0.2s ease;
}

.workflow-tab-btn:hover { color: #0A192F; }

.workflow-tab-btn.active {
  color: #0A192F;
  border-bottom-color: #10B981;
}

.tab-icon { width: 18px; height: 18px; }

.tab-badge {
  font-size: 0.72rem;
  font-weight: 800;
  padding: 0.15rem 0.5rem;
  border-radius: 12px;
}

.tab-badge.badge-primary {
  background: #ECFDF5;
  color: #059669;
}

.tab-badge.badge-empty {
  background: #F1F5F9;
  color: #94A3B8;
}

.tab-badge.badge-neutral {
  background: #EFF6FF;
  color: #1E40AF;
}

/* Streams Grid */
.streams-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1.25rem;
}

.stream-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  box-shadow: 0 2px 6px rgba(10, 25, 47, 0.03);
  transition: all 0.2s ease;
}

.stream-card:hover {
  border-color: #CBD5E1;
  box-shadow: 0 6px 18px rgba(10, 25, 47, 0.06);
}

.stream-card.card-overdue {
  border-left: 4px solid #EF4444;
}

.stream-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
}

.stream-title-col {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  min-width: 0;
}

.stream-type-line {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.exam-type-pill {
  font-size: 0.68rem;
  font-weight: 800;
  background: #0A192F;
  color: #FFFFFF;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  letter-spacing: 0.04em;
}

.deadline-countdown-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.68rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 12px;
}

.deadline-countdown-chip.OVERDUE {
  background: #FEF2F2;
  color: #DC2626;
  border: 1px solid #FECACA;
}

.deadline-countdown-chip.DUE_SOON {
  background: #FEF3C7;
  color: #D97706;
  border: 1px solid #FDE68A;
}

.deadline-countdown-chip.ON_TIME {
  background: #ECFDF5;
  color: #059669;
  border: 1px solid #A7F3D0;
}

.chip-icon { width: 12px; height: 12px; }

.exam-title {
  font-size: 1.1rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
}

.exam-scope {
  font-size: 0.78rem;
  color: #64748B;
  font-weight: 600;
}

.alert-box-small {
  padding: 0.6rem 0.85rem;
  border-radius: 8px;
  font-size: 0.76rem;
  line-height: 1.4;
}

.alert-box-small.danger {
  background: #FEF2F2;
  border: 1px solid #FCA5A5;
  color: #991B1B;
}

.alert-box-small.warning {
  background: #FEF3C7;
  border: 1px solid #FDE68A;
  color: #92400E;
}

.stream-deadline-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.74rem;
  background: #F8FAFC;
  padding: 0.45rem 0.75rem;
  border-radius: 6px;
  color: #64748B;
}

.progress-section {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.progress-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.74rem;
  color: #64748B;
}

.progress-bar-bg {
  width: 100%;
  height: 6px;
  background: #E2E8F0;
  border-radius: 10px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #10B981, #059669);
  border-radius: 10px;
}

.stream-meta-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.76rem;
  color: #64748B;
  border-top: 1px solid #F1F5F9;
  padding-top: 0.5rem;
}

.btn-open-roster {
  width: 100%;
  background: #0A192F;
  color: #FFFFFF;
  border: none;
  padding: 0.6rem 1rem;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-open-roster:hover { background: #10B981; }

/* Full Roster Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(10, 25, 47, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 60;
  padding: 1rem;
}

.modal-card.full-modal {
  background: #FFFFFF;
  border-radius: 20px;
  width: 100%;
  max-width: 1200px;
  max-height: 94vh;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 1.25rem 2rem;
  border-bottom: 1px solid #E2E8F0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #F8FAFC;
}

.header-tag-line {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.class-badge-pill, .subject-badge-pill {
  font-size: 0.72rem;
  font-weight: 800;
  background: #E2E8F0;
  color: #0A192F;
  padding: 0.15rem 0.55rem;
  border-radius: 4px;
}

.modal-exam-name {
  font-size: 1.35rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.75rem;
  color: #94A3B8;
  cursor: pointer;
}

.modal-close:hover { color: #0A192F; }

.modal-scroll-body {
  padding: 1.5rem 2rem;
  overflow-y: auto;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.deadline-instructions-card {
  background: #EFF6FF;
  border: 1px solid #BFDBFE;
  border-radius: 12px;
  padding: 1rem 1.25rem;
}

.deadline-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.meta-label { font-size: 0.76rem; color: #1E40AF; font-weight: 700; }
.meta-date { font-size: 0.84rem; font-weight: 800; color: #1E3A8A; margin-left: 0.35rem; }

.instructions-block {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px dashed #BFDBFE;
  font-size: 0.8rem;
  color: #1E3A8A;
}

.alert-box-compact {
  padding: 0.75rem 1rem;
  border-radius: 10px;
  font-size: 0.82rem;
}

.alert-box-compact.warning { background: #FEF3C7; border: 1px solid #FDE68A; color: #92400E; }
.alert-box-compact.danger { background: #FEF2F2; border: 1px solid #FCA5A5; color: #991B1B; }
.alert-box-compact.info { background: #F1F5F9; border: 1px solid #CBD5E1; color: #334155; }

.alert-compact-title { font-weight: 800; margin-bottom: 0.15rem; }
.alert-compact-desc { margin: 0; }

.roster-summary-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.75rem;
}

.kpi-box {
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 10px;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  text-align: center;
}

.kpi-box.kpi-max-box {
  background: #0A192F;
}

.kpi-box.kpi-max-box .kpi-label { color: #94A3B8; }
.kpi-box.kpi-max-box .kpi-value { color: #FFFFFF !important; }

.kpi-label {
  font-size: 0.62rem;
  font-weight: 800;
  color: #64748B;
  text-transform: uppercase;
}

.kpi-value {
  font-size: 1.35rem;
  font-weight: 900;
}

.text-navy { color: #0A192F !important; }
.text-emerald { color: #059669 !important; }
.text-rose { color: #DC2626 !important; }
.text-amber { color: #D97706 !important; }

.desktop-table-container {
  overflow-x: auto;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
}

.somroyal-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.86rem;
  text-align: left;
}

.somroyal-table thead {
  background: #0A192F;
  color: #FFFFFF;
}

.somroyal-table th {
  padding: 0.85rem 1rem;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #1E293B;
}

.somroyal-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #F1F5F9;
  color: #1E293B;
  vertical-align: middle;
}

.roster-select, .roster-mark-input, .roster-text-input {
  background: #F8FAFC;
  border: 1px solid #CBD5E1;
  padding: 0.35rem 0.55rem;
  border-radius: 6px;
  font-size: 0.82rem;
  color: #0A192F;
  outline: none;
}

.roster-mark-input {
  width: 70px;
  font-weight: 800;
  text-align: center;
}

.roster-text-input { width: 100%; }

.grade-pill {
  display: inline-block;
  font-size: 0.76rem;
  font-weight: 800;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
}

.grade-pill.grade-pass { background: #ECFDF5; color: #065F46; }
.grade-pill.grade-fail { background: #FEF2F2; color: #991B1B; }
.grade-pill.grade-abs { background: #F1F5F9; color: #64748B; }

.paper-badge-group {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.btn-view-paper {
  background: #EFF6FF;
  border: 1px solid #BFDBFE;
  color: #1E40AF;
  padding: 0.2rem 0.45rem;
  border-radius: 4px;
  font-size: 0.72rem;
  font-weight: 700;
  cursor: pointer;
}

.btn-delete-paper {
  background: #FEF2F2;
  border: 1px solid #FECACA;
  color: #DC2626;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
}

.btn-upload-paper {
  display: inline-block;
  background: #F1F5F9;
  border: 1px dashed #94A3B8;
  color: #475569;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.72rem;
  font-weight: 700;
  cursor: pointer;
}

.btn-upload-paper:hover { background: #E2E8F0; }

.notes-section {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.notes-lbl {
  font-size: 0.74rem;
  font-weight: 700;
  color: #0A192F;
}

.notes-textarea {
  background: #F8FAFC;
  border: 1px solid #CBD5E1;
  border-radius: 8px;
  padding: 0.6rem 0.75rem;
  font-size: 0.84rem;
  color: #0A192F;
  outline: none;
}

.modal-footer {
  padding: 1rem 2rem;
  background: #F8FAFC;
  border-top: 1px solid #E2E8F0;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-cancel {
  background: #FFFFFF;
  border: 1px solid #CBD5E1;
  color: #475569;
  padding: 0.55rem 1.15rem;
  border-radius: 8px;
  font-size: 0.84rem;
  font-weight: 700;
  cursor: pointer;
}

.btn-save-draft {
  background: #F1F5F9;
  border: 1px solid #CBD5E1;
  color: #0A192F;
  padding: 0.55rem 1.15rem;
  border-radius: 8px;
  font-size: 0.84rem;
  font-weight: 700;
  cursor: pointer;
}

.btn-submit-admin {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: #1E3A8A;
  border: none;
  color: #FFFFFF;
  padding: 0.55rem 1.25rem;
  border-radius: 8px;
  font-size: 0.84rem;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(30, 58, 138, 0.3);
}

.btn-submit-admin:hover:not(:disabled) { background: #1E40AF; }
.btn-submit-admin svg { width: 16px; height: 16px; }

/* Mobile Roster List */
.mobile-roster-list {
  display: none;
  flex-direction: column;
  gap: 1rem;
}

.mobile-std-card {
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.m-card-top-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.m-std-info {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.m-idx { font-size: 0.75rem; color: #94A3B8; font-weight: 700; }
.m-name { font-size: 0.95rem; font-weight: 800; color: #0A192F; margin: 0; }
.m-fields-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.65rem;
}

.m-field { display: flex; flex-direction: column; gap: 0.2rem; }
.m-field-lbl { font-size: 0.68rem; font-weight: 700; color: #64748B; }

/* Confirm Submit Modal */
.modal-card.small { max-width: 460px; }
.confirm-modal-header { padding: 1.5rem 1.5rem 0.5rem; text-align: center; }
.confirm-icon-box {
  width: 48px;
  height: 48px;
  background: #ECFDF5;
  color: #10B981;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 0.75rem;
}

.confirm-icon-box svg { width: 24px; height: 24px; }
.confirm-title { font-size: 1.25rem; font-weight: 800; color: #0A192F; margin: 0; }
.confirm-subtitle { font-size: 0.84rem; color: #64748B; margin-top: 0.25rem; }
.confirm-modal-body { padding: 1rem 1.5rem; display: flex; flex-direction: column; gap: 1rem; }
.confirm-checklist {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  background: #F8FAFC;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  border: 1px solid #E2E8F0;
  font-size: 0.84rem;
}

.check-item { display: flex; justify-content: space-between; }
.warning-lock-note {
  background: #FEF3C7;
  border: 1px solid #FDE68A;
  color: #92400E;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.8rem;
  line-height: 1.4;
}

.confirm-modal-footer {
  padding: 1rem 1.5rem;
  background: #F8FAFC;
  border-top: 1px solid #E2E8F0;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-confirm-submit {
  background: #1E3A8A;
  color: #FFFFFF;
  border: none;
  padding: 0.55rem 1.25rem;
  border-radius: 8px;
  font-size: 0.84rem;
  font-weight: 800;
  cursor: pointer;
}

.btn-confirm-submit:hover { background: #1E40AF; }

/* States */
.state-card {
  background: #FFFFFF;
  border-radius: 16px;
  border: 1px solid #E2E8F0;
  padding: 4rem 1.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.85rem;
}

.spinner-ring {
  width: 36px;
  height: 36px;
  border: 3px solid #E2E8F0;
  border-top-color: #10B981;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.loading-label { font-size: 0.88rem; color: #64748B; font-weight: 600; }
.empty-icon-circle {
  width: 56px;
  height: 56px;
  background: #F1F5F9;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94A3B8;
}

.empty-icon-circle svg { width: 28px; height: 28px; }
.state-title { font-size: 1.15rem; font-weight: 800; color: #0A192F; margin: 0; }
.state-desc { font-size: 0.86rem; color: #64748B; max-width: 500px; line-height: 1.5; margin: 0; }

@media (max-width: 1024px) {
  .filters-grid { grid-template-columns: 1fr; }
  .roster-summary-grid { grid-template-columns: repeat(4, 1fr); }
}

@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: stretch; }
  .btn-create-exam { width: 100%; justify-content: center; }
  .streams-grid { grid-template-columns: 1fr; }
  .desktop-table-container { display: none; }
  .mobile-roster-list { display: flex; }
  .roster-summary-grid { grid-template-columns: repeat(2, 1fr); }
  .modal-card.full-modal { border-radius: 14px; max-height: 98vh; }
  .modal-header, .modal-scroll-body, .modal-footer { padding-left: 1rem; padding-right: 1rem; }
  .modal-footer { flex-direction: column-reverse; }
  .btn-cancel, .btn-save-draft, .btn-submit-admin { width: 100%; justify-content: center; }
}
</style>
