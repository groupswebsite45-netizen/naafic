<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { examService } from '../../../services/examService';
import { ExamProfile, Exam, ReportCardData } from '../../../types/school';

import ExamStatusBadge from './components/ExamStatusBadge.vue';
import ResultProgressBar from './components/ResultProgressBar.vue';
import GradeBadge from './components/GradeBadge.vue';
import ExamReportCard from './components/ExamReportCard.vue';
import PublishModal from './components/PublishModal.vue';
import ExamConfirmDialog from './components/ExamConfirmDialog.vue';

const route = useRoute();
const router = useRouter();

const examId = computed(() => Number(route.params.id));
const activeTab = ref<'overview' | 'students' | 'marks' | 'results' | 'publication' | 'report-card'>('overview');

const profile = ref<ExamProfile | null>(null);
const isLoading = ref(true);
const errorMessage = ref('');
const successMessage = ref('');

// Modals
const isPublishModalOpen = ref(false);
const isPublishAction = ref(true);
const isSubmittingPublish = ref(false);

const isDeleteModalOpen = ref(false);
const isDeleting = ref(false);

// Edit Exam Modal
const isEditModalOpen = ref(false);
const isSavingEdit = ref(false);
const editForm = ref({
  name: '',
  exam_type: '',
  academic_year: '',
  start_date: '',
  end_date: '',
  start_time: '',
  end_time: '',
  result_submission_deadline: '',
  instructions: '',
  max_marks: 100,
  pass_marks: 50,
  status: 'SCHEDULED'
});

// Deadline Extension & Reopen Modal State
const isExtendModalOpen = ref(false);
const extendDeadlineVal = ref('');
const extendReason = ref('');
const isExtending = ref(false);

const isReopenModalOpen = ref(false);
const reopenReason = ref('');
const isReopening = ref(false);

const isOverdueExam = computed(() => {
  if (!profile.value?.exam?.result_submission_deadline) return false;
  const dl = new Date(profile.value.exam.result_submission_deadline);
  return dl.getTime() < Date.now();
});

// Report Card State
const selectedStudentIdForReport = ref<number | null>(null);
const studentReportCard = ref<ReportCardData | null>(null);
const isLoadingReport = ref(false);

async function loadProfile() {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    const data = await examService.getExamProfile(examId.value);
    profile.value = data;

    // Prefill edit form
    if (data.exam) {
      editForm.value = {
        name: data.exam.name,
        exam_type: data.exam.exam_type,
        academic_year: data.exam.academic_year,
        start_date: (data.exam.start_date || data.exam.exam_date || '').split('T')[0],
        end_date: (data.exam.end_date || '').split('T')[0],
        start_time: data.exam.start_time || '',
        end_time: data.exam.end_time || '',
        result_submission_deadline: data.exam.result_submission_deadline ? data.exam.result_submission_deadline.slice(0, 16) : '',
        instructions: data.exam.instructions || '',
        max_marks: data.exam.max_marks ?? 100,
        pass_marks: data.exam.pass_marks ?? 50,
        status: data.exam.status
      };
    }

    // Default first student for report card
    if (data.student_sheet && data.student_sheet.length > 0 && !selectedStudentIdForReport.value) {
      selectedStudentIdForReport.value = data.student_sheet[0].student_id;
      loadReportCard(data.student_sheet[0].student_id);
    }
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to load examination profile from PostgreSQL.';
  } finally {
    isLoading.value = false;
  }
}

async function loadReportCard(studentId: number) {
  isLoadingReport.value = true;
  try {
    const data = await examService.getReportCard(examId.value, studentId);
    studentReportCard.value = data;
  } catch (err) {
    console.error('Failed to load report card', err);
  } finally {
    isLoadingReport.value = false;
  }
}

watch(selectedStudentIdForReport, (newStudentId) => {
  if (newStudentId) {
    loadReportCard(newStudentId);
  }
});

function openPublishModal(publish: boolean) {
  isPublishAction.value = publish;
  isPublishModalOpen.value = true;
}

async function handleConfirmPublish(exam: Exam, publish: boolean) {
  isSubmittingPublish.value = true;
  try {
    await examService.publishResults(exam.id, publish);
    successMessage.value = publish
      ? `Results for "${exam.name}" have been published to student & guardian portals.`
      : `Results for "${exam.name}" have been unpublished.`;
    isPublishModalOpen.value = false;
    await loadProfile();
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to update publication state.';
  } finally {
    isSubmittingPublish.value = false;
  }
}

async function handleConfirmDelete() {
  isDeleting.value = true;
  try {
    await examService.deleteExam(examId.value);
    router.push('/admin/exams');
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to delete examination.';
  } finally {
    isDeleting.value = false;
  }
}

async function handleSaveEdit() {
  isSavingEdit.value = true;
  errorMessage.value = '';
  try {
    await examService.updateExam(examId.value, {
      name: editForm.value.name,
      exam_type: editForm.value.exam_type,
      academic_year: editForm.value.academic_year,
      start_date: editForm.value.start_date,
      end_date: editForm.value.end_date || null,
      start_time: editForm.value.start_time || null,
      end_time: editForm.value.end_time || null,
      result_submission_deadline: editForm.value.result_submission_deadline ? new Date(editForm.value.result_submission_deadline).toISOString() : null,
      instructions: editForm.value.instructions || null,
      max_marks: Number(editForm.value.max_marks),
      pass_marks: Number(editForm.value.pass_marks),
      status: editForm.value.status
    });
    isEditModalOpen.value = false;
    successMessage.value = 'Examination updated successfully.';
    await loadProfile();
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to update exam.';
  } finally {
    isSavingEdit.value = false;
  }
}

