<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { studentService } from '../../../services/studentService';
import { classService } from '../../../services/classService';
import { Student, SchoolClass, StudentSummary as StudentSummaryType, StudentFilterParams } from '../../../types/school';

import StudentSummary from './components/StudentSummary.vue';
import StudentToolbar from './components/StudentToolbar.vue';
import StudentActiveChips from './components/StudentActiveChips.vue';
import StudentFilterDrawer from './components/StudentFilterDrawer.vue';
import StudentTable from './components/StudentTable.vue';
import StudentCardList from './components/StudentCardList.vue';
import StudentSkeleton from './components/StudentSkeleton.vue';
import StudentEmptyState from './components/StudentEmptyState.vue';
import StudentConfirmDialog from './components/StudentConfirmDialog.vue';
import StudentFormModal from './components/StudentFormModal.vue';
import StudentImportModal from './components/StudentImportModal.vue';
import ChangeClassModal from './components/ChangeClassModal.vue';
import ManagePortalModal from './components/ManagePortalModal.vue';
import { clearFormDraft } from '../../../composables/useFormDraft';

// State
const students = ref<Student[]>([]);
const summary = ref<StudentSummaryType | null>(null);
const availableClasses = ref<SchoolClass[]>([]);
const allActiveClasses = ref<SchoolClass[]>([]);
const totalCount = ref(0);
const page = ref(1);
const pageSize = ref(10);
const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize.value)));

const isLoading = ref(true);
const isSummaryLoading = ref(true);
const isSubmitting = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

// Confirmation Dialog State
const isConfirmDialogOpen = ref(false);
const confirmDialogTitle = ref('');
const confirmDialogMessage = ref('');
const confirmDialogConfirmText = ref('Confirm');
const confirmDialogVariant = ref<'danger' | 'primary' | 'warning'>('danger');
const confirmDialogLoading = ref(false);
let pendingConfirmAction: (() => Promise<void>) | null = null;

// Filters
const availableYears = ref<string[]>(['2026/2027', '2025/2026', '2027/2028']);

const filters = reactive<StudentFilterParams>({
  search: '',
  class_id: undefined,
  academic_year: '2026/2027',
  gender: '',
  status: '',
  has_portal: undefined,
});

const isFilterDrawerOpen = ref(false);

const activeFiltersCount = computed(() => {
  let count = 0;
  if (filters.class_id) count++;
  if (filters.academic_year && filters.academic_year !== '2026/2027') count++;
  if (filters.gender) count++;
  if (filters.status) count++;
  if (filters.has_portal !== undefined) count++;
  return count;
});

const hasActiveFiltersOrSearch = computed(() => {
  return activeFiltersCount.value > 0 || !!filters.search?.trim() || !!filters.class_id;
});

// Modals
const isFormModalOpen = ref(false);
const isEditing = ref(false);
const activeStudent = ref<Student | null>(null);

const isChangeClassModalOpen = ref(false);
const isPortalModalOpen = ref(false);
const isImportModalOpen = ref(false);

// Debounce timer for search input
let searchDebounceTimer: any = null;

async function loadSummary() {
  isSummaryLoading.value = true;
  try {
    const data = await studentService.getSummary(filters.academic_year || undefined);
    summary.value = data;
  } catch (err) {
    console.error('Failed to load student summary metrics', err);
  } finally {
    isSummaryLoading.value = false;
  }
}

async function loadDropdowns() {
  try {
    // 1. Available classes with active students (for filter toolbar)
    const res = await classService.getActiveClassesWithStudents({
      academic_year: filters.academic_year || undefined,
    });
    availableClasses.value = Array.isArray(res) ? res : [];

    // 2. All active classes (for student registration, change class & import)
    // Fetch all active classes regardless of table filters so newly created classes are included
    const allRes = await classService.getClasses({
      status: 'ACTIVE',
      page_size: 200,
    });
    allActiveClasses.value = Array.isArray(allRes) ? allRes : (allRes as any)?.items || [];
  } catch (err) {
    console.error('Failed to load classes dropdown', err);
  }
}

