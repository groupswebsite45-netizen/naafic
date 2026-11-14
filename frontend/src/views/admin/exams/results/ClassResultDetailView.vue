<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { resultWorkflowService } from '../../../../services/resultWorkflowService';
import {
  ClassResultDashboardResponse,
  ClassSubjectMatrixItem,
  SubmissionReviewDetail,
  ClassReceiptSummary,
} from '../../../../types/resultWorkflow';
import ResultStatusBadge from '../../../../components/results/ResultStatusBadge.vue';
import ClassResultMatrix from '../../../../components/results/ClassResultMatrix.vue';
import StudentReceiptTable from '../../../../components/results/StudentReceiptTable.vue';
import ResultReviewModal from '../../../../components/results/ResultReviewModal.vue';
import ReturnSubmissionModal from '../../../../components/results/ReturnSubmissionModal.vue';
import ReleaseResultsModal from '../../../../components/results/ReleaseResultsModal.vue';

const route = useRoute();
const router = useRouter();

const classId = computed(() => Number(route.params.classId));
const academicYear = ref<string>((route.query.academic_year as string) || '2026/2027');
const examName = ref<string>((route.query.exam_name as string) || 'Final Examination 2026');

const isLoading = ref(true);
const classData = ref<ClassResultDashboardResponse | null>(null);
const receiptData = ref<ClassReceiptSummary | null>(null);
const activeTab = ref<'matrix' | 'receipt'>('matrix');

// Modal States
const isReviewModalOpen = ref(false);
const activeSubmission = ref<SubmissionReviewDetail | null>(null);
const isReviewLoading = ref(false);
const isReviewProcessing = ref(false);

const isReturnModalOpen = ref(false);
const subjectToReturn = ref<ClassSubjectMatrixItem | null>(null);
const isReturnProcessing = ref(false);

const isReleaseModalOpen = ref(false);
const isReleaseProcessing = ref(false);

const notification = ref<{ type: 'success' | 'error'; message: string } | null>(null);

function showNotification(type: 'success' | 'error', message: string) {
  notification.value = { type, message };
  setTimeout(() => {
    notification.value = null;
  }, 6000);
}

async function loadData() {
  if (!classId.value) return;
  isLoading.value = true;
  try {
    const [detailRes, receiptRes] = await Promise.all([
      resultWorkflowService.getClassResultDetail(classId.value, academicYear.value, examName.value),
      resultWorkflowService.getClassReceiptStatus(classId.value, academicYear.value, examName.value).catch(() => null),
    ]);
    classData.value = detailRes;
    receiptData.value = receiptRes;
  } catch (err: any) {
    showNotification('error', err?.response?.data?.detail || 'Failed to load class result details.');
  } finally {
    isLoading.value = false;
  }
}

// Inspect / Review Subject
async function handleReviewSubject(subject: ClassSubjectMatrixItem) {
  if (!subject.submission_id) return;
  subjectToReturn.value = subject;
  isReviewLoading.value = true;
  isReviewModalOpen.value = true;
  try {
    activeSubmission.value = await resultWorkflowService.getSubmissionDetail(subject.submission_id);
  } catch (err: any) {
    showNotification('error', err?.response?.data?.detail || 'Failed to fetch submission details.');
    isReviewModalOpen.value = false;
  } finally {
    isReviewLoading.value = false;
  }
}

// Admin Action: Approve Submission
async function handleApprove() {
  if (!activeSubmission.value) return;
  isReviewProcessing.value = true;
  try {
    const res = await resultWorkflowService.approveSubmission(activeSubmission.value.id);
    showNotification('success', res.message || 'Submission approved successfully.');
    isReviewModalOpen.value = false;
    await loadData();
  } catch (err: any) {
    showNotification('error', err?.response?.data?.detail || 'Failed to approve submission.');
  } finally {
    isReviewProcessing.value = false;
  }
}

// Open Return Modal from Review Modal
function handleOpenReturn() {
  isReturnModalOpen.value = true;
}

// Admin Action: Confirm Return for Correction
async function handleConfirmReturn(reason: string) {
  if (!activeSubmission.value) return;
  isReturnProcessing.value = true;
  try {
    const res = await resultWorkflowService.returnSubmission(activeSubmission.value.id, reason);
    showNotification('success', res.message || 'Submission returned to teacher for correction.');
    isReturnModalOpen.value = false;
    isReviewModalOpen.value = false;
    await loadData();
  } catch (err: any) {
    showNotification('error', err?.response?.data?.detail || 'Failed to return submission.');
  } finally {
    isReturnProcessing.value = false;
  }
}

