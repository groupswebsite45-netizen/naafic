<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { examService } from '../../../services/examService';
import { Exam, ExamSummary, ExamFilterOptions } from '../../../types/school';

import ExamHeader from './components/ExamHeader.vue';
import ExamStats from './components/ExamStats.vue';
import ExamToolbar from './components/ExamToolbar.vue';
import ExamActiveChips from './components/ExamActiveChips.vue';
import ExamFilterDrawer from './components/ExamFilterDrawer.vue';
import ExamTable from './components/ExamTable.vue';
import ExamCardList from './components/ExamCardList.vue';
import ExamSkeleton from './components/ExamSkeleton.vue';
import ExamEmptyState from './components/ExamEmptyState.vue';
import ExamConfirmDialog from './components/ExamConfirmDialog.vue';
import PublishModal from './components/PublishModal.vue';

const router = useRouter();

// State
const exams = ref<Exam[]>([]);
const summary = ref<ExamSummary | null>(null);
const filterOptions = ref<ExamFilterOptions | null>(null);
const isLoading = ref(false);
const isLoadingSummary = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

// Filters
const filters = reactive({
  query: '',
  academic_year: '2026/2027',
  exam_type: '',
  class_id: undefined as number | undefined,
  subject_id: undefined as number | undefined,
  status: '',
});

const isFilterDrawerOpen = ref(false);

// Pagination
const currentPage = ref(1);
const pageSize = ref(15);
const totalExams = ref(0);

// Modals
const isDeleteModalOpen = ref(false);
const isDeleting = ref(false);
const examToDelete = ref<Exam | null>(null);

const isPublishModalOpen = ref(false);
const isPublishingAction = ref(false); // true = publish, false = unpublish
const isSubmittingPublish = ref(false);
const selectedExamForPublish = ref<Exam | null>(null);

// Lookups for chips
const classLookup = computed(() => {
  const map: Record<number, string> = {};
  filterOptions.value?.classes.forEach((c) => {
    map[c.id] = c.name;
  });
  return map;
});

const subjectLookup = computed(() => {
  const map: Record<number, string> = {};
  filterOptions.value?.subjects.forEach((s) => {
    map[s.id] = s.name;
  });
  return map;
});

const activeFilterCount = computed(() => {
  let count = 0;
  if (filters.academic_year) count++;
  if (filters.exam_type) count++;
  if (filters.class_id) count++;
  if (filters.subject_id) count++;
  if (filters.status) count++;
  return count;
});

const hasAnyFilters = computed(() => {
  return Boolean(
    filters.query ||
    filters.academic_year ||
    filters.exam_type ||
    filters.class_id ||
    filters.subject_id ||
    filters.status
  );
});

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(totalExams.value / pageSize.value));
});

const paginatedExams = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return exams.value.slice(start, start + pageSize.value);
});

// Load summary from API
async function loadSummary() {
  isLoadingSummary.value = true;
  try {
    const data = await examService.getSummary(filters.academic_year || undefined);
    summary.value = data;
  } catch (err: any) {
    console.error('Failed to load exam summary:', err);
  } finally {
    isLoadingSummary.value = false;
  }
}

// Load filter options from API
async function loadFilterOptions() {
  try {
    const data = await examService.getFilterOptions();
    filterOptions.value = data;
  } catch (err: any) {
    console.error('Failed to load filter options:', err);
  }
}

// Load exams from API
async function loadExams() {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    const data = await examService.getExams({
      query: filters.query.trim() || undefined,
      academic_year: filters.academic_year || undefined,
      exam_type: filters.exam_type || undefined,
      class_id: filters.class_id || undefined,
      subject_id: filters.subject_id || undefined,
      status: filters.status || undefined,
      skip: 0,
      limit: 100,
    });
    exams.value = Array.isArray(data) ? data : [];
    totalExams.value = exams.value.length;
    currentPage.value = 1;
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to load examinations from PostgreSQL.';
  } finally {
    isLoading.value = false;
  }
}

// Handlers for Navigation & Actions
function handleViewExam(exam: Exam) {
  router.push(`/admin/exams/${exam.id}`);
}

function handleEditExam(exam: Exam) {
  router.push(`/admin/exams/${exam.id}?tab=overview&edit=true`);
}