function openExtendModal() {
  if (!profile.value?.exam) return;
  const dl = profile.value.exam.result_submission_deadline;
  const base = dl ? new Date(dl) : new Date();
  const nextDate = new Date(base.getTime() + 14 * 24 * 60 * 60 * 1000);
  extendDeadlineVal.value = nextDate.toISOString().slice(0, 16);
  extendReason.value = '';
  isExtendModalOpen.value = true;
}

function setProfileExtendPreset(days: number) {
  const nextDate = new Date(Date.now() + days * 24 * 60 * 60 * 1000);
  extendDeadlineVal.value = nextDate.toISOString().slice(0, 16);
}

async function handleConfirmExtend() {
  if (!extendDeadlineVal.value) {
    errorMessage.value = 'Please select a new deadline.';
    return;
  }
  if (!extendReason.value.trim()) {
    errorMessage.value = 'Please provide an audit reason for extending the deadline.';
    return;
  }
  isExtending.value = true;
  try {
    await examService.extendDeadline(examId.value, {
      new_deadline: new Date(extendDeadlineVal.value).toISOString(),
      reason: extendReason.value.trim(),
    });
    successMessage.value = 'Deadline extended successfully.';
    isExtendModalOpen.value = false;
    await loadProfile();
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to extend deadline.';
  } finally {
    isExtending.value = false;
  }
}

function openReopenModal() {
  reopenReason.value = '';
  isReopenModalOpen.value = true;
}

async function handleConfirmReopen() {
  if (!reopenReason.value.trim()) {
    errorMessage.value = 'Please provide a reason for reopening submissions.';
    return;
  }
  isReopening.value = true;
  try {
    await examService.reopenSubmissions(examId.value, {
      reason: reopenReason.value.trim(),
    });
    successMessage.value = 'Submissions reopened successfully.';
    isReopenModalOpen.value = false;
    await loadProfile();
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to reopen submissions.';
  } finally {
    isReopening.value = false;
  }
}

const isDispatching = ref(false);

async function handleDispatchToTeachers() {
  isDispatching.value = true;
  errorMessage.value = '';
  try {
    const res = await examService.dispatchToTeachers(examId.value);
    successMessage.value = res.message || 'Examination successfully released to assigned faculty teachers.';
    await loadProfile();
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to release examination to teachers.';
  } finally {
    isDispatching.value = false;
  }
}