async function loadStudents() {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    const res: any = await studentService.getStudents({
      search: filters.search?.trim() || undefined,
      class_id: filters.class_id || undefined,
      academic_year: filters.academic_year || undefined,
      gender: filters.gender || undefined,
      status: filters.status || undefined,
      has_portal: filters.has_portal,
      page: page.value,
      page_size: pageSize.value,
    });

    if (Array.isArray(res)) {
      students.value = res;
      totalCount.value = res.length;
    } else if (res && Array.isArray(res.items)) {
      students.value = res.items;
      totalCount.value = res.total ?? res.items.length;
    } else {
      students.value = [];
      totalCount.value = 0;
    }
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Unable to load students from database. Please try again.';
  } finally {
    isLoading.value = false;
  }
}

// Watchers
watch(
  () => filters.search,
  () => {
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => {
      page.value = 1;
      loadStudents();
    }, 300);
  }
);

watch(
  () => filters.academic_year,
  async (newYear) => {
    if (filters.class_id) {
      const exists = availableClasses.value.some(c => c.id === filters.class_id && (!newYear || c.academic_year === newYear));
      if (!exists) {
        filters.class_id = undefined;
      }
    }
    await loadDropdowns();
    page.value = 1;
    await Promise.all([loadStudents(), loadSummary()]);
  }
);

watch(
  [() => filters.class_id, () => filters.status, () => filters.gender, () => filters.has_portal],
  () => {
    page.value = 1;
    loadStudents();
  }
);

function applyDrawerFilters(newFilters: StudentFilterParams) {
  filters.class_id = newFilters.class_id;
  filters.academic_year = newFilters.academic_year;
  filters.gender = newFilters.gender;
  filters.status = newFilters.status;
  filters.has_portal = newFilters.has_portal;
  page.value = 1;
  loadStudents();
}

function handleRemoveFilterChip(key: keyof StudentFilterParams) {
  if (key === 'search') filters.search = '';
  else if (key === 'class_id') filters.class_id = undefined;
  else if (key === 'academic_year') filters.academic_year = '';
  else if (key === 'gender') filters.gender = '';
  else if (key === 'status') filters.status = '';
  else if (key === 'has_portal') filters.has_portal = undefined;
  page.value = 1;
  loadStudents();
}

function resetAllFilters() {
  filters.search = '';
  filters.class_id = undefined;
  filters.academic_year = '';
  filters.gender = '';
  filters.status = '';
  filters.has_portal = undefined;
  page.value = 1;
  loadStudents();
}

