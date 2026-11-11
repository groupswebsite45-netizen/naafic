<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { resultWorkflowService } from '../../../../services/resultWorkflowService';
import { examService } from '../../../../services/examService';
import {
  TeacherSubmissionItem,
  TeacherAccountabilitySummary,
  ResultFilterOptions,
  SubmissionReviewDetail,
} from '../../../../types/resultWorkflow';
import ResultStatusBadge from '../../../../components/results/ResultStatusBadge.vue';
import ResultReviewModal from '../../../../components/results/ResultReviewModal.vue';
import ReturnSubmissionModal from '../../../../components/results/ReturnSubmissionModal.vue';

const router = useRouter();

// Filter States
const academicYear = ref<string>('2025-2026');
const selectedExam = ref<string>('Final Examination 2026');
const selectedTeacherId = ref<number | ''>('');
const selectedClassId = ref<number | ''>('');
const selectedSubjectId = ref<number | ''>('');
const selectedStatus = ref<string>('');

// Data States
const filterOptions = ref<ResultFilterOptions | null>(null);
const submissions = ref<TeacherSubmissionItem[]>([]);
const teacherAccountability = ref<TeacherAccountabilitySummary | null>(null);
const isLoading = ref(true);
const isAccountabilityLoading = ref(false);

// Modal States
const isReviewModalOpen = ref(false);
const activeSubmission = ref<SubmissionReviewDetail | null>(null);
const isReviewLoading = ref(false);
const isReviewProcessing = ref(false);

const isReturnModalOpen = ref(false);
const isReturnProcessing = ref(false);

// Extend Deadline Modal State
const isExtendModalOpen = ref(false);
const extendTarget = ref<{ exam_id: number; exam_name: string; current_deadline?: string } | null>(null);
const extendForm = ref({
  new_deadline: '',
  reason: '',
});
const isExtending = ref(false);

// Reopen Submissions Modal State
const isReopenModalOpen = ref(false);
const reopenTarget = ref<{ exam_id: number; exam_name: string } | null>(null);
const reopenReason = ref('');
const isReopening = ref(false);

const notification = ref<{ type: 'success' | 'error'; message: string } | null>(null);

function showNotification(type: 'success' | 'error', message: string) {
  notification.value = { type, message };
  setTimeout(() => {
    notification.value = null;
  }, 6000);
}

// Telemetry & KPI Calculations
const summaryKPIs = computed(() => {
  const total = submissions.value.length;
  const submitted = submissions.value.filter((s) => s.status === 'SUBMITTED' || s.status === 'APPROVED' || s.status === 'RELEASED').length;
  const pending = submissions.value.filter((s) => s.status === 'DRAFT' || s.status === 'PARTIAL' || s.status === 'NOT_STARTED').length;
  const overdue = submissions.value.filter((s) => s.is_overdue && s.status !== 'SUBMITTED' && s.status !== 'APPROVED' && s.status !== 'RELEASED').length;
  const completionRate = total > 0 ? Math.round((submitted / total) * 100) : 0;
  return { total, submitted, pending, overdue, completionRate };
});

function openExtendModal(sub: TeacherSubmissionItem) {
  extendTarget.value = {
    exam_id: sub.exam_id,
    exam_name: sub.exam_name,
    current_deadline: sub.submission_deadline ? String(sub.submission_deadline) : undefined,
  };
  const base = sub.submission_deadline ? new Date(sub.submission_deadline) : new Date();
  const nextDate = new Date(base.getTime() + 14 * 24 * 60 * 60 * 1000);
  extendForm.value = {
    new_deadline: nextDate.toISOString().slice(0, 16),
    reason: '',
  };
  isExtendModalOpen.value = true;
}

function setExtendPreset(days: number) {
  const nextDate = new Date(Date.now() + days * 24 * 60 * 60 * 1000);
  extendForm.value.new_deadline = nextDate.toISOString().slice(0, 16);
}

async function handleConfirmExtend() {
  if (!extendTarget.value) return;
  if (!extendForm.value.new_deadline) {
    showNotification('error', 'Please choose a new submission deadline.');
    return;
  }
  if (!extendForm.value.reason.trim()) {
    showNotification('error', 'Please provide an audit reason for extending the deadline.');
    return;
  }

  isExtending.value = true;
  try {
    await examService.extendDeadline(extendTarget.value.exam_id, {
      new_deadline: new Date(extendForm.value.new_deadline).toISOString(),
      reason: extendForm.value.reason.trim(),
    });
    showNotification('success', 'Deadline extended successfully.');
    isExtendModalOpen.value = false;
    await loadSubmissions();
  } catch (err: any) {
    showNotification('error', err?.response?.data?.detail || 'Failed to extend deadline.');
  } finally {
    isExtending.value = false;
  }
}