// Admin Action: Class Result Release
async function handleConfirmRelease(releaseType: 'FULL' | 'PARTIAL', notes?: string) {
  if (!classId.value) return;
  isReleaseProcessing.value = true;
  try {
    const res = await resultWorkflowService.releaseClassResults(classId.value, {
      academic_year: academicYear.value,
      exam_name: examName.value,
      release_type: releaseType,
      notes,
    });
    showNotification('success', `${res.message} Batch Code: ${res.batch_code}`);
    isReleaseModalOpen.value = false;
    await loadData();
  } catch (err: any) {
    showNotification('error', err?.response?.data?.detail || 'Failed to release results.');
  } finally {
    isReleaseProcessing.value = false;
  }
}

onMounted(() => {
  loadData();
});

watch([academicYear, examName], () => {
  loadData();
});
</script>

<template>
  <div class="class-detail-page">
    <!-- Top Bar Navigation -->
    <div class="page-nav-bar">
      <button type="button" class="back-link" @click="router.push('/admin/exams/results')">
        <svg class="back-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Back to Results Overview
      </button>

      <div class="context-tags">
        <span class="context-tag academic-year-tag">{{ academicYear }}</span>
        <span class="context-tag exam-tag">{{ examName }}</span>
      </div>
    </div>

    <!-- Notification Banner -->
    <div v-if="notification" class="notification-banner" :class="notification.type">
      <span>{{ notification.message }}</span>
      <button type="button" class="notif-close" @click="notification = null">&times;</button>
    </div>

    <!-- Class Header Card -->
    <div class="class-header-card">
      <div class="header-main">
        <div class="title-group">
          <div class="pre-heading">EDUCATION MANAGEMENT SYSTEM &bull; CLASS RESULTS</div>
          <h1 class="class-title">{{ classData?.class_name || 'Loading Class...' }}</h1>
          <p class="class-subtitle">
            Curriculum tracking &bull; {{ classData?.subjects_count || 0 }} Subjects &bull; {{ classData?.students_count || 0 }} Enrolled Students
          </p>
        </div>
        <div class="header-status-box">
          <ResultStatusBadge v-if="classData" :status="classData.status" size="md" />
          <button
            type="button"
            class="btn-release-action"
            :disabled="!classData"
            @click="isReleaseModalOpen = true"
          >
            <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            Release Class Results
          </button>
        </div>
      </div>

      <!-- Key Metrics Row -->
      <div class="metrics-strip">
        <div class="metric-item">
          <span class="metric-label">ENROLLED STUDENTS</span>
          <span class="metric-value">{{ classData?.students_count || 0 }}</span>
        </div>
        <div class="metric-item">
          <span class="metric-label">SUBJECTS</span>
          <span class="metric-value">{{ classData?.subjects_count || 0 }}</span>
        </div>
        <div class="metric-item">
          <span class="metric-label">EXPECTED RESULTS</span>
          <span class="metric-value">{{ classData?.expected_results || 0 }}</span>
        </div>
        <div class="metric-item">
          <span class="metric-label">SUBMITTED</span>
          <span class="metric-value text-amber">{{ classData?.submitted_results || 0 }}</span>
        </div>
        <div class="metric-item">
          <span class="metric-label">APPROVED</span>
          <span class="metric-value text-blue">{{ classData?.approved_results || 0 }}</span>
        </div>
        <div class="metric-item">
          <span class="metric-label">RELEASED</span>
          <span class="metric-value text-emerald">{{ classData?.released_results || 0 }}</span>
        </div>
        <div class="metric-item">
          <span class="metric-label">PENDING</span>
          <span class="metric-value" :class="{ 'text-red': (classData?.pending_results || 0) > 0 }">
            {{ classData?.pending_results || 0 }}
          </span>
        </div>
      </div>
    </div>

    <!-- Tab Navigation -->
    <div class="tab-nav-bar">
      <button
        type="button"
        class="tab-btn"
        :class="{ active: activeTab === 'matrix' }"
        @click="activeTab = 'matrix'"
      >
        <svg class="tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
        </svg>
        Subject Submission Matrix ({{ classData?.subjects_matrix?.length || 0 }})
      </button>

      <button
        type="button"
        class="tab-btn"
        :class="{ active: activeTab === 'receipt' }"
        @click="activeTab = 'receipt'"
      >
        <svg class="tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        Student Result Delivery & Receipt ({{ receiptData?.total_students || 0 }})
      </button>
    </div>

    <!-- Active Tab Content -->
    <div class="tab-content-area">
      <div v-if="activeTab === 'matrix'">
        <ClassResultMatrix
          :subjects="classData?.subjects_matrix || []"
          :is-loading="isLoading"
          @review="handleReviewSubject"
        />
      </div>

      <div v-else-if="activeTab === 'receipt'">
        <StudentReceiptTable
          :receipts="receiptData?.receipts || []"
          :released-count="receiptData?.released_students || 0"
          :viewed-count="receiptData?.viewed_students || 0"
          :not-viewed-count="receiptData?.not_viewed_students || 0"
          :is-loading="isLoading"
        />
      </div>
    </div>

    <!-- Modals -->
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
      :subject-name="subjectToReturn?.subject_name || ''"
      :class-name="classData?.class_name || ''"
      :is-processing="isReturnProcessing"
      @close="isReturnModalOpen = false"
      @confirm="handleConfirmReturn"
    />

    <ReleaseResultsModal
      v-if="classData"
      :is-open="isReleaseModalOpen"
      :class-name="classData.class_name"
      :exam-name="examName"
      :academic-year="academicYear"
      :students-count="classData.students_count"
      :subjects-count="classData.subjects_count"
      :expected-results="classData.expected_results"
      :approved-results="classData.approved_results"
      :pending-results="classData.pending_results"
      :is-processing="isReleaseProcessing"
      @close="isReleaseModalOpen = false"
      @confirm="handleConfirmRelease"
    />
  </div>