function handleEnterMarks(exam: Exam) {
  router.push(`/admin/exams/${exam.id}?tab=marks`);
}

function handleReviewResults(exam: Exam) {
  router.push(`/admin/exams/${exam.id}?tab=results`);
}

function openPublishModal(exam: Exam) {
  selectedExamForPublish.value = exam;
  isPublishingAction.value = true;
  isPublishModalOpen.value = true;
}

function openUnpublishModal(exam: Exam) {
  selectedExamForPublish.value = exam;
  isPublishingAction.value = false;
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
    await Promise.all([loadExams(), loadSummary()]);
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to update publication status.';
  } finally {
    isSubmittingPublish.value = false;
  }
}

function openDeleteModal(exam: Exam) {
  examToDelete.value = exam;
  isDeleteModalOpen.value = true;
}

async function handleConfirmDelete() {
  if (!examToDelete.value) return;
  isDeleting.value = true;
  try {
    await examService.deleteExam(examToDelete.value.id);
    successMessage.value = `Examination "${examToDelete.value.name}" deleted successfully.`;
    isDeleteModalOpen.value = false;
    await Promise.all([loadExams(), loadSummary()]);
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to delete examination.';
  } finally {
    isDeleting.value = false;
  }
}

function removeFilter(key: string) {
  if (key === 'query') filters.query = '';
  if (key === 'academic_year') filters.academic_year = '';
  if (key === 'exam_type') filters.exam_type = '';
  if (key === 'class_id') filters.class_id = undefined;
  if (key === 'subject_id') filters.subject_id = undefined;
  if (key === 'status') filters.status = '';
  loadExams();
}

function clearAllFilters() {
  filters.query = '';
  filters.academic_year = '';
  filters.exam_type = '';
  filters.class_id = undefined;
  filters.subject_id = undefined;
  filters.status = '';
  loadExams();
  loadSummary();
}

function applyDrawerFilters(newFilters: any) {
  filters.academic_year = newFilters.academic_year;
  filters.exam_type = newFilters.exam_type;
  filters.class_id = newFilters.class_id;
  filters.subject_id = newFilters.subject_id;
  filters.status = newFilters.status;
  loadExams();
  loadSummary();
}

// Watch filters
watch(() => filters.academic_year, () => {
  loadExams();
  loadSummary();
});

watch(() => filters.status, () => {
  loadExams();
});

let searchTimeout: any = null;
watch(() => filters.query, () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    loadExams();
  }, 300);
});

onMounted(async () => {
  await Promise.all([loadFilterOptions(), loadSummary(), loadExams()]);
});
</script>

