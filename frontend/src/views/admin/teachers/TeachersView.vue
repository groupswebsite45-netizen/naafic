<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { teacherService, CreateTeacherPayload, AssignTeacherPayload } from '../../../services/teacherService';
import { classService } from '../../../services/classService';
import { subjectService } from '../../../services/subjectService';
import { Teacher, SchoolClass, Subject, TeacherSummary as TeacherSummaryType, TeacherFilterParams } from '../../../types/school';

import TeacherSummary from './components/TeacherSummary.vue';
import TeacherToolbar from './components/TeacherToolbar.vue';
import TeacherActiveChips from './components/TeacherActiveChips.vue';
import TeacherFilterDrawer from './components/TeacherFilterDrawer.vue';
import TeacherTable from './components/TeacherTable.vue';
import TeacherCardList from './components/TeacherCardList.vue';
import TeacherSkeleton from './components/TeacherSkeleton.vue';
import TeacherEmptyState from './components/TeacherEmptyState.vue';
import TeacherConfirmDialog from './components/TeacherConfirmDialog.vue';
import TeacherFormModal from './components/TeacherFormModal.vue';
import TeacherAssignmentModal from './components/TeacherAssignmentModal.vue';
import TeacherPortalModal from './components/TeacherPortalModal.vue';
import { clearFormDraft } from '../../../composables/useFormDraft';

// State
const teachers = ref<Teacher[]>([]);
const summary = ref<TeacherSummaryType | null>(null);
const availableClasses = ref<SchoolClass[]>([]);
const availableSubjects = ref<Subject[]>([]);
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
const filters = reactive<TeacherFilterParams>({
  search: '',
  class_id: undefined,
  subject_id: undefined,
  status: '',
  has_portal: undefined,
  academic_year: '',
});

const isFilterDrawerOpen = ref(false);

const activeFiltersCount = computed(() => {
  let count = 0;
  if (filters.class_id) count++;
  if (filters.subject_id) count++;
  if (filters.status) count++;
  if (filters.has_portal !== undefined) count++;
  if (filters.academic_year) count++;
  return count;
});

const hasActiveFiltersOrSearch = computed(() => {
  return activeFiltersCount.value > 0 || !!filters.search?.trim();
});

// Modals
const isFormModalOpen = ref(false);
const isEditing = ref(false);
const activeTeacher = ref<Teacher | null>(null);

const isAssignModalOpen = ref(false);
const assignmentError = ref('');
const isPortalModalOpen = ref(false);

// Debounce timer for search input
let searchDebounceTimer: any = null;

async function loadSummary() {
  isSummaryLoading.value = true;
  try {
    const data = await teacherService.getSummary();
    summary.value = data;
  } catch (err) {
    console.error('Failed to load teacher summary metrics', err);
  } finally {
    isSummaryLoading.value = false;
  }
}

async function loadDropdowns() {
  try {
    const [cRes, sRes]: any = await Promise.all([
      classService.getClasses({ page_size: 100 }),
      subjectService.getSubjects({ page_size: 100 }),
    ]);
    availableClasses.value = Array.isArray(cRes) ? cRes : cRes?.items || [];
    availableSubjects.value = Array.isArray(sRes) ? sRes : sRes?.items || [];
  } catch (err) {
    console.error('Failed to load classes or subjects dropdown', err);
  }
}

async function loadTeachers() {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    const res: any = await teacherService.getTeachers({
      search: filters.search?.trim() || undefined,
      class_id: filters.class_id || undefined,
      subject_id: filters.subject_id || undefined,
      status: filters.status || undefined,
      has_portal: filters.has_portal,
      academic_year: filters.academic_year || undefined,
      page: page.value,
      page_size: pageSize.value,
    });

    if (Array.isArray(res)) {
      teachers.value = res;
      totalCount.value = res.length;
    } else if (res && Array.isArray(res.items)) {
      teachers.value = res.items;
      totalCount.value = res.total ?? res.items.length;
    } else {
      teachers.value = [];
      totalCount.value = 0;
    }
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Unable to load teachers from database. Please try again.';
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
      loadTeachers();
    }, 300);
  }
);