</template>

<style scoped>
.class-detail-page {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  box-sizing: border-box;
}

.page-nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  color: #38bdf8;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0.25rem 0;
}

.back-link:hover {
  text-decoration: underline;
  color: #7dd3fc;
}

.back-icon {
  width: 1.125rem;
  height: 1.125rem;
}

.context-tags {
  display: flex;
  gap: 0.5rem;
}

.context-tag {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.65rem;
  border-radius: 6px;
}

.academic-year-tag {
  background-color: #334155;
  color: #f1f5f9;
}

.exam-tag {
  background-color: rgba(2, 132, 199, 0.2);
  color: #38bdf8;
  border: 1px solid rgba(2, 132, 199, 0.4);
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

.class-header-card {
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.header-main {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.pre-heading {
  font-size: 0.6875rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #94a3b8;
  text-transform: uppercase;
}

.class-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #ffffff;
  margin: 0.2rem 0;
}

.class-subtitle {
  font-size: 0.8125rem;
  color: #94a3b8;
  margin: 0;
}

.header-status-box {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  flex-wrap: wrap;
}

.btn-release-action {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #059669;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  padding: 0.6rem 1.15rem;
  font-size: 0.875rem;
  font-weight: 700;
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.btn-release-action:hover:not(:disabled) {
  background-color: #047857;
}

.btn-release-action:disabled {
  background-color: #334155;
  color: #64748b;
  cursor: not-allowed;
}

.btn-icon {
  width: 1.125rem;
  height: 1.125rem;
}

.metrics-strip {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.75rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 0.85rem;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  text-align: center;
}

.metric-label {
  font-size: 0.625rem;
  font-weight: 700;
  color: #64748b;
  letter-spacing: 0.04em;
}

.metric-value {
  font-size: 1.25rem;
  font-weight: 800;
  color: #f1f5f9;
}

.text-amber { color: #fbbf24; }
.text-blue { color: #60a5fa; }
.text-emerald { color: #34d399; }
.text-red { color: #f87171; }

.tab-nav-bar {
  display: flex;
  gap: 0.5rem;
  border-bottom: 1px solid #334155;
  padding-bottom: 0.25rem;
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: #94a3b8;
  padding: 0.65rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.tab-btn:hover {
  color: #f1f5f9;
}

.tab-btn.active {
  color: #38bdf8;
  border-bottom-color: #38bdf8;
}

.tab-icon {
  width: 1.125rem;
  height: 1.125rem;
}

.tab-content-area {
  width: 100%;
}

@media (max-width: 1024px) {
  .metrics-strip {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 640px) {
  .class-detail-page {
    padding: 1rem;
  }
  .metrics-strip {
    grid-template-columns: repeat(2, 1fr);
  }
  .header-main {
    flex-direction: column;
  }
  .header-status-box {
    width: 100%;
    justify-content: space-between;
  }
  .btn-release-action {
    width: 100%;
    justify-content: center;
  }
}
</style>