function openReopenModal(sub: TeacherSubmissionItem) {
  reopenTarget.value = {
    exam_id: sub.exam_id,
    exam_name: sub.exam_name,
  };
  reopenReason.value = '';
  isReopenModalOpen.value = true;
}

async function handleConfirmReopen() {
  if (!reopenTarget.value) return;
  if (!reopenReason.value.trim()) {
    showNotification('error', 'Please provide a reason for reopening submissions.');
    return;
  }

  isReopening.value = true;
  try {
    await examService.reopenSubmissions(reopenTarget.value.exam_id, {
      reason: reopenReason.value.trim(),
    });
    showNotification('success', 'Examination submissions reopened successfully.');
    isReopenModalOpen.value = false;
    await loadSubmissions();
  } catch (err: any) {
    showNotification('error', err?.response?.data?.detail || 'Failed to reopen submissions.');
  } finally {
    isReopening.value = false;
  }
}

function formatDeadlineDisplay(val?: string | null) {
  if (!val) return '—';
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

// Load Filters
async function loadFilterOptions() {
  try {
    filterOptions.value = await resultWorkflowService.getFilterOptions(academicYear.value);
    if (!selectedExam.value && filterOptions.value?.exam_names?.length) {
      selectedExam.value = filterOptions.value.exam_names[0];
    }
  } catch (err: any) {
    showNotification('error', 'Failed to load filter options.');
  }
}

// Load Submissions
async function loadSubmissions() {
  isLoading.value = true;
  try {
    submissions.value = await resultWorkflowService.getTeacherSubmissions({
      academic_year: academicYear.value || undefined,
      exam_name: selectedExam.value || undefined,
      teacher_id: selectedTeacherId.value ? Number(selectedTeacherId.value) : undefined,
      class_id: selectedClassId.value ? Number(selectedClassId.value) : undefined,
      subject_id: selectedSubjectId.value ? Number(selectedSubjectId.value) : undefined,
      status: selectedStatus.value || undefined,
    });
  } catch (err: any) {
    showNotification('error', 'Failed to load teacher submissions.');
  } finally {
    isLoading.value = false;
  }
}

// Load Teacher Accountability if teacher is selected
async function loadTeacherAccountability() {
  if (!selectedTeacherId.value) {
    teacherAccountability.value = null;
    return;
  }
  isAccountabilityLoading.value = true;
  try {
    teacherAccountability.value = await resultWorkflowService.getTeacherAccountability(
      Number(selectedTeacherId.value),
      academicYear.value
    );
  } catch (err: any) {
    teacherAccountability.value = null;
  } finally {
    isAccountabilityLoading.value = false;
  }
}

// Review action
async function handleInspect(submission: TeacherSubmissionItem) {
  isReviewLoading.value = true;
  isReviewModalOpen.value = true;
  try {
    activeSubmission.value = await resultWorkflowService.getSubmissionDetail(submission.id);
  } catch (err: any) {
    showNotification('error', 'Failed to fetch submission details.');
    isReviewModalOpen.value = false;
  } finally {
    isReviewLoading.value = false;
  }
}

// Approve
async function handleApprove() {
  if (!activeSubmission.value) return;
  isReviewProcessing.value = true;
  try {
    const res = await resultWorkflowService.approveSubmission(activeSubmission.value.id);
    showNotification('success', res.message || 'Submission approved.');
    isReviewModalOpen.value = false;
    await Promise.all([loadSubmissions(), loadTeacherAccountability()]);
  } catch (err: any) {
    showNotification('error', err?.response?.data?.detail || 'Failed to approve submission.');
  } finally {
    isReviewProcessing.value = false;
  }
}

// Open Return Modal
function handleOpenReturn() {
  isReturnModalOpen.value = true;
}

// Confirm Return
async function handleConfirmReturn(reason: string) {
  if (!activeSubmission.value) return;
  isReturnProcessing.value = true;
  try {
    const res = await resultWorkflowService.returnSubmission(activeSubmission.value.id, reason);
    showNotification('success', res.message || 'Returned for correction.');
    isReturnModalOpen.value = false;
    isReviewModalOpen.value = false;
    await Promise.all([loadSubmissions(), loadTeacherAccountability()]);
  } catch (err: any) {
    showNotification('error', err?.response?.data?.detail || 'Failed to return submission.');
  } finally {
    isReturnProcessing.value = false;
  }
}

function formatDate(dateStr?: string | null) {
  if (!dateStr) return '—';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateStr;
  }
}

onMounted(async () => {
  await loadFilterOptions();
  await loadSubmissions();
});

watch([academicYear, selectedExam, selectedClassId, selectedSubjectId, selectedStatus], () => {
  loadSubmissions();
});

watch(selectedTeacherId, () => {
  loadSubmissions();
  loadTeacherAccountability();
});
</script>