function formatDateTime(val?: string | null): string {
  if (!val) return '—';
  try {
    const d = new Date(val);
    return d.toLocaleString('en-GB', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
  } catch {
    return val;
  }
}

function formatDateRange(startDate?: string | null, endDate?: string | null): string {
  if (!startDate) return '—';
  try {
    const s = new Date(startDate);
    const startStr = s.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
    if (!endDate || endDate === startDate) return startStr;
    const e = new Date(endDate);
    const endStr = e.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
    return `${startStr} – ${endStr}`;
  } catch {
    return startDate;
  }
}

onMounted(() => {
  if (route.query.tab) {
    activeTab.value = route.query.tab as any;
  }
  if (route.query.edit === 'true') {
    isEditModalOpen.value = true;
  }
  loadProfile();
});
</script>

<template>
  <div class="exam-profile-page">
    <!-- Breadcrumb -->
    <div class="profile-breadcrumb">
      <button type="button" class="back-link" @click="router.push('/admin/exams')">
        <svg class="back-icon" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clip-rule="evenodd" />
        </svg>
        <span>Back to Exams Directory</span>
      </button>
    </div>

    <!-- Alert Messages -->
    <div v-if="successMessage" class="alert success">
      <span>{{ successMessage }}</span>
      <button type="button" class="alert-dismiss" @click="successMessage = ''">&times;</button>
    </div>
    <div v-if="errorMessage" class="alert error">
      <span>{{ errorMessage }}</span>
      <button type="button" class="alert-dismiss" @click="errorMessage = ''">&times;</button>
    </div>

    <!-- Profile Header Card -->
    <div v-if="profile?.exam" class="profile-header-card">
      <div class="header-main">
        <div class="title-area">
          <div class="badge-row">
            <span class="exam-type-pill">{{ profile.exam.exam_type }}</span>
            <span class="year-pill">{{ profile.exam.academic_year }}</span>
            <ExamStatusBadge :status="profile.exam.status" />
          </div>

          <h1 class="profile-exam-name">{{ profile.exam.name }}</h1>

          <div class="exam-details-strip">
            <span class="detail-item">
              <svg class="strip-icon" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
              </svg>
              {{ formatDateRange(profile.exam.start_date || profile.exam.exam_date, profile.exam.end_date) }}
            </span>
            <span class="separator">•</span>
            <span class="detail-item">
              <strong>Class:</strong> {{ profile.exam.school_class?.name || `Class #${profile.exam.class_id}` }}
            </span>
            <span class="separator">•</span>
            <span class="detail-item">
              <strong>Subject:</strong> {{ profile.exam.subject?.name || `Subject #${profile.exam.subject_id}` }}
            </span>
          </div>
        </div>

        <!-- Quick Actions Header -->
        <div class="header-actions-group">
          <button type="button" class="action-btn outline" @click="isEditModalOpen = true">
            <svg class="act-icon" viewBox="0 0 20 20" fill="currentColor">
              <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
            </svg>
            <span>Edit</span>
          </button>

          <button
            type="button"
            class="action-btn outline"
            @click="openExtendModal"
            title="Extend result submission deadline"
          >
            <svg class="act-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
            </svg>
            <span>Extend Deadline</span>
          </button>

          <button
            v-if="profile.exam.status === 'CLOSED' || isOverdueExam"
            type="button"
            class="action-btn outline"
            style="color: #059669; border-color: #a7f3d0; background: #ecfdf5;"
            @click="openReopenModal"
            title="Reopen exam submissions"
          >
            <svg class="act-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
            </svg>
            <span>Reopen Submissions</span>
          </button>

          <button
            type="button"
            class="action-btn primary"
            style="color: #ffffff; background: #2563eb;"
            :disabled="isDispatching"
            @click="handleDispatchToTeachers"
            title="Release this exam to assigned teachers for results entry"
          >
            <svg class="act-icon" viewBox="0 0 20 20" fill="currentColor">
              <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
            </svg>
            <span>{{ isDispatching ? 'Releasing...' : 'Release to Teachers' }}</span>
          </button>

          <button
            v-if="profile.exam.status === 'UNDER_REVIEW' || profile.student_sheet?.some(s => s.is_saved)"
            type="button"
            class="action-btn outline"
            style="color: #4f46e5; border-color: #c7d2fe; background: #eef2ff;"
            @click="router.push('/admin/results/management')"
            title="Review results submitted by teachers in Results Management"
          >
            <svg class="act-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
            <span>Review Submissions</span>
          </button>

          <button
            v-if="profile.exam.status !== 'PUBLISHED'"
            type="button"
            class="action-btn publish"
            @click="openPublishModal(true)"
          >
            Publish Results
          </button>
          <button
            v-else
            type="button"
            class="action-btn unpublish"
            @click="openPublishModal(false)"
          >
            Unpublish
          </button>

          <button
            type="button"
            class="action-btn danger"
            :disabled="profile.exam.status === 'PUBLISHED'"
            title="Delete Exam"
            @click="isDeleteModalOpen = true"
          >
            Delete
          </button>
        </div>
      </div>
    </div>

    <!-- Summary KPI Cards -->
    <div v-if="profile" class="summary-kpi-grid">
      <div class="kpi-card">
        <span class="kpi-label">Enrolled Students</span>
        <span class="kpi-val">{{ profile.enrolled_count }}</span>
        <span class="kpi-sub">Active in {{ profile.exam.school_class?.name }}</span>
      </div>

      <div class="kpi-card">
        <span class="kpi-label">Scores Recorded</span>
        <span class="kpi-val">{{ profile.results_count }} / {{ profile.enrolled_count }}</span>
        <span class="kpi-sub">{{ profile.completion_percentage }}% complete</span>
      </div>

      <div class="kpi-card">
        <span class="kpi-label">Class Average Score</span>
        <span class="kpi-val">{{ profile.average_score !== null ? `${profile.average_score} pts` : '—' }}</span>
        <span class="kpi-sub">Scale: 0 – {{ profile.exam.max_marks }}</span>
      </div>

      <div class="kpi-card">
        <span class="kpi-label">Pass Rate</span>
        <span class="kpi-val" :class="{ 'text-emerald': profile.pass_rate >= 70 }">
          {{ profile.results_count > 0 ? `${profile.pass_rate}%` : '—' }}
        </span>
        <span class="kpi-sub">{{ profile.pass_count }} Pass · {{ profile.fail_count }} Fail</span>
      </div>
    </div>

    <!-- Profile Tabs Strip -->
    <div class="tabs-strip-container">
      <div class="tabs-strip">
        <button
          type="button"
          class="tab-item"
          :class="{ active: activeTab === 'overview' }"
          @click="activeTab = 'overview'"
        >
          Overview
        </button>

        <button
          type="button"
          class="tab-item"
          :class="{ active: activeTab === 'students' }"
          @click="activeTab = 'students'"
        >
          Students ({{ profile?.enrolled_count ?? 0 }})
        </button>

        <button
          type="button"
          class="tab-item"
          :class="{ active: activeTab === 'marks' }"
          @click="activeTab = 'marks'"
        >
          Teacher Submissions & Results
        </button>

        <button
          type="button"
          class="tab-item"
          :class="{ active: activeTab === 'results' }"
          @click="activeTab = 'results'"
        >
          Results Analytics
        </button>

        <button
          type="button"
          class="tab-item"
          :class="{ active: activeTab === 'publication' }"
          @click="activeTab = 'publication'"
        >
          Publication
        </button>

        <button
          type="button"
          class="tab-item"
          :class="{ active: activeTab === 'report-card' }"
          @click="activeTab = 'report-card'"
        >
          Report Card
        </button>
      </div>
    </div>

    <!-- TAB 1: OVERVIEW -->
    <div v-if="activeTab === 'overview' && profile" class="tab-pane">
      <div class="overview-grid">
        <div class="overview-card">
          <h2 class="card-title">Assessment Metadata</h2>
          <div class="meta-rows">
            <div class="row-item">
              <span class="k">Exam Title:</span>
              <span class="v">{{ profile.exam.name }}</span>
            </div>
            <div class="row-item">
              <span class="k">Exam Type:</span>
              <span class="v">{{ profile.exam.exam_type }}</span>
            </div>
            <div class="row-item">
              <span class="k">Academic Year:</span>
              <span class="v">{{ profile.exam.academic_year }}</span>
            </div>
            <div class="row-item">
              <span class="k">Target Class:</span>
              <span class="v">{{ profile.exam.school_class?.name }} (Code: {{ profile.exam.school_class?.code }})</span>
            </div>
            <div class="row-item">
              <span class="k">Subject:</span>
              <span class="v">{{ profile.exam.subject?.name }} (Code: {{ profile.exam.subject?.code }})</span>
            </div>
            <div class="row-item">
              <span class="k">Result Submission Deadline:</span>
              <span class="v font-bold" style="color: #0284c7;">
                {{ formatDateTime(profile.exam.result_submission_deadline) }}
                <span v-if="isOverdueExam" style="color: #dc2626; font-size: 0.75rem; margin-left: 0.35rem; font-weight: 700;">(Overdue)</span>
              </span>
            </div>
            <div v-if="profile.exam.instructions" class="row-item">
              <span class="k">Teacher Instructions:</span>
              <span class="v" style="color: #475569;">{{ profile.exam.instructions }}</span>
            </div>
          </div>
        </div>

        <div class="overview-card">
          <h2 class="card-title">Grading & Score Scale</h2>
          <div class="meta-rows">
            <div class="row-item">
              <span class="k">Maximum Marks:</span>
              <span class="v font-bold">{{ profile.exam.max_marks }} points</span>
            </div>
            <div class="row-item">
              <span class="k">Passing Mark:</span>
              <span class="v font-bold">{{ profile.exam.pass_marks }} points ({{ Math.round((Number(profile.exam.pass_marks) / Number(profile.exam.max_marks)) * 100) }}%)</span>
            </div>
            <div class="row-item">
              <span class="k">Highest Score:</span>
              <span class="v">{{ profile.highest_score !== null ? `${profile.highest_score} pts` : '—' }}</span>
            </div>
            <div class="row-item">
              <span class="k">Lowest Score:</span>
              <span class="v">{{ profile.lowest_score !== null ? `${profile.lowest_score} pts` : '—' }}</span>
            </div>
            <div class="row-item">
              <span class="k">Publication State:</span>
              <span class="v">
                <ExamStatusBadge :status="profile.exam.status" />
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: STUDENTS / ROSTER -->
    <div v-if="activeTab === 'students' && profile" class="tab-pane">
      <div class="roster-card">
        <div class="roster-header">
          <h2 class="card-title">Class Roster & Score Status</h2>
          <span class="roster-count">{{ profile.student_sheet.length }} students enrolled</span>
        </div>

        <div class="table-responsive" tabindex="0" role="region" aria-label="Class roster and score status table">
          <table class="roster-table">
            <thead>
              <tr>
                <th scope="col">Student Name</th>
                <th scope="col">Admission #</th>
                <th scope="col">Roll #</th>
                <th scope="col">Gender</th>
                <th scope="col">Marks Obtained</th>
                <th scope="col">Grade</th>
                <th scope="col">Evaluation Remark</th>
                <th scope="col">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="st in profile.student_sheet" :key="st.student_id">
                <td class="font-bold">{{ st.student_name }}</td>
                <td><code>{{ st.admission_number }}</code></td>
                <td>{{ st.roll_number || '—' }}</td>
                <td>{{ st.gender || '—' }}</td>
                <td class="font-bold">
                  {{ st.marks_obtained !== null ? `${st.marks_obtained} / ${profile.exam.max_marks}` : '—' }}
                </td>
                <td>
                  <GradeBadge :grade="st.grade" />
                </td>
                <td class="text-secondary">{{ st.remarks || '—' }}</td>
                <td>
                  <span v-if="st.is_saved" class="badge-saved">Recorded</span>
                  <span v-else class="badge-pending">Pending</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 3: TEACHER SUBMISSIONS & RESULTS SHEET -->
    <div v-if="activeTab === 'marks' && profile" class="tab-pane">
      <div class="teacher-workflow-pane">
        <!-- Notice Banner -->
        <div class="workflow-info-banner">
          <div class="banner-icon-circle">
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="banner-text-wrap">
            <h3 class="banner-title">Diiwaangelinta Natiijada Waxaa Leh Macalimiinta (Teacher Assessment Scope)</h3>
            <p class="banner-desc">
              Dhibcaha ardayda iyo xaadirinta imtixaanka waxaa si toos ah u gelaya macalinka loo xilsaaray maaddadan isagoo ka galaya <strong>Teacher Portal</strong>.
              Macalinku wuxuu dhibcaha ku keydsan karaa <strong>Draft</strong> ahaan inta uusan soo dirin, si haddii wax u dhiman yihiin uu dib ugu soo dhammaystiro ka hor inta uusan waqtigu dhicin.
            </p>
          </div>
          <button
            type="button"
            class="banner-action-btn"
            :disabled="isDispatching"
            @click="handleDispatchToTeachers"
          >
            <svg class="act-icon" viewBox="0 0 20 20" fill="currentColor">
              <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
            </svg>
            <span>{{ isDispatching ? 'U diraya...' : 'U Sii Daa Macalinka (Dispatch)' }}</span>
          </button>
        </div>

        <!-- Teacher Assignment & Status Overview Cards -->
        <div class="teacher-status-grid">
          <div class="t-card">
            <span class="tc-label">Assigned Subject Teacher</span>
            <span class="tc-val">{{ (profile.exam as any).teacher?.full_name || (profile.exam as any).teacher_name || 'Assigned Faculty Teacher' }}</span>
            <span class="tc-sub">{{ profile.exam.subject?.name }} • {{ profile.exam.school_class?.name }}</span>
          </div>

          <div class="t-card">
            <span class="tc-label">Submission Deadline</span>
            <span class="tc-val">{{ formatDateTime(profile.exam.result_submission_deadline) }}</span>
            <span class="tc-sub" :class="{ 'text-danger': isOverdueExam }">
              {{ isOverdueExam ? 'Deadline passed' : 'Teacher must submit within this window' }}
            </span>
          </div>

          <div class="t-card">
            <span class="tc-label">Graded Progress</span>
            <span class="tc-val">{{ profile.results_count }} / {{ profile.enrolled_count }}</span>
            <span class="tc-sub">{{ profile.pass_rate }}% Pass Rate</span>
          </div>

          <div class="t-card">
            <span class="tc-label">Workflow Status</span>
            <div class="tc-status-wrap">
              <ExamStatusBadge :status="profile.exam.status" />
            </div>
            <span class="tc-sub">Teacher Portal Marks Entry</span>
          </div>
        </div>

        <!-- Student Marks Roster (Read-Only Audit) -->
        <div class="student-sheet-card">
          <div class="sheet-header">
            <div>
              <h3 class="sheet-title">Student Marks & Evaluation Roster</h3>
              <p class="sheet-subtitle">Real-time view of grades recorded by the assigned faculty teacher.</p>
            </div>
            <div class="sheet-actions">
              <button
                type="button"
                class="refresh-btn"
                @click="loadProfile"
                title="Refresh latest marks"
              >
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
                </svg>
                <span>Refresh</span>
              </button>
            </div>
          </div>

          <div class="sheet-table-wrap">
            <table class="sheet-table">
              <thead>
                <tr>
                  <th>Student Name</th>
                  <th>Admission #</th>
                  <th>Attendance</th>
                  <th>Marks (/ {{ profile.exam.max_marks }})</th>
                  <th>Grade</th>
                  <th>Evaluation Remark</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="!profile.student_sheet || profile.student_sheet.length === 0">
                  <td colspan="7" class="text-center py-6 text-muted">
                    No students currently enrolled in this class.
                  </td>
                </tr>
                <tr v-for="st in profile.student_sheet" :key="st.student_id">
                  <td class="font-bold">{{ st.student_name }}</td>
                  <td><code>{{ st.admission_number }}</code></td>
                  <td>
                    <span class="attendance-pill" :class="(((st as any).attendance_status || (st.marks_obtained !== null ? 'PRESENT' : 'PENDING')) as string).toLowerCase()">
                      {{ (st as any).attendance_status || (st.marks_obtained !== null ? 'PRESENT' : 'PENDING') }}
                    </span>
                  </td>
                  <td class="font-bold">
                    {{ st.marks_obtained !== null ? st.marks_obtained : '—' }}
                  </td>
                  <td>
                    <GradeBadge :grade="st.grade" />
                  </td>
                  <td class="text-secondary">{{ st.remarks || '—' }}</td>
                  <td>
                    <span v-if="st.is_saved" class="badge-saved">Recorded by Teacher</span>
                    <span v-else class="badge-pending">Pending Entry</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 4: RESULTS ANALYTICS -->
    <div v-if="activeTab === 'results' && profile" class="tab-pane">
      <div class="analytics-container">
        <div class="analytics-metrics-row">
          <div class="metric-box">
            <span class="m-label">Average Score</span>
            <span class="m-val">{{ profile.average_score ?? '—' }}</span>
          </div>
          <div class="metric-box">
            <span class="m-label">Highest Score</span>
            <span class="m-val text-emerald">{{ profile.highest_score ?? '—' }}</span>
          </div>
          <div class="metric-box">
            <span class="m-label">Lowest Score</span>
            <span class="m-val text-amber">{{ profile.lowest_score ?? '—' }}</span>
          </div>
          <div class="metric-box">
            <span class="m-label">Pass Percentage</span>
            <span class="m-val">{{ profile.pass_rate }}%</span>
          </div>
        </div>

        <!-- Progress Overview -->
        <div class="progress-overview-card">
          <h2 class="card-title">Score Completion Overview</h2>
          <ResultProgressBar
            :entered="profile.results_count"
            :total="profile.enrolled_count"
            :percentage="profile.completion_percentage"
          />
          <p class="progress-note">
            {{ profile.results_count }} out of {{ profile.enrolled_count }} enrolled students have graded marks recorded in PostgreSQL.
          </p>
        </div>
      </div>
    </div>

    <!-- TAB 5: PUBLICATION -->
    <div v-if="activeTab === 'publication' && profile" class="tab-pane">
      <div class="publication-pane-card">
        <div class="pub-status-box" :class="{ published: profile.exam.status === 'PUBLISHED' }">
          <div class="pub-icon-wrapper">
            <svg v-if="profile.exam.status === 'PUBLISHED'" class="pub-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <svg v-else class="pub-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
          </div>
          <div>
            <h2 class="pub-title">
              Current State: {{ profile.exam.status === 'PUBLISHED' ? 'Published to Student Portal' : 'Unpublished (Draft / Completed)' }}
            </h2>
            <p class="pub-desc">
              {{
                profile.exam.status === 'PUBLISHED'
                  ? 'All scores and grades for this examination are currently visible to authorized student and guardian accounts.'
                  : 'Scores and grades are currently hidden from students. You can publish once marks entry and administrative reviews are finalized.'
              }}
            </p>
          </div>
        </div>

        <div class="pub-actions-row">
          <button
            v-if="profile.exam.status !== 'PUBLISHED'"
            type="button"
            class="publish-btn"
            @click="openPublishModal(true)"
          >
            Publish Results to Student Portal
          </button>
          <button
            v-else
            type="button"
            class="unpublish-btn"
            @click="openPublishModal(false)"
          >
            Unpublish (Revoke Student Portal Access)
          </button>
        </div>
      </div>
    </div>

    <!-- TAB 6: REPORT CARD -->
    <div v-if="activeTab === 'report-card' && profile" class="tab-pane">
      <div class="report-card-container">
        <!-- Student Selector Bar -->
        <div class="student-selector-bar">
          <label class="selector-label">Select Student for Report Card:</label>
          <select v-model="selectedStudentIdForReport" class="student-select">
            <option
              v-for="st in profile.student_sheet"
              :key="st.student_id"
              :value="st.student_id"
            >
              {{ st.student_name }} ({{ st.admission_number }})
            </option>
          </select>
        </div>

        <!-- Render Report Card -->
        <ExamReportCard :report-card="studentReportCard" />
      </div>
    </div>

    <!-- Edit Exam Details Modal -->
    <div v-if="isEditModalOpen" class="modal-overlay" @click.self="isEditModalOpen = false">
      <div class="modal-card">
        <div class="modal-header">
          <h2 class="modal-title">Edit Examination Details</h2>
          <button type="button" class="close-btn" @click="isEditModalOpen = false">&times;</button>
        </div>

        <form class="modal-body" @submit.prevent="handleSaveEdit">
          <div class="form-group">
            <label class="field-label">Exam Name</label>
            <input v-model="editForm.name" type="text" class="form-input" required />
          </div>

          <div class="form-grid-2">
            <div class="form-group">
              <label class="field-label">Exam Type</label>
              <select v-model="editForm.exam_type" class="form-select" required>
                <option value="Final">Final Examination</option>
                <option value="Mid-Term">Mid-Term Examination</option>
                <option value="Monthly Test">Monthly Examination</option>
                <option value="Quiz">Quiz</option>
              </select>
            </div>
            <div class="form-group">
              <label class="field-label">Academic Year</label>
              <input v-model="editForm.academic_year" type="text" class="form-input" required />
            </div>
          </div>

          <div class="form-grid-2">
            <div class="form-group">
              <label class="field-label">Start Date</label>
              <input v-model="editForm.start_date" type="date" class="form-input" required />
            </div>
            <div class="form-group">
              <label class="field-label">End Date</label>
              <input v-model="editForm.end_date" type="date" class="form-input" />
            </div>
          </div>

          <div class="form-grid-2">
            <div class="form-group">
              <label class="field-label">Start Time</label>
              <input v-model="editForm.start_time" type="time" class="form-input" />
            </div>
            <div class="form-group">
              <label class="field-label">End Time</label>
              <input v-model="editForm.end_time" type="time" class="form-input" />
            </div>
          </div>

          <div class="form-grid-2">
            <div class="form-group">
              <label class="field-label">Result Submission Deadline</label>
              <input v-model="editForm.result_submission_deadline" type="datetime-local" class="form-input" />
            </div>
            <div class="form-group">
              <label class="field-label">Lifecycle Status</label>
              <select v-model="editForm.status" class="form-select" required>
                <option value="DRAFT">Draft</option>
                <option value="SCHEDULED">Scheduled</option>
                <option value="OPEN_FOR_RESULTS">Open for Results</option>
                <option value="ONGOING">Ongoing</option>
                <option value="COMPLETED">Completed</option>
                <option value="CLOSED">Closed</option>
                <option value="PUBLISHED">Published</option>
                <option value="CANCELLED">Cancelled</option>
              </select>
            </div>
          </div>

          <div class="form-grid-2">
            <div class="form-group">
              <label class="field-label">Maximum Marks</label>
              <input v-model="editForm.max_marks" type="number" class="form-input" required />
            </div>
            <div class="form-group">
              <label class="field-label">Passing Marks</label>
              <input v-model="editForm.pass_marks" type="number" class="form-input" required />
            </div>
          </div>

          <div class="form-group">
            <label class="field-label">Teacher Instructions / Notes</label>
            <textarea
              v-model="editForm.instructions"
              rows="2"
              class="form-input"
              placeholder="Instructions or guidelines for teachers submitting scores..."
            ></textarea>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn-cancel" @click="isEditModalOpen = false">Cancel</button>
            <button type="submit" class="btn-save" :disabled="isSavingEdit">
              {{ isSavingEdit ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Extend Deadline Modal -->
    <div v-if="isExtendModalOpen" class="modal-overlay" @click.self="isExtendModalOpen = false">
      <div class="modal-card">
        <div class="modal-header">
          <h2 class="modal-title">Extend Result Submission Deadline</h2>
          <button type="button" class="close-btn" @click="isExtendModalOpen = false">&times;</button>
        </div>
        <form class="modal-body" @submit.prevent="handleConfirmExtend">
          <div v-if="profile?.exam?.result_submission_deadline" class="row-item" style="margin-bottom: 0.75rem;">
            <span class="k">Current Deadline:</span>
            <span class="v font-bold">{{ formatDateTime(profile.exam.result_submission_deadline) }}</span>
          </div>

          <div class="form-group">
            <label class="field-label">New Submission Deadline <span style="color: #ef4444;">*</span></label>
            <input v-model="extendDeadlineVal" type="datetime-local" class="form-input" required />
            <div style="display: flex; gap: 0.5rem; margin-top: 0.35rem;">
              <button type="button" class="action-btn outline" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;" @click="setProfileExtendPreset(7)">+7 Days</button>
              <button type="button" class="action-btn outline" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;" @click="setProfileExtendPreset(14)">+14 Days</button>
              <button type="button" class="action-btn outline" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;" @click="setProfileExtendPreset(30)">+1 Month</button>
            </div>
          </div>

          <div class="form-group">
            <label class="field-label">Reason for Extension (Audit Trail) <span style="color: #ef4444;">*</span></label>
            <textarea
              v-model="extendReason"
              rows="3"
              class="form-input"
              placeholder="e.g. Granted additional time due to laboratory equipment calibration..."
              required
            ></textarea>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn-cancel" @click="isExtendModalOpen = false">Cancel</button>
            <button type="submit" class="btn-save" :disabled="isExtending">
              {{ isExtending ? 'Updating...' : 'Confirm Deadline Extension' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Reopen Submissions Modal -->
    <div v-if="isReopenModalOpen" class="modal-overlay" @click.self="isReopenModalOpen = false">
      <div class="modal-card">
        <div class="modal-header">
          <h2 class="modal-title">Reopen Results Submission</h2>
          <button type="button" class="close-btn" @click="isReopenModalOpen = false">&times;</button>
        </div>
        <form class="modal-body" @submit.prevent="handleConfirmReopen">
          <div style="background: #eff6ff; border: 1px solid #bfdbfe; color: #1e40af; padding: 0.75rem; border-radius: 8px; font-size: 0.8125rem; margin-bottom: 0.75rem;">
            <strong>Reopen Authorization:</strong> This will transition the examination state to <code>OPEN_FOR_RESULTS</code> and allow teachers to modify and submit scores. All existing records are preserved.
          </div>

          <div class="form-group">
            <label class="field-label">Reason for Reopening <span style="color: #ef4444;">*</span></label>
            <textarea
              v-model="reopenReason"
              rows="3"
              class="form-input"
              placeholder="e.g. Authorized moderation of student scores following internal review..."
              required
            ></textarea>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn-cancel" @click="isReopenModalOpen = false">Cancel</button>
            <button type="submit" class="btn-save" style="background: #059669; border-color: #047857;" :disabled="isReopening">
              {{ isReopening ? 'Reopening...' : 'Confirm Reopen Submissions' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirm Modal -->
    <ExamConfirmDialog
      :is-open="isDeleteModalOpen"
      title="Delete Examination"
      :message="`Are you sure you want to delete '${profile?.exam?.name}'? This will permanently delete this examination record.`"
      confirm-text="Delete"
      :is-dangerous="true"
      :is-loading="isDeleting"
      @confirm="handleConfirmDelete"
      @cancel="isDeleteModalOpen = false"
    />

    <!-- Publish Modal -->
    <PublishModal
      :is-open="isPublishModalOpen"
      :exam="profile?.exam || null"
      :is-publishing="isPublishAction"
      :is-loading="isSubmittingPublish"
      @confirm="handleConfirmPublish"
      @cancel="isPublishModalOpen = false"
    />
  </div>
</template>

<style scoped>
.exam-profile-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  max-width: 1300px;
  margin: 0 auto;
  box-sizing: border-box;
}

.profile-breadcrumb {
  margin-bottom: 0.25rem;
}

.back-link {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0.25rem 0;
  gap: 0.35rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #4f46e5;
  background: none;
  border: none;
  cursor: pointer;
}

.back-link:hover {
  text-decoration: underline;
}

.back-icon {
  width: 16px;
  height: 16px;
}

.alert {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
}
.alert.success { background-color: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
.alert.error { background-color: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
.alert-dismiss { font-size: 1.25rem; background: none; border: none; cursor: pointer; color: inherit; }

/* Profile Header Card */
.profile-header-card {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.header-main {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.title-area {
  flex: 1;
  min-width: 0;
}

.badge-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.exam-type-pill {
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  background-color: #eff6ff;
  color: #2563eb;
  border-radius: 4px;
}

.year-pill {
  font-size: 0.6875rem;
  font-weight: 600;
  color: #64748b;
}

.profile-exam-name {
  font-size: 1.625rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
  line-height: 1.25;
}

.exam-details-strip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  color: #475569;
  margin-top: 0.5rem;
  flex-wrap: wrap;
}

.strip-icon {
  width: 15px;
  height: 15px;
  color: #94a3b8;
  display: inline-block;
  vertical-align: middle;
}

.separator {
  color: #cbd5e1;
}

.header-actions-group {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  flex-wrap: wrap;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.5rem 1rem;
  font-size: 0.8125rem;
  font-weight: 600;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.action-btn.primary {
  background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
  color: #ffffff;
  border: 1px solid #4338ca;
}

.action-btn.outline {
  background-color: #ffffff;
  color: #334155;
  border: 1px solid #cbd5e1;
}

.action-btn.publish {
  background-color: #ecfdf5;
  color: #047857;
  border: 1px solid #a7f3d0;
}

.action-btn.unpublish {
  background-color: #fffbeb;
  color: #b45309;
  border: 1px solid #fde68a;
}

.action-btn.danger {
  background-color: #fef2f2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.act-icon {
  width: 15px;
  height: 15px;
}

/* KPI Cards */
.summary-kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.875rem;
}

.kpi-card {
  display: flex;
  flex-direction: column;
  padding: 1rem;
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}

.kpi-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.kpi-val {
  font-size: 1.375rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0.25rem 0;
}

.kpi-sub {
  font-size: 0.75rem;
  color: #94a3b8;
}

.text-emerald {
  color: #059669;
}

/* Tab Strip */
.tabs-strip-container {
  border-bottom: 1px solid #e2e8f0;
  overflow-x: auto;
  scrollbar-width: thin;
}

.tabs-strip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: max-content;
}

.tab-item {
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
  border: none;
  background: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.15s ease;
}

.tab-item:hover {
  color: #0f172a;
}

.tab-item.active {
  color: #4f46e5;
  border-bottom-color: #4f46e5;
}

/* Tab Panes */
.tab-pane {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Overview */
.overview-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.overview-card {
  padding: 1.25rem;
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}

.card-title {
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 1rem 0;
}

.meta-rows {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.row-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.35rem 0;
  border-bottom: 1px solid #f8fafc;
  font-size: 0.8125rem;
}

.row-item .k {
  color: #64748b;
  font-weight: 500;
}

.row-item .v {
  color: #0f172a;
  font-weight: 600;
}

/* Roster */
.roster-card {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
}

.roster-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
}

.roster-count {
  font-size: 0.8125rem;
  color: #64748b;
}

.table-responsive {
  overflow-x: auto;
}

.roster-table {
  width: 100%;
  min-width: 720px;
  border-collapse: collapse;
  text-align: left;
}

.roster-table th {
  background-color: #f8fafc;
  padding: 0.625rem 1rem;
  font-size: 0.75rem;
  font-weight: 700;
  color: #475569;
  text-transform: uppercase;
  border-bottom: 1px solid #e2e8f0;
}

.roster-table td {
  padding: 0.625rem 1rem;
  font-size: 0.8125rem;
  color: #0f172a;
  border-bottom: 1px solid #f1f5f9;
}

.badge-saved {
  font-size: 0.6875rem;
  font-weight: 600;
  color: #059669;
  background-color: #ecfdf5;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.badge-pending {
  font-size: 0.6875rem;
  color: #94a3b8;
}

/* Marks Entry View Responsive Switch */
.desktop-marks-view {
  display: block;
  width: 100%;
}

.mobile-marks-view {
  display: none;
  width: 100%;
}

@media (max-width: 768px) {
  .desktop-marks-view {
    display: none;
  }
  .mobile-marks-view {
    display: block;
  }
}

/* Analytics */
.analytics-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.analytics-metrics-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.875rem;
}

.metric-box {
  display: flex;
  flex-direction: column;
  padding: 1rem;
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.m-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
}

.m-val {
  font-size: 1.375rem;
  font-weight: 800;
  color: #0f172a;
  margin-top: 0.25rem;
}

.progress-overview-card {
  padding: 1.25rem;
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.progress-note {
  font-size: 0.8125rem;
  color: #64748b;
  margin: 0;
}

/* Publication Pane */
.publication-pane-card {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding: 1.5rem;
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}

.pub-status-box {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.25rem;
  border-radius: 8px;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
}

.pub-status-box.published {
  background-color: #f0fdf4;
  border-color: #bbf7d0;
}

.pub-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #e2e8f0;
  color: #475569;
  flex-shrink: 0;
}

.published .pub-icon-wrapper {
  background-color: #dcfce7;
  color: #16a34a;
}

.pub-icon {
  width: 22px;
  height: 22px;
}

.pub-title {
  font-size: 1.0625rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.25rem 0;
}

.pub-desc {
  font-size: 0.875rem;
  color: #475569;
  margin: 0;
  line-height: 1.45;
}

.publish-btn {
  padding: 0.65rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #ffffff;
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  border: 1px solid #047857;
  border-radius: 6px;
  cursor: pointer;
}

.unpublish-btn {
  padding: 0.65rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #ffffff;
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
  border: 1px solid #b45309;
  border-radius: 6px;
  cursor: pointer;
}

/* Report Card Tab */
.report-card-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.student-selector-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  flex-wrap: wrap;
}

.selector-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #334155;
}

.student-select {
  padding: 0.4rem 0.75rem;
  font-size: 0.875rem;
  color: #0f172a;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  background-color: rgba(15, 23, 42, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.modal-card {
  width: 100%;
  max-width: 500px;
  background-color: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.close-btn {
  font-size: 1.5rem;
  line-height: 1;
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  min-width: 40px;
  min-height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  flex-shrink: 0;
}

.modal-body {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.field-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #334155;
}

.form-input, .form-select {
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  outline: none;
}

.form-grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.875rem;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid #f1f5f9;
}

.btn-cancel {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
  background-color: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  cursor: pointer;
}

.btn-save {
  padding: 0.5rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #ffffff;
  background: #4f46e5;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.teacher-workflow-pane {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.workflow-info-banner {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1.25rem 1.5rem;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 12px;
}

.banner-icon-circle {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #dbeafe;
  color: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.banner-icon-circle svg {
  width: 24px;
  height: 24px;
}

.banner-text-wrap {
  flex: 1;
}

.banner-title {
  font-size: 1rem;
  font-weight: 700;
  color: #1e3a8a;
  margin: 0 0 0.25rem 0;
}

.banner-desc {
  font-size: 0.875rem;
  color: #1e40af;
  margin: 0;
  line-height: 1.5;
}

.banner-action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #ffffff;
  background: #2563eb;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.15s ease;
}

.banner-action-btn:hover:not(:disabled) {
  background: #1d4ed8;
}

.banner-action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.teacher-status-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.t-card {
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1rem 1.25rem;
  gap: 0.35rem;
}

.tc-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
  font-weight: 600;
}

.tc-val {
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
}

.tc-sub {
  font-size: 0.75rem;
  color: #64748b;
}

.tc-status-wrap {
  display: flex;
  align-items: center;
  margin-top: 0.1rem;
}

.student-sheet-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}

.sheet-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.sheet-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.sheet-subtitle {
  font-size: 0.8125rem;
  color: #64748b;
  margin: 0.2rem 0 0 0;
}

.refresh-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.4rem 0.85rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #475569;
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  cursor: pointer;
}

.refresh-btn svg {
  width: 14px;
  height: 14px;
}

.refresh-btn:hover {
  background: #f1f5f9;
}

.sheet-table-wrap {
  overflow-x: auto;
}

.sheet-table {
  width: 100%;
  min-width: 680px;
  border-collapse: collapse;
  font-size: 0.875rem;
  text-align: left;
}

.sheet-table th {
  background: #f8fafc;
  color: #475569;
  font-weight: 600;
  padding: 0.75rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
}

.sheet-table td {
  padding: 0.85rem 1.25rem;
  border-bottom: 1px solid #f1f5f9;
  color: #1e293b;
}

.sheet-table tr:hover {
  background: #f8fafc;
}

.attendance-pill {
  display: inline-flex;
  padding: 0.2rem 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 4px;
}

.attendance-pill.present {
  background: #dcfce7;
  color: #15803d;
}

.attendance-pill.absent {
  background: #fee2e2;
  color: #b91c1c;
}

.attendance-pill.excused {
  background: #fef3c7;
  color: #b45309;
}

@media (max-width: 900px) {
  .teacher-status-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .workflow-info-banner {
    flex-direction: column;
    align-items: flex-start;
  }
  .summary-kpi-grid, .analytics-metrics-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .overview-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .header-main {
    flex-direction: column;
    align-items: flex-start;
  }
  .header-actions-group {
    width: 100%;
  }
  .header-actions-group .action-btn {
    flex: 1;
    justify-content: center;
  }
  .profile-exam-name {
    font-size: 1.25rem;
  }
}
</style>