function changePage(newPage: number) {
  if (newPage >= 1 && newPage <= totalPages.value) {
    page.value = newPage;
    loadStudents();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

// Actions
function openCreateModal() {
  loadDropdowns();
  isEditing.value = false;
  activeStudent.value = null;
  isFormModalOpen.value = true;
}

function openEditModal(student: Student) {
  isEditing.value = true;
  activeStudent.value = student;
  isFormModalOpen.value = true;
}

function openChangeClassModal(student: Student) {
  activeStudent.value = student;
  isChangeClassModalOpen.value = true;
}

function openPortalModal(student: Student) {
  activeStudent.value = student;
  isPortalModalOpen.value = true;
}

async function handleSaveStudent(payload: any) {
  isSubmitting.value = true;
  errorMessage.value = '';
  try {
    if (isEditing.value && activeStudent.value) {
      await studentService.updateStudent(activeStudent.value.id, payload);
      successMessage.value = `Student ${payload.first_name} ${payload.last_name} updated successfully.`;
    } else {
      await studentService.createStudent(payload);
      clearFormDraft('sms_draft_student_create');
      successMessage.value = `Student ${payload.first_name} ${payload.last_name} admitted successfully.`;
    }
    isFormModalOpen.value = false;
    await Promise.all([loadStudents(), loadSummary()]);
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to save student record.';
  } finally {
    isSubmitting.value = false;
  }
}

function handleClassChangeSuccess(result: any) {
  successMessage.value = result?.message || 'Student class change applied successfully.';
  isChangeClassModalOpen.value = false;
  loadStudents();
  loadSummary();
  setTimeout(() => { successMessage.value = ''; }, 4000);
}

async function handleImportComplete(classId: number, academicYear: string) {
  filters.class_id = classId;
  filters.academic_year = academicYear;
  page.value = 1;
  successMessage.value = 'Students imported successfully. Displaying updated class roster.';
  await Promise.all([loadStudents(), loadSummary(), loadDropdowns()]);
  setTimeout(() => { successMessage.value = ''; }, 6000);
}


function handleToggleStatus(student: Student) {
  const isCurrentlyActive = student.status === 'ACTIVE';
  const targetStatus = isCurrentlyActive ? 'INACTIVE' : 'ACTIVE';
  const actionName = isCurrentlyActive ? 'deactivate' : 'activate';

  confirmDialogTitle.value = `${isCurrentlyActive ? 'Deactivate' : 'Activate'} Student?`;
  confirmDialogMessage.value = isCurrentlyActive
    ? `Are you sure you want to deactivate ${student.full_name || student.first_name} (${student.admission_number})? The student will lose portal access and active school services.`
    : `Are you sure you want to activate ${student.full_name || student.first_name} (${student.admission_number})? The student will regain active school status.`;
  confirmDialogConfirmText.value = isCurrentlyActive ? 'Deactivate Student' : 'Activate Student';
  confirmDialogVariant.value = isCurrentlyActive ? 'danger' : 'primary';

  pendingConfirmAction = async () => {
    confirmDialogLoading.value = true;
    try {
      await studentService.updateStatus(student.id, targetStatus, `Admin ${actionName}d student`);
      successMessage.value = `Student status changed to ${targetStatus}.`;
      isConfirmDialogOpen.value = false;
      await Promise.all([loadStudents(), loadSummary()]);
    } catch (err: any) {
      errorMessage.value = err.response?.data?.detail || 'Failed to update student status.';
      isConfirmDialogOpen.value = false;
    } finally {
      confirmDialogLoading.value = false;
    }
  };

  isConfirmDialogOpen.value = true;
}

async function onConfirmDialogAction() {
  if (pendingConfirmAction) {
    await pendingConfirmAction();
  }
}

onMounted(() => {
  loadSummary();
  loadDropdowns();
  loadStudents();
});
</script>

<template>
  <div class="students-module-page">
    <!-- Page Header Row -->
    <div class="page-header-row">
      <div class="page-title-block">
        <div class="page-title-with-badge">
          <h1 class="page-title">Students</h1>
          <span class="page-count-badge">{{ totalCount }} Students</span>
        </div>
        <p class="page-subtitle">Manage student profiles, admissions, enrollment and portal access.</p>
      </div>
      <div class="page-header-actions">
        <button
          type="button"
          class="btn-secondary-header"
          aria-label="Import Students from Excel"
          @click="isImportModalOpen = true"
        >
          <svg class="btn-hdr-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <span>Import Students</span>
        </button>
        <button
          type="button"
          class="btn-primary-header"
          aria-label="Register New Student"
          @click="openCreateModal"
        >
          <svg class="btn-hdr-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span>Register Student</span>
        </button>
      </div>
    </div>

    <!-- Alert Notifications -->
    <div v-if="successMessage" class="alert-box success" role="alert">
      <div class="alert-content">
        <svg class="w-5 h-5 text-emerald-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <span>{{ successMessage }}</span>
      </div>
      <button class="alert-close" aria-label="Dismiss alert" @click="successMessage = ''">&times;</button>
    </div>

    <div v-if="errorMessage" class="alert-box error" role="alert">
      <div class="alert-content">
        <svg class="w-5 h-5 text-rose-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <span>{{ errorMessage }}</span>
      </div>
      <button class="btn-retry" @click="loadStudents">Retry</button>
    </div>

    <!-- Summary Overview Cards -->
    <StudentSummary
      :summary="summary"
      :is-loading="isSummaryLoading"
    />

    <!-- Search & Filters Toolbar -->
    <StudentToolbar
      :search="filters.search || ''"
      :class-id="filters.class_id || ''"
      :academic-year="filters.academic_year || ''"
      :available-years="availableYears"
      :status="filters.status || ''"
      :active-filters-count="activeFiltersCount"
      :available-classes="availableClasses"
      :is-loading="isLoading"
      @update:search="filters.search = $event"
      @update:class-id="filters.class_id = $event ? Number($event) : undefined"
      @update:academic-year="filters.academic_year = $event"
      @update:status="filters.status = $event"
      @open-drawer="isFilterDrawerOpen = true"
      @reset-filters="resetAllFilters"
    />

    <!-- Active Filter Chips Bar -->
    <StudentActiveChips
      :filters="filters"
      :available-classes="availableClasses"
      @remove="handleRemoveFilterChip"
      @clear-all="resetAllFilters"
    />

    <!-- Main Content Container -->
    <div class="table-content-card">
      <!-- Loading Skeleton State -->
      <StudentSkeleton v-if="isLoading" :rows="6" />

      <!-- Empty State -->
      <StudentEmptyState
        v-else-if="students.length === 0"
        :has-filters="hasActiveFiltersOrSearch"
        @clear-filters="resetAllFilters"
        @register="openCreateModal"
      />

      <!-- Real Student List -->
      <div v-else class="list-wrapper">
        <!-- Desktop / Tablet Table View (>=768px) -->
        <div class="hide-mobile">
          <StudentTable
            :students="students"
            @edit="openEditModal"
            @change-class="openChangeClassModal"
            @manage-portal="openPortalModal"
            @toggle-status="handleToggleStatus"
          />
        </div>

        <!-- Mobile Card List View (<768px) -->
        <div class="hide-desktop">
          <StudentCardList
            :students="students"
            @edit="openEditModal"
            @change-class="openChangeClassModal"
            @manage-portal="openPortalModal"
            @toggle-status="handleToggleStatus"
          />
        </div>

        <!-- Pagination Controls -->
        <div class="pagination-bar">
          <div class="pagination-info">
            Showing <strong>{{ totalCount > 0 ? (page - 1) * pageSize + 1 : 0 }}</strong> to <strong>{{ Math.min(page * pageSize, totalCount) }}</strong> of <strong>{{ totalCount }}</strong> students
          </div>

          <div class="pagination-nav">
            <button
              type="button"
              class="btn-page-nav"
              :disabled="page <= 1"
              aria-label="Previous page"
              @click="changePage(page - 1)"
            >
              &larr; Previous
            </button>

            <span class="page-indicator">
              Page {{ page }} of {{ totalPages }}
            </span>

            <button
              type="button"
              class="btn-page-nav"
              :disabled="page >= totalPages"
              aria-label="Next page"
              @click="changePage(page + 1)"
            >
              Next &rarr;
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Filter Drawer (Mobile & Advanced) -->
    <StudentFilterDrawer
      :is-open="isFilterDrawerOpen"
      :filters="filters"
      :available-classes="availableClasses"
      :available-years="availableYears"
      @close="isFilterDrawerOpen = false"
      @apply="applyDrawerFilters"
      @reset="resetAllFilters"
    />

    <!-- Student Form Modal (Register & Edit) -->
    <StudentFormModal
      :is-open="isFormModalOpen"
      :is-editing="isEditing"
      :student="activeStudent"
      :available-classes="allActiveClasses.length > 0 ? allActiveClasses : availableClasses"
      :is-submitting="isSubmitting"
      @close="isFormModalOpen = false"
      @save="handleSaveStudent"
    />

    <!-- Change Class Modal -->
    <ChangeClassModal
      :is-open="isChangeClassModalOpen"
      :student="activeStudent"
      :available-classes="allActiveClasses.length > 0 ? allActiveClasses : availableClasses"
      @close="isChangeClassModalOpen = false"
      @success="handleClassChangeSuccess"
    />

    <!-- Manage Portal Modal -->
    <ManagePortalModal
      :is-open="isPortalModalOpen"
      :student="activeStudent"
      :is-submitting="isSubmitting"
      @close="isPortalModalOpen = false"
      @updated="loadStudents"
    />

    <!-- Student Import Modal (Excel Bulk) -->
    <StudentImportModal
      :is-open="isImportModalOpen"
      :available-classes="allActiveClasses.length > 0 ? allActiveClasses : availableClasses"
      :available-years="availableYears"
      :initial-academic-year="filters.academic_year || '2026/2027'"
      @close="isImportModalOpen = false"
      @import-complete="handleImportComplete"
    />

    <!-- Confirmation Dialog -->
    <StudentConfirmDialog
      :is-open="isConfirmDialogOpen"
      :title="confirmDialogTitle"
      :message="confirmDialogMessage"
      :confirm-text="confirmDialogConfirmText"
      :variant="confirmDialogVariant"
      :is-loading="confirmDialogLoading"
      @confirm="onConfirmDialogAction"
      @cancel="isConfirmDialogOpen = false"
    />
  </div>
</template>

<style scoped>
.students-module-page {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
  box-sizing: border-box;
}

.page-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.125rem;
  flex-wrap: wrap;
  width: 100%;
  box-sizing: border-box;
}

.page-title-block {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1 1 auto;
}

.page-title-with-badge {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.page-title {
  font-size: 1.65rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
  letter-spacing: -0.025em;
  line-height: 1.2;
}

.page-count-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.22rem 0.75rem;
  background: linear-gradient(135deg, #EEF5FE 0%, #E0EEFF 100%);
  color: #1D4ED8;
  border: 1.5px solid #BFDBFE;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  box-shadow: 0 1px 3px rgba(37, 99, 235, 0.08);
}

.page-subtitle {
  font-size: 0.86rem;
  color: #64748b;
  margin: 0.35rem 0 0;
  line-height: 1.4;
  word-break: break-word;
}

.page-header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn-secondary-header {
  height: 44px;
  padding: 0 1.25rem;
  background: #ffffff;
  color: #1e293b;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  font-size: 0.86rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
  box-sizing: border-box;
  flex-shrink: 0;
}

.btn-secondary-header:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  color: #0f172a;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
}

.btn-primary-header {
  height: 44px;
  padding: 0 1.35rem;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  color: #ffffff;
  border: none;
  border-radius: 12px;
  font-size: 0.86rem;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(37, 99, 235, 0.35);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
  box-sizing: border-box;
  flex-shrink: 0;
}

.btn-primary-header:hover {
  background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
  box-shadow: 0 6px 22px rgba(37, 99, 235, 0.45);
  transform: translateY(-1px);
}

.btn-hdr-icon {
  width: 1.15rem;
  height: 1.15rem;
}

.table-content-card {
  background: #ffffff;
  border-radius: 20px;
  border: 1.5px solid #e2e8f0;
  box-shadow: 0 10px 30px -5px rgba(15, 23, 42, 0.05), 0 2px 6px -1px rgba(15, 23, 42, 0.02);
  overflow: hidden;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.list-wrapper {
  width: 100%;
  box-sizing: border-box;
}

.pagination-bar {
  padding: 1rem 1.5rem;
  border-top: 1.5px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  background: #f8fafc;
  width: 100%;
  box-sizing: border-box;
}

.pagination-info {
  font-size: 0.84rem;
  color: #64748b;
}

.pagination-info strong {
  color: #0f172a;
  font-weight: 700;
}

.pagination-nav {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.btn-page-nav {
  height: 36px;
  padding: 0 1rem;
  background: #ffffff;
  border: 1.5px solid #cbd5e1;
  border-radius: 10px;
  font-size: 0.81rem;
  font-weight: 600;
  color: #334155;
  cursor: pointer;
  transition: all 0.15s ease;
  box-sizing: border-box;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.btn-page-nav:hover:not(:disabled) {
  background: #f1f5f9;
  border-color: #94a3b8;
  color: #0f172a;
  transform: translateY(-1px);
}

.btn-page-nav:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-indicator {
  font-size: 0.81rem;
  font-weight: 700;
  color: #1e293b;
  padding: 0 0.4rem;
  white-space: nowrap;
}

.alert-box {
  padding: 0.75rem 1rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.8125rem;
  font-weight: 500;
  margin-bottom: 0.875rem;
  width: 100%;
  box-sizing: border-box;
}

.alert-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
  flex: 1;
}

.alert-box.success { background: #ecfdf5; border: 1px solid #a7f3d0; color: #065f46; }
.alert-box.error { background: #fff1f2; border: 1px solid #fecdd3; color: #9f1239; }

.alert-close {
  width: 32px;
  height: 32px;
  background: none;
  border: none;
  font-size: 1.25rem;
  color: currentColor;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  flex-shrink: 0;
}

.alert-close:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.btn-retry {
  background: #ffffff;
  border: 1px solid #fecdd3;
  color: #9f1239;
  padding: 0.25rem 0.65rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  flex-shrink: 0;
}

@media (max-width: 767px) {
  .hide-mobile { display: none !important; }
}

@media (min-width: 768px) {
  .hide-desktop { display: none !important; }
}

@media (max-width: 540px) {
  .page-header-row {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }

  .page-header-actions {
    display: flex;
    flex-direction: column;
    width: 100%;
  }

  .btn-secondary-header,
  .btn-primary-header {
    width: 100%;
    justify-content: center;
  }

  .page-title {
    font-size: 1.25rem;
  }

  .pagination-bar {
    flex-direction: column;
    align-items: center;
    gap: 0.625rem;
    text-align: center;
  }

  .pagination-nav {
    width: 100%;
    justify-content: space-between;
  }

  .btn-page-nav {
    flex: 1;
  }
}
</style>