<template>
  <div class="submissions-page">
    <!-- Top Header -->
    <div class="page-top-bar">
      <div>
        <div class="pre-title">ADMIN RESULT CONTROL</div>
        <h1 class="page-title">Teacher Submissions Monitoring</h1>
        <p class="page-sub">
          Monitor mark entries, draft completion, verify submissions, approve or return for teacher correction.
        </p>
      </div>

      <div class="top-nav-links">
        <button
          type="button"
          class="btn-nav"
          @click="router.push('/admin/exams/results')"
        >
          <svg class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          Class Result Overview
        </button>
      </div>
    </div>

    <!-- Notification -->
    <div v-if="notification" class="notification-banner" :class="notification.type">
      <span>{{ notification.message }}</span>
      <button type="button" class="notif-close" @click="notification = null">&times;</button>
    </div>

    <!-- Filters Strip -->
    <div class="filter-card">
      <div class="filters-grid">
        <!-- Academic Year -->
        <div class="filter-group">
          <label class="filter-label" for="academicYearFilter">ACADEMIC YEAR</label>
          <select
            id="academicYearFilter"
            v-model="academicYear"
            class="filter-select"
          >
            <option
              v-for="yr in filterOptions?.academic_years"
              :key="yr"
              :value="yr"
            >
              {{ yr }}
            </option>
          </select>
        </div>

        <!-- Exam -->
        <div class="filter-group">
          <label class="filter-label" for="examFilter">EXAMINATION</label>
          <select
            id="examFilter"
            v-model="selectedExam"
            class="filter-select"
          >
            <option value="">All Examinations</option>
            <option
              v-for="ex in filterOptions?.exam_names"
              :key="ex"
              :value="ex"
            >
              {{ ex }}
            </option>
          </select>
        </div>

        <!-- Teacher Filter (Ahmed Hassan, Fatima, Sheikh, etc.) -->
        <div class="filter-group">
          <label class="filter-label" for="teacherFilter">TEACHER</label>
          <select
            id="teacherFilter"
            v-model="selectedTeacherId"
            class="filter-select"
          >
            <option :value="''">All Teachers</option>
            <option
              v-for="tch in filterOptions?.teachers"
              :key="tch.id"
              :value="tch.id"
            >
              {{ tch.name }}
            </option>
          </select>
        </div>

        <!-- Class Filter -->
        <div class="filter-group">
          <label class="filter-label" for="classFilter">CLASS</label>
          <select
            id="classFilter"
            v-model="selectedClassId"
            class="filter-select"
          >
            <option :value="''">All Classes</option>
            <option
              v-for="cls in filterOptions?.classes"
              :key="cls.id"
              :value="cls.id"
            >
              {{ cls.name }}
            </option>
          </select>
        </div>

        <!-- Subject Filter -->
        <div class="filter-group">
          <label class="filter-label" for="subjectFilter">SUBJECT</label>
          <select
            id="subjectFilter"
            v-model="selectedSubjectId"
            class="filter-select"
          >
            <option :value="''">All Subjects</option>
            <option
              v-for="sbj in filterOptions?.subjects"
              :key="sbj.id"
              :value="sbj.id"
            >
              {{ sbj.name }} ({{ sbj.code }})
            </option>
          </select>
        </div>

        <!-- Status Filter -->
        <div class="filter-group">
          <label class="filter-label" for="statusFilter">SUBMISSION STATUS</label>
          <select
            id="statusFilter"
            v-model="selectedStatus"
            class="filter-select"
          >
            <option value="">All Statuses</option>
            <option value="OVERDUE">⚠️ Overdue Submissions</option>
            <option value="DRAFT">Draft</option>
            <option value="SUBMITTED">Submitted (Pending Review)</option>
            <option value="UNDER_REVIEW">Under Review</option>
            <option value="RETURNED">Returned for Correction</option>
            <option value="APPROVED">Approved</option>
            <option value="RELEASED">Released</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Real-time Exam Submission KPI Overview -->
    <div class="kpi-overview-strip">
      <div class="kpi-card">
        <span class="kpi-title">TOTAL ASSIGNED</span>
        <div class="kpi-val-row">
          <span class="kpi-val">{{ summaryKPIs.total }}</span>
          <span class="kpi-subtext">Class &bull; Subject Streams</span>
        </div>
      </div>
      <div class="kpi-card kpi-card-submitted">
        <span class="kpi-title">SUBMITTED RESULTS</span>
        <div class="kpi-val-row">
          <span class="kpi-val text-emerald">{{ summaryKPIs.submitted }}</span>
          <span class="kpi-subtext font-bold text-emerald">{{ summaryKPIs.completionRate }}% completed</span>
        </div>
      </div>
      <div class="kpi-card kpi-card-pending">
        <span class="kpi-title">PENDING SUBMISSIONS</span>
        <div class="kpi-val-row">
          <span class="kpi-val text-amber">{{ summaryKPIs.pending }}</span>
          <span class="kpi-subtext">Awaiting teacher entry</span>
        </div>
      </div>
      <div class="kpi-card kpi-card-overdue" :class="{ 'has-overdue': summaryKPIs.overdue > 0 }">
        <span class="kpi-title">OVERDUE SUBMISSIONS</span>
        <div class="kpi-val-row">
          <span class="kpi-val text-red">{{ summaryKPIs.overdue }}</span>
          <span class="kpi-subtext" :class="{ 'text-red font-bold': summaryKPIs.overdue > 0 }">
            {{ summaryKPIs.overdue > 0 ? 'Requires Admin Extension' : 'All on schedule' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Teacher Accountability Banner (if teacher selected) -->
    <div v-if="selectedTeacherId && teacherAccountability" class="accountability-card">
      <div class="accountability-header">
        <div>
          <span class="accountability-pre">TEACHER ACCOUNTABILITY AUDIT</span>
          <h3 class="accountability-title">{{ teacherAccountability.teacher_name }}</h3>
          <span class="accountability-email">{{ teacherAccountability.teacher_number || 'ID: ' + teacherAccountability.teacher_id }}</span>
        </div>
        <div class="accountability-badge">
          <span>{{ academicYear }}</span>
        </div>
      </div>

      <div class="accountability-metrics">
        <div class="acc-box">
          <span class="acc-label">TOTAL ASSIGNED</span>
          <span class="acc-val">{{ teacherAccountability.total_assigned }}</span>
        </div>
        <div class="acc-box">
          <span class="acc-label">SUBMITTED</span>
          <span class="acc-val text-amber">{{ teacherAccountability.submitted }}</span>
        </div>
        <div class="acc-box">
          <span class="acc-label">PARTIAL</span>
          <span class="acc-val text-yellow">{{ teacherAccountability.partial }}</span>
        </div>
        <div class="acc-box">
          <span class="acc-label">PENDING</span>
          <span class="acc-val" :class="{ 'text-red': teacherAccountability.pending > 0 }">
            {{ teacherAccountability.pending }}
          </span>
        </div>
        <div class="acc-box">
          <span class="acc-label">APPROVED</span>
          <span class="acc-val text-blue">{{ teacherAccountability.approved }}</span>
        </div>
        <div class="acc-box">
          <span class="acc-label">RETURNED</span>
          <span class="acc-val text-red">{{ teacherAccountability.returned }}</span>
        </div>
        <div class="acc-box">
          <span class="acc-label">RELEASED</span>
          <span class="acc-val text-emerald">{{ teacherAccountability.released }}</span>
        </div>
      </div>
    </div>

    <!-- Submissions Table (Desktop) -->
    <div class="submissions-container">
      <div class="desktop-view">
        <table class="submissions-table" aria-label="Teacher Submissions Table">
          <thead>
            <tr>
              <th scope="col">TEACHER</th>
              <th scope="col">SUBJECT</th>
              <th scope="col">CLASS</th>
              <th scope="col">EXAM</th>
              <th scope="col" class="text-center">STUDENTS</th>
              <th scope="col" class="text-center">STATUS</th>
              <th scope="col">DEADLINE</th>
              <th scope="col">SUBMITTED AT</th>
              <th scope="col" class="text-right">ACTIONS</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="isLoading">
              <td colspan="9" class="state-cell">
                <div class="shimmer-line" />
                <div class="shimmer-line" />
                <div class="shimmer-line" />
              </td>
            </tr>
            <tr v-else-if="submissions.length === 0">
              <td colspan="9" class="state-cell">
                No submissions found matching selected filters.
              </td>
            </tr>
            <tr
              v-for="sub in submissions"
              :key="sub.id"
              class="submission-row"
              :class="{ 'row-overdue': sub.is_overdue && sub.status !== 'SUBMITTED' && sub.status !== 'APPROVED' }"
            >
              <td class="teacher-cell">
                <div class="tch-name">{{ sub.teacher_name }}</div>
                <div class="tch-email">{{ sub.teacher_number || 'TCH-' + sub.teacher_id }}</div>
              </td>
              <td class="subject-cell">
                <div class="sbj-name">{{ sub.subject_name }}</div>
                <div class="sbj-code">{{ sub.subject_code }}</div>
              </td>
              <td class="class-cell">
                <span class="class-pill">{{ sub.class_name }}</span>
              </td>
              <td class="exam-cell">
                <div class="ex-name">{{ sub.exam_name }}</div>
                <div class="ex-year">{{ sub.academic_year }}</div>
              </td>
              <td class="text-center metrics-cell">
                <div class="students-summary">
                  <span class="std-completed">{{ sub.completed_students }}</span>
                  <span class="std-sep">/</span>
                  <span class="std-total">{{ sub.expected_students }}</span>
                </div>
                <div v-if="sub.pending_students > 0" class="std-pending">
                  {{ sub.pending_students }} pending
                </div>
              </td>
              <td class="text-center">
                <ResultStatusBadge :status="sub.status" size="sm" />
              </td>
              <td class="deadline-cell">
                <div class="dl-date">{{ formatDeadlineDisplay(sub.submission_deadline) }}</div>
                <span
                  v-if="sub.is_overdue && sub.status !== 'SUBMITTED' && sub.status !== 'APPROVED'"
                  class="dl-badge overdue"
                >
                  ⚠️ Overdue
                </span>
                <span
                  v-else-if="sub.deadline_status === 'APPROACHING'"
                  class="dl-badge approaching"
                >
                  ⏳ Approaching
                </span>
                <span
                  v-else-if="sub.submission_deadline"
                  class="dl-badge on-track"
                >
                  On Schedule
                </span>
              </td>
              <td class="date-cell">
                {{ formatDate(sub.submitted_at) }}
              </td>
              <td class="text-right actions-cell">
                <div class="action-btn-group">
                  <button
                    type="button"
                    class="btn-inspect"
                    @click="handleInspect(sub)"
                    title="Review marks and verify grades"
                  >
                    Review
                  </button>
                  <button
                    type="button"
                    class="btn-action-extend"
                    @click="openExtendModal(sub)"
                    title="Extend submission deadline"
                  >
                    Extend
                  </button>
                  <button
                    v-if="sub.is_overdue || sub.exam_status === 'CLOSED'"
                    type="button"
                    class="btn-action-reopen"
                    @click="openReopenModal(sub)"
                    title="Reopen closed or overdue submission"
                  >
                    Reopen
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile Cards (< 820px) -->
      <div class="mobile-view">
        <div v-if="isLoading" class="mobile-loading">
          <div class="shimmer-card" />
          <div class="shimmer-card" />
        </div>
        <div v-else-if="submissions.length === 0" class="mobile-empty">
          No submissions found matching selected filters.
        </div>
        <div
          v-for="sub in submissions"
          :key="`mob-sub-${sub.id}`"
          class="mobile-sub-card"
          :class="{ 'card-overdue': sub.is_overdue && sub.status !== 'SUBMITTED' && sub.status !== 'APPROVED' }"
        >
          <div class="mob-card-head">
            <div>
              <h4 class="mob-tch-title">{{ sub.teacher_name }}</h4>
              <span class="mob-sbj-sub">{{ sub.subject_name }} &bull; {{ sub.class_name }}</span>
            </div>
            <ResultStatusBadge :status="sub.status" size="sm" />
          </div>

          <div class="mob-card-stats">
            <div class="mob-stat">
              <span class="mob-stat-lbl">Marks Entered</span>
              <span class="mob-stat-val">{{ sub.completed_students }} / {{ sub.expected_students }}</span>
            </div>
            <div class="mob-stat">
              <span class="mob-stat-lbl">Deadline</span>
              <span class="mob-stat-val">{{ formatDeadlineDisplay(sub.submission_deadline) }}</span>
            </div>
          </div>

          <div class="mob-action-row">
            <button
              type="button"
              class="btn-inspect mob-half-btn"
              @click="handleInspect(sub)"
            >
              Review Marks
            </button>
            <button
              type="button"
              class="btn-action-extend mob-half-btn"
              @click="openExtendModal(sub)"
            >
              Extend Deadline
            </button>
            <button
              v-if="sub.is_overdue || sub.exam_status === 'CLOSED'"
              type="button"
              class="btn-action-reopen mob-half-btn"
              @click="openReopenModal(sub)"
            >
              Reopen
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Extend Deadline Modal -->
    <div v-if="isExtendModalOpen && extendTarget" class="modal-backdrop" @click.self="isExtendModalOpen = false">
      <div class="custom-modal-card">
        <div class="custom-modal-header">
          <div class="modal-icon-wrap amber">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="modal-header-text">
            <h3 class="custom-modal-title">Extend Result Submission Deadline</h3>
            <p class="custom-modal-sub">{{ extendTarget.exam_name }}</p>
          </div>
          <button type="button" class="custom-close-btn" @click="isExtendModalOpen = false">&times;</button>
        </div>

        <form @submit.prevent="handleConfirmExtend" class="custom-modal-body">
          <div v-if="extendTarget.current_deadline" class="modal-info-pill">
            <span class="info-pill-label">Current Deadline:</span>
            <span class="info-pill-val">{{ formatDeadlineDisplay(extendTarget.current_deadline) }}</span>
          </div>

          <div class="form-group-modal">
            <label class="modal-form-label">
              New Result Submission Deadline <span class="required">*</span>
            </label>
            <input
              v-model="extendForm.new_deadline"
              type="datetime-local"
              class="modal-input"
              required
            />
            <div class="preset-chips">
              <span class="preset-label">Quick Presets:</span>
              <button type="button" class="preset-chip" @click="setExtendPreset(7)">+7 Days</button>
              <button type="button" class="preset-chip" @click="setExtendPreset(14)">+14 Days</button>
              <button type="button" class="preset-chip" @click="setExtendPreset(30)">+1 Month</button>
            </div>
          </div>

          <div class="form-group-modal">
            <label class="modal-form-label">
              Reason for Extension (Audit Log) <span class="required">*</span>
            </label>
            <textarea
              v-model="extendForm.reason"
              rows="3"
              class="modal-textarea"
              placeholder="e.g. Additional grading window granted due to practical assessment delays..."
              required
            ></textarea>
            <span class="modal-hint">This justification is recorded in the permanent audit trail and sent to assigned teachers.</span>
          </div>

          <div class="custom-modal-footer">
            <button type="button" class="btn-cancel" @click="isExtendModalOpen = false">Cancel</button>
            <button type="submit" class="btn-confirm-extend" :disabled="isExtending">
              {{ isExtending ? 'Updating Deadline...' : 'Authorize Deadline Extension' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Reopen Submissions Modal -->
    <div v-if="isReopenModalOpen && reopenTarget" class="modal-backdrop" @click.self="isReopenModalOpen = false">
      <div class="custom-modal-card">
        <div class="custom-modal-header">
          <div class="modal-icon-wrap emerald">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </div>
          <div class="modal-header-text">
            <h3 class="custom-modal-title">Reopen Results Submission</h3>
            <p class="custom-modal-sub">{{ reopenTarget.exam_name }}</p>
          </div>
          <button type="button" class="custom-close-btn" @click="isReopenModalOpen = false">&times;</button>
        </div>

        <form @submit.prevent="handleConfirmReopen" class="custom-modal-body">
          <div class="modal-warning-banner">
            <svg class="warning-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
            <div>
              <strong>Reopening Authorization:</strong> This will transition the examination state to <code>OPEN_FOR_RESULTS</code>. Assigned teachers will immediately be permitted to enter, modify, and submit marks. All existing results are safely preserved.
            </div>
          </div>

          <div class="form-group-modal">
            <label class="modal-form-label">
              Reason for Reopening <span class="required">*</span>
            </label>
            <textarea
              v-model="reopenReason"
              rows="3"
              class="modal-textarea"
              placeholder="e.g. Authorized review of student marks after department evaluation..."
              required
            ></textarea>
          </div>

          <div class="custom-modal-footer">
            <button type="button" class="btn-cancel" @click="isReopenModalOpen = false">Cancel</button>
            <button type="submit" class="btn-confirm-reopen" :disabled="isReopening">
              {{ isReopening ? 'Reopening Exam...' : 'Confirm Reopen Submissions' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Review & Return Modals -->
    <ResultReviewModal
      :is-open="isReviewModalOpen"
      :submission="activeSubmission"
      :is-loading="isReviewLoading"
      :is-processing="isReviewProcessing"
      @close="isReviewModalOpen = false"
      @approve="handleApprove"
      @return="handleOpenReturn"
    />

    <ReturnSubmissionModal
      :is-open="isReturnModalOpen"
      :subject-name="activeSubmission?.subject_name || ''"
      :class-name="activeSubmission?.class_name || ''"
      :is-processing="isReturnProcessing"
      @close="isReturnModalOpen = false"
      @confirm="handleConfirmReturn"
    />
  </div>
</template>

<style scoped>
.submissions-page {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  box-sizing: border-box;
}

.page-top-bar {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.pre-title {
  font-size: 0.6875rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #38bdf8;
  text-transform: uppercase;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #ffffff;
  margin: 0.2rem 0;
}

.page-sub {
  font-size: 0.8125rem;
  color: #94a3b8;
  margin: 0;
}

.btn-nav {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #1e293b;
  border: 1px solid #334155;
  color: #f1f5f9;
  border-radius: 8px;
  padding: 0.6rem 1rem;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-nav:hover {
  background-color: #334155;
  color: #38bdf8;
}

.nav-icon {
  width: 1.125rem;
  height: 1.125rem;
}

.notification-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.85rem 1.25rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
}

.notification-banner.success {
  background-color: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.35);
  color: #34d399;
}

.notification-banner.error {
  background-color: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.35);
  color: #f87171;
}

.notif-close {
  background: none;
  border: none;
  color: inherit;
  font-size: 1.25rem;
  cursor: pointer;
  line-height: 1;
}

.filter-card {
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 1.25rem;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 0.85rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.filter-label {
  font-size: 0.625rem;
  font-weight: 700;
  color: #94a3b8;
  letter-spacing: 0.05em;
}

.filter-select {
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 6px;
  padding: 0.55rem 0.65rem;
  color: #ffffff;
  font-size: 0.8125rem;
  outline: none;
}

.filter-select:focus {
  border-color: #0284c7;
}

/* Accountability Card */
.accountability-card {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border: 1px solid #38bdf8;
  border-radius: 12px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.accountability-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.accountability-pre {
  font-size: 0.625rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #38bdf8;
}

.accountability-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: #ffffff;
  margin: 0.15rem 0;
}

.accountability-email {
  font-size: 0.75rem;
  color: #94a3b8;
}

.accountability-badge {
  background-color: rgba(56, 189, 248, 0.15);
  border: 1px solid rgba(56, 189, 248, 0.3);
  color: #38bdf8;
  padding: 0.25rem 0.65rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
}

.accountability-metrics {
  display: grid;
  grid-template-columns: repeat(9, 1fr);
  gap: 0.5rem;
  background-color: rgba(15, 23, 42, 0.6);
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 0.75rem;
  text-align: center;
}

.acc-box {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.acc-label {
  font-size: 0.5625rem;
  font-weight: 700;
  color: #64748b;
  letter-spacing: 0.04em;
}

.acc-val {
  font-size: 1.125rem;
  font-weight: 800;
  color: #f1f5f9;
}

.text-amber { color: #fbbf24; }
.text-yellow { color: #fde047; }
.text-blue { color: #60a5fa; }
.text-emerald { color: #34d399; }
.text-red { color: #f87171; }
.text-muted { color: #64748b; }

/* Submissions Table */
.submissions-container {
  width: 100%;
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  overflow: hidden;
}

.desktop-view {
  width: 100%;
  overflow-x: auto;
}

.submissions-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8125rem;
  text-align: left;
}

.submissions-table th {
  background-color: #0f172a;
  color: #94a3b8;
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #334155;
  white-space: nowrap;
}

.submissions-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #334155;
  color: #f1f5f9;
  vertical-align: middle;
}

.submission-row:hover {
  background-color: rgba(51, 65, 85, 0.4);
}

.tch-name { font-weight: 700; color: #ffffff; }
.tch-email { font-size: 0.6875rem; color: #94a3b8; }
.sbj-name { font-weight: 700; color: #e2e8f0; }
.sbj-code { font-size: 0.6875rem; color: #94a3b8; }

.class-pill {
  background-color: #0f172a;
  border: 1px solid #334155;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-weight: 600;
}

.ex-name { font-weight: 600; }
.ex-year { font-size: 0.6875rem; color: #94a3b8; }

.students-summary {
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.std-completed { color: #f1f5f9; }
.std-sep { color: #64748b; margin: 0 0.15rem; }
.std-total { color: #94a3b8; }

.std-pending {
  font-size: 0.6875rem;
  color: #f87171;
  font-weight: 600;
}

.date-cell {
  font-size: 0.75rem;
  color: #cbd5e1;
  white-space: nowrap;
}

.text-center { text-align: center; }
.text-right { text-align: right; }

.btn-inspect {
  background-color: #0284c7;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  padding: 0.35rem 0.85rem;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-inspect:hover {
  background-color: #0369a1;
}

/* KPI Overview Strip */
.kpi-overview-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.kpi-card {
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.kpi-title {
  font-size: 0.6875rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  color: #94a3b8;
  text-transform: uppercase;
}

.kpi-val-row {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
}

.kpi-val {
  font-size: 1.65rem;
  font-weight: 800;
  color: #ffffff;
}

.kpi-subtext {
  font-size: 0.75rem;
  color: #94a3b8;
}

.kpi-card-overdue.has-overdue {
  border-color: rgba(239, 68, 68, 0.5);
  background: rgba(239, 68, 68, 0.08);
}

/* Row & Badge Overdue styling */
.row-overdue {
  background-color: rgba(239, 68, 68, 0.04);
}

.deadline-cell {
  padding: 0.85rem 1rem;
}

.dl-date {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #f1f5f9;
}

.dl-badge {
  display: inline-block;
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  margin-top: 0.2rem;
}

.dl-badge.overdue {
  background: rgba(239, 68, 68, 0.2);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.4);
}

.dl-badge.approaching {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.4);
}

.dl-badge.on-track {
  background: rgba(56, 189, 248, 0.15);
  color: #38bdf8;
}

/* Action buttons */
.action-btn-group {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.35rem;
  flex-wrap: wrap;
}

.btn-action-extend {
  background-color: #d97706;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  padding: 0.35rem 0.7rem;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-action-extend:hover {
  background-color: #b45309;
}

.btn-action-reopen {
  background-color: #059669;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  padding: 0.35rem 0.7rem;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-action-reopen:hover {
  background-color: #047857;
}

/* Modal styling */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.75);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
}

.custom-modal-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 16px;
  width: 100%;
  max-width: 540px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  overflow: hidden;
  color: #f1f5f9;
}

.custom-modal-header {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #334155;
  position: relative;
}

.modal-icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.modal-icon-wrap svg {
  width: 22px;
  height: 22px;
}

.modal-icon-wrap.amber {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.4);
}

.modal-icon-wrap.emerald {
  background: rgba(16, 185, 129, 0.2);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.4);
}

.modal-header-text {
  flex: 1;
}

.custom-modal-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0;
  color: #ffffff;
}

.custom-modal-sub {
  font-size: 0.8125rem;
  color: #94a3b8;
  margin: 0.15rem 0 0;
}

.custom-close-btn {
  font-size: 1.5rem;
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
}

.custom-close-btn:hover {
  color: #ffffff;
}

.custom-modal-body {
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.modal-info-pill {
  background: #0f172a;
  border: 1px solid #334155;
  padding: 0.5rem 0.85rem;
  border-radius: 8px;
  font-size: 0.8125rem;
  display: flex;
  gap: 0.5rem;
}

.info-pill-label {
  color: #94a3b8;
}

.info-pill-val {
  color: #38bdf8;
  font-weight: 600;
}

.form-group-modal {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.modal-form-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #cbd5e1;
}

.modal-input,
.modal-textarea {
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 8px;
  color: #f1f5f9;
  padding: 0.6rem 0.85rem;
  font-size: 0.875rem;
  outline: none;
}

.modal-input:focus,
.modal-textarea:focus {
  border-color: #38bdf8;
}

.preset-chips {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  margin-top: 0.25rem;
}

.preset-label {
  font-size: 0.72rem;
  color: #64748b;
  font-weight: 600;
}

.preset-chip {
  background: #0f172a;
  border: 1px solid #334155;
  color: #38bdf8;
  border-radius: 6px;
  padding: 0.2rem 0.55rem;
  font-size: 0.72rem;
  font-weight: 600;
  cursor: pointer;
}

.preset-chip:hover {
  background: #1e293b;
  border-color: #38bdf8;
}

.modal-hint {
  font-size: 0.72rem;
  color: #64748b;
}

.modal-warning-banner {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: #34d399;
  padding: 0.85rem 1rem;
  border-radius: 8px;
  font-size: 0.8125rem;
  line-height: 1.45;
}

.warning-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  margin-top: 1px;
}

.custom-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #334155;
}

.btn-cancel {
  padding: 0.55rem 1rem;
  background: transparent;
  border: 1px solid #334155;
  color: #cbd5e1;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-cancel:hover {
  background: #334155;
}

.btn-confirm-extend {
  padding: 0.55rem 1.25rem;
  background: #d97706;
  border: 1px solid #b45309;
  color: #ffffff;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-confirm-extend:hover:not(:disabled) {
  background: #b45309;
}

.btn-confirm-reopen {
  padding: 0.55rem 1.25rem;
  background: #059669;
  border: 1px solid #047857;
  color: #ffffff;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-confirm-reopen:hover:not(:disabled) {
  background: #047857;
}

.mob-action-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.mob-half-btn {
  flex: 1;
  min-width: 110px;
  text-align: center;
  padding: 0.45rem;
}

.state-cell {
  text-align: center;
  padding: 2.5rem 1rem;
  color: #94a3b8;
}

.shimmer-line {
  height: 1.5rem;
  background: linear-gradient(90deg, #334155 25%, #475569 50%, #334155 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 0.75rem;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Mobile View */
.mobile-view {
  display: none;
}

@media (max-width: 1024px) {
  .filters-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  .accountability-metrics {
    grid-template-columns: repeat(5, 1fr);
  }
}

@media (max-width: 820px) {
  .desktop-view {
    display: none;
  }
  .mobile-view {
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
    padding: 1rem;
  }

  .mobile-sub-card {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .mob-card-head {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .mob-tch-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0;
  }

  .mob-sbj-sub {
    font-size: 0.75rem;
    color: #94a3b8;
  }

  .mob-card-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
    background-color: #1e293b;
    border-radius: 8px;
    padding: 0.65rem;
  }

  .mob-stat {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
  }

  .mob-stat-lbl {
    font-size: 0.625rem;
    text-transform: uppercase;
    color: #64748b;
    font-weight: 700;
  }

  .mob-stat-val {
    font-size: 0.8125rem;
    font-weight: 700;
    color: #f1f5f9;
  }

  .mob-full-btn {
    width: 100%;
    padding: 0.55rem;
    text-align: center;
  }
}

@media (max-width: 640px) {
  .submissions-page {
    padding: 1rem;
  }
  .filters-grid {
    grid-template-columns: 1fr;
  }
  .accountability-metrics {
    grid-template-columns: repeat(auto-fit, minmax(85px, 1fr));
  }
  .accountability-email {
    overflow-wrap: anywhere;
  }
}
</style>