watch(
  [() => filters.class_id, () => filters.subject_id, () => filters.status],
  () => {
    page.value = 1;
    loadTeachers();
  }
);

function applyDrawerFilters(newFilters: TeacherFilterParams) {
  filters.class_id = newFilters.class_id;
  filters.subject_id = newFilters.subject_id;
  filters.status = newFilters.status;
  filters.has_portal = newFilters.has_portal;
  filters.academic_year = newFilters.academic_year;
  page.value = 1;
  loadTeachers();
}

function handleRemoveFilterChip(key: keyof TeacherFilterParams) {
  if (key === 'search') filters.search = '';
  else if (key === 'class_id') filters.class_id = undefined;
  else if (key === 'subject_id') filters.subject_id = undefined;
  else if (key === 'status') filters.status = '';
  else if (key === 'has_portal') filters.has_portal = undefined;
  else if (key === 'academic_year') filters.academic_year = '';
  page.value = 1;
  loadTeachers();
}

function resetAllFilters() {
  filters.search = '';
  filters.class_id = undefined;
  filters.subject_id = undefined;
  filters.status = '';
  filters.has_portal = undefined;
  filters.academic_year = '';
  page.value = 1;
  loadTeachers();
}

function changePage(newPage: number) {
  if (newPage >= 1 && newPage <= totalPages.value) {
    page.value = newPage;
    loadTeachers();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

// Actions
function openCreateModal() {
  isEditing.value = false;
  activeTeacher.value = null;
  isFormModalOpen.value = true;
}

function openEditModal(teacher: Teacher) {
  isEditing.value = true;
  activeTeacher.value = teacher;
  isFormModalOpen.value = true;
}

function openAssignModal(teacher: Teacher) {
  activeTeacher.value = teacher;
  assignmentError.value = '';
  isAssignModalOpen.value = true;
}

function openPortalModal(teacher: Teacher) {
  activeTeacher.value = teacher;
  isPortalModalOpen.value = true;
}

async function handleSaveTeacher(payload: CreateTeacherPayload) {
  isSubmitting.value = true;
  errorMessage.value = '';
  try {
    if (isEditing.value && activeTeacher.value) {
      await teacherService.updateTeacher(activeTeacher.value.id, payload);
      successMessage.value = `Teacher ${payload.first_name} ${payload.last_name} updated successfully.`;
    } else {
      await teacherService.createTeacher(payload);
      clearFormDraft('sms_draft_teacher_create');
      successMessage.value = `Teacher ${payload.first_name} ${payload.last_name} registered successfully.`;
    }
    isFormModalOpen.value = false;
    await Promise.all([loadTeachers(), loadSummary()]);
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to save teacher record.';
  } finally {
    isSubmitting.value = false;
  }
}

async function handleSaveAssignment(payload: AssignTeacherPayload) {
  if (!activeTeacher.value) return;
  isSubmitting.value = true;
  assignmentError.value = '';
  try {
    await teacherService.assignTeacher(activeTeacher.value.id, payload);
    successMessage.value = 'Teaching allocation added successfully.';
    // Refresh active teacher assignments inside modal without closing it
    const updated = await teacherService.getTeacherById(activeTeacher.value.id);
    activeTeacher.value = updated;
    await Promise.all([loadTeachers(), loadSummary()]);
  } catch (err: any) {
    const errorDetail = err.response?.data?.detail || 'Failed to allocate teacher to class.';
    assignmentError.value = errorDetail;
  } finally {
    isSubmitting.value = false;
  }
}

async function handleRemoveAssignment(assignmentId: number) {
  if (!activeTeacher.value) return;
  try {
    await teacherService.removeAssignment(assignmentId);
    successMessage.value = 'Teaching assignment removed.';
    // Refresh active teacher
    const updated = await teacherService.getTeacherById(activeTeacher.value.id);
    activeTeacher.value = updated;
    await Promise.all([loadTeachers(), loadSummary()]);
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Failed to remove assignment.');
  }
}

async function handleCreatePortal(payload: any) {
  if (!activeTeacher.value) return;
  isSubmitting.value = true;
  try {
    await teacherService.createPortalAccount(activeTeacher.value.id, payload);
    successMessage.value = 'Teacher portal account activated successfully.';
    isPortalModalOpen.value = false;
    await loadTeachers();
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Failed to provision portal account.');
  } finally {
    isSubmitting.value = false;
  }
}

function handleToggleStatus(teacher: Teacher) {
  const isCurrentlyActive = teacher.status === 'ACTIVE';
  const targetStatus = isCurrentlyActive ? 'INACTIVE' : 'ACTIVE';
  const actionName = isCurrentlyActive ? 'deactivate' : 'activate';

  confirmDialogTitle.value = `${isCurrentlyActive ? 'Deactivate' : 'Activate'} Faculty Member?`;
  confirmDialogMessage.value = isCurrentlyActive
    ? `Are you sure you want to deactivate ${teacher.full_name || teacher.first_name} (${teacher.teacher_number || teacher.employee_id})? The teacher will lose portal access and active assignment permissions.`
    : `Are you sure you want to activate ${teacher.full_name || teacher.first_name} (${teacher.teacher_number || teacher.employee_id})? The teacher will regain active portal and teaching status.`;
  confirmDialogConfirmText.value = isCurrentlyActive ? 'Deactivate Teacher' : 'Activate Teacher';
  confirmDialogVariant.value = isCurrentlyActive ? 'danger' : 'primary';

  pendingConfirmAction = async () => {
    confirmDialogLoading.value = true;
    try {
      await teacherService.updateStatus(teacher.id, targetStatus, `Admin ${actionName}d teacher`);
      successMessage.value = `Teacher status changed to ${targetStatus}.`;
      isConfirmDialogOpen.value = false;
      await Promise.all([loadTeachers(), loadSummary()]);
    } catch (err: any) {
      errorMessage.value = err.response?.data?.detail || 'Failed to update teacher status.';
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
  loadTeachers();
});
</script>

<template>
  <div class="teachers-module-page">
    <!-- Page Header -->
    <div class="page-header-row">
      <div class="page-title-block">
        <div class="page-title-with-badge">
          <h1 class="page-title">Teachers</h1>
          <span class="page-count-badge">{{ totalCount }} Faculty</span>
        </div>
        <p class="page-subtitle">Manage faculty profiles, class assignments, subjects and portal access.</p>
      </div>
      <button class="btn-primary-header" @click="openCreateModal">
        <svg class="btn-hdr-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        <span>Register Teacher</span>
      </button>
    </div>

    <!-- Alert Notifications -->
    <div v-if="successMessage" class="alert-box success">
      <div class="alert-content">
        <svg class="w-5 h-5 text-emerald-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <span>{{ successMessage }}</span>
      </div>
      <button class="alert-close" @click="successMessage = ''">&times;</button>
    </div>
    <div v-if="errorMessage" class="alert-box error">
      <div class="alert-content">
        <svg class="w-5 h-5 text-rose-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <span>{{ errorMessage }}</span>
      </div>
      <button class="btn-retry" @click="loadTeachers">Retry</button>
    </div>

    <!-- Summary Overview Cards -->
    <TeacherSummary
      :summary="summary"
      :is-loading="isSummaryLoading"
    />

    <!-- Search & Filters Toolbar -->
    <TeacherToolbar
      :search="filters.search || ''"
      :class-id="filters.class_id || ''"
      :subject-id="filters.subject_id || ''"
      :status="filters.status || ''"
      :active-filters-count="activeFiltersCount"
      :available-classes="availableClasses"
      :available-subjects="availableSubjects"
      :is-loading="isLoading"
      @update:search="filters.search = $event"
      @update:class-id="filters.class_id = $event ? Number($event) : undefined"
      @update:subject-id="filters.subject_id = $event ? Number($event) : undefined"
      @update:status="filters.status = $event"
      @open-drawer="isFilterDrawerOpen = true"
      @reset-filters="resetAllFilters"
    />

    <!-- Active Filter Chips Bar -->
    <TeacherActiveChips
      :filters="filters"
      :available-classes="availableClasses"
      :available-subjects="availableSubjects"
      @remove="handleRemoveFilterChip"
      @clear-all="resetAllFilters"
    />

    <!-- Main Content Container -->
    <div class="table-content-card">
      <!-- Loading Skeleton State -->
      <TeacherSkeleton v-if="isLoading" :rows="6" />

      <!-- Empty State -->
      <TeacherEmptyState
        v-else-if="teachers.length === 0"
        :has-filters="hasActiveFiltersOrSearch"
        @clear-filters="resetAllFilters"
        @register="openCreateModal"
      />

      <!-- Real Teacher List -->
      <div v-else class="list-wrapper">
        <!-- Desktop & Tablet Table View (>=768px) -->
        <div class="hide-mobile">
          <TeacherTable
            :teachers="teachers"
            @edit="openEditModal"
            @assign="openAssignModal"
            @manage-portal="openPortalModal"
            @toggle-status="handleToggleStatus"
          />
        </div>

        <!-- Mobile Card List View (<768px) -->
        <div class="hide-desktop">
          <TeacherCardList
            :teachers="teachers"
            @edit="openEditModal"
            @assign="openAssignModal"
            @manage-portal="openPortalModal"
            @toggle-status="handleToggleStatus"
          />
        </div>

        <!-- Pagination Controls -->
        <div class="pagination-bar">
          <div class="pagination-info">
            Showing <strong>{{ totalCount > 0 ? (page - 1) * pageSize + 1 : 0 }}</strong> to <strong>{{ Math.min(page * pageSize, totalCount) }}</strong> of <strong>{{ totalCount }}</strong> faculty members
          </div>

          <div class="pagination-nav">
            <button
              class="btn-page-nav"
              :disabled="page <= 1"
              @click="changePage(page - 1)"
            >
              Previous
            </button>

            <span class="page-indicator">
              Page {{ page }} of {{ totalPages }}
            </span>

            <button
              class="btn-page-nav"
              :disabled="page >= totalPages"
              @click="changePage(page + 1)"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Filter Drawer (Mobile & Advanced) -->
    <TeacherFilterDrawer
      :is-open="isFilterDrawerOpen"
      :filters="filters"
      :available-classes="availableClasses"
      :available-subjects="availableSubjects"
      @close="isFilterDrawerOpen = false"
      @apply="applyDrawerFilters"
      @reset="resetAllFilters"
    />

    <!-- Teacher Form Modal (Register & Edit) -->
    <TeacherFormModal
      :is-open="isFormModalOpen"
      :is-editing="isEditing"
      :teacher="activeTeacher"
      :is-submitting="isSubmitting"
      @close="isFormModalOpen = false"
      @save="handleSaveTeacher"
    />

    <!-- Assignment Modal -->
    <TeacherAssignmentModal
      :is-open="isAssignModalOpen"
      :teacher="activeTeacher"
      :available-classes="availableClasses"
      :available-subjects="availableSubjects"
      :is-submitting="isSubmitting"
      :error-message="assignmentError"
      @close="isAssignModalOpen = false"
      @assign="handleSaveAssignment"
      @remove-assignment="handleRemoveAssignment"
    />

    <!-- Manage Portal Modal -->
    <TeacherPortalModal
      :is-open="isPortalModalOpen"
      :teacher="activeTeacher"
      :is-submitting="isSubmitting"
      @close="isPortalModalOpen = false"
      @create-account="handleCreatePortal"
    />

    <!-- Confirmation Dialog -->
    <TeacherConfirmDialog
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
.teachers-module-page {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.page-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.875rem;
  margin-bottom: 0.875rem;
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
  padding: 0.65rem 0.875rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.8125rem;
  font-weight: 500;
  margin-bottom: 0.75rem;
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
  background: none;
  border: none;
  font-size: 1.25rem;
  color: currentColor;
  cursor: pointer;
  flex-shrink: 0;
}

.btn-retry {
  background: #ffffff;
  border: 1px solid #fecdd3;
  color: #9f1239;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  font-size: 0.72rem;
  font-weight: 600;
  cursor: pointer;
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .hide-mobile { display: none !important; }
}

@media (min-width: 769px) {
  .hide-desktop { display: none !important; }
}

@media (max-width: 540px) {
  .page-header-row {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }

  .btn-primary-header {
    width: 100%;
  }

  .page-title {
    font-size: 1.2rem;
  }

  .pagination-bar {
    flex-direction: column;
    align-items: center;
    gap: 0.45rem;
    text-align: center;
  }
}
</style>