<template>
  <div class="exams-management-page">
    <!-- Page Header -->
    <ExamHeader />

    <!-- Alerts -->
    <div v-if="successMessage" class="alert success" role="alert">
      <span>{{ successMessage }}</span>
      <button type="button" class="alert-dismiss" @click="successMessage = ''">&times;</button>
    </div>

    <div v-if="errorMessage" class="alert error" role="alert">
      <span>{{ errorMessage }}</span>
      <button type="button" class="alert-dismiss" @click="errorMessage = ''">&times;</button>
    </div>

    <!-- Exam Statistics from PostgreSQL -->
    <ExamStats :summary="summary" :is-loading="isLoadingSummary" />

    <!-- Filter Toolbar -->
    <ExamToolbar
      :query="filters.query"
      :academic-year="filters.academic_year"
      :status="filters.status"
      :filter-options="filterOptions"
      :active-filter-count="activeFilterCount"
      @update:query="filters.query = $event"
      @update:academic-year="filters.academic_year = $event"
      @update:status="filters.status = $event"
      @open-filter-drawer="isFilterDrawerOpen = true"
      @refresh="loadExams(); loadSummary();"
    />

    <!-- Active Filter Chips -->
    <ExamActiveChips
      :filters="filters"
      :class-lookup="classLookup"
      :subject-lookup="subjectLookup"
      @remove="removeFilter"
      @clear-all="clearAllFilters"
    />

    <!-- Main Content Area -->
    <div class="exam-directory-container">
      <!-- Loading Skeleton -->
      <ExamSkeleton v-if="isLoading" />

      <!-- Empty State -->
      <ExamEmptyState
        v-else-if="exams.length === 0"
        :has-filters="hasAnyFilters"
        @clear-filters="clearAllFilters"
      />

      <!-- Directory Views (Desktop Table + Mobile Cards) -->
      <div v-else class="directory-views">
        <!-- Desktop Table (visible >= 769px) -->
        <div class="desktop-table-view">
          <ExamTable
            :exams="paginatedExams"
            @view="handleViewExam"
            @edit="handleEditExam"
            @enter-marks="handleEnterMarks"
            @review-results="handleReviewResults"
            @publish="openPublishModal"
            @unpublish="openUnpublishModal"
            @delete="openDeleteModal"
          />
        </div>

        <!-- Mobile Card List (visible <= 768px) -->
        <div class="mobile-cards-view">
          <ExamCardList
            :exams="paginatedExams"
            @view="handleViewExam"
            @edit="handleEditExam"
            @enter-marks="handleEnterMarks"
            @review-results="handleReviewResults"
            @publish="openPublishModal"
            @unpublish="openUnpublishModal"
            @delete="openDeleteModal"
          />
        </div>

        <!-- Pagination Controls -->
        <div v-if="totalExams > pageSize" class="pagination-bar">
          <div class="pagination-info">
            Showing {{ (currentPage - 1) * pageSize + 1 }}–{{ Math.min(currentPage * pageSize, totalExams) }} of {{ totalExams }} examinations
          </div>
          <div class="pagination-actions">
            <button
              type="button"
              class="page-btn"
              :disabled="currentPage === 1"
              @click="currentPage--"
            >
              Previous
            </button>
            <span class="page-current">Page {{ currentPage }} of {{ totalPages }}</span>
            <button
              type="button"
              class="page-btn"
              :disabled="currentPage === totalPages"
              @click="currentPage++"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Filter Drawer (Mobile & Tablet) -->
    <ExamFilterDrawer
      :is-open="isFilterDrawerOpen"
      :filters="filters"
      :options="filterOptions"
      @close="isFilterDrawerOpen = false"
      @apply="applyDrawerFilters"
      @reset="clearAllFilters"
    />

    <!-- Confirm Delete Modal -->
    <ExamConfirmDialog
      :is-open="isDeleteModalOpen"
      title="Delete Examination"
      :message="`Are you sure you want to delete '${examToDelete?.name}'? All unrecorded score sheets will be deleted from PostgreSQL. This action cannot be undone.`"
      confirm-text="Delete Examination"
      :is-dangerous="true"
      :is-loading="isDeleting"
      @confirm="handleConfirmDelete"
      @cancel="isDeleteModalOpen = false"
    />

    <!-- Publish Results Modal -->
    <PublishModal
      :is-open="isPublishModalOpen"
      :exam="selectedExamForPublish"
      :is-publishing="isPublishingAction"
      :is-loading="isSubmittingPublish"
      @confirm="handleConfirmPublish"
      @cancel="isPublishModalOpen = false"
    />
  </div>
</template>

<style scoped>
.exams-management-page {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  box-sizing: border-box;
}

.alert {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.alert.success {
  background-color: #ecfdf5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.alert.error {
  background-color: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.alert-dismiss {
  font-size: 1.25rem;
  background: none;
  border: none;
  cursor: pointer;
  color: inherit;
  line-height: 1;
}

.exam-directory-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
}

.directory-views {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
}

.desktop-table-view {
  display: block;
  width: 100%;
}

.mobile-cards-view {
  display: none;
  width: 100%;
}

.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem 1rem;
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  margin-top: 0.5rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.pagination-info {
  font-size: 0.8125rem;
  color: #64748b;
  font-weight: 500;
}

.pagination-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.page-btn {
  padding: 0.4rem 0.875rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #334155;
  background-color: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.page-btn:hover:not(:disabled) {
  background-color: #f1f5f9;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-current {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #0f172a;
}

/* Responsive View Switch */
@media (max-width: 768px) {
  .desktop-table-view {
    display: none;
  }
  .mobile-cards-view {
    display: block;
  }
  .pagination-bar {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
}
</style>
