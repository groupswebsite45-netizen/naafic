<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { Subject, SubjectSummary as ISubjectSummary } from '../../../types/school';
import { subjectService } from '../../../services/subjectService';

import SubjectSummary from './components/SubjectSummary.vue';
import SubjectToolbar from './components/SubjectToolbar.vue';
import SubjectActiveChips from './components/SubjectActiveChips.vue';
import SubjectFilterDrawer from './components/SubjectFilterDrawer.vue';
import SubjectTable from './components/SubjectTable.vue';
import SubjectCardList from './components/SubjectCardList.vue';
import SubjectFormModal from './components/SubjectFormModal.vue';
import SubjectAssignClassModal from './components/SubjectAssignClassModal.vue';
import SubjectAssignTeacherModal from './components/SubjectAssignTeacherModal.vue';
import SubjectConfirmDialog from './components/SubjectConfirmDialog.vue';
import SubjectSkeleton from './components/SubjectSkeleton.vue';
import SubjectEmptyState from './components/SubjectEmptyState.vue';
import { clearFormDraft } from '../../../composables/useFormDraft';

// State
const subjects = ref<Subject[]>([]);
const summary = ref<ISubjectSummary | null>(null);
const departments = ref<string[]>([]);
const isLoading = ref(true);
const isSummaryLoading = ref(true);
const totalCount = ref(0);

// Messages
const successMessage = ref('');
const errorMessage = ref('');

// Filters & Pagination
const filters = reactive({
  query: '',
  department: '',
  status: '',
  section: '',
  assignment_state: '',
  page: 1,
  pageSize: 15,
});

// Modals
const isFormModalOpen = ref(false);
const isEditing = ref(false);
const selectedSubject = ref<Subject | null>(null);
const isSubmittingForm = ref(false);

const isAssignClassModalOpen = ref(false);
const isSubmittingAssignClass = ref(false);

const isAssignTeacherModalOpen = ref(false);
const isSubmittingAssignTeacher = ref(false);

const isFilterDrawerOpen = ref(false);

const isConfirmDialogOpen = ref(false);
const confirmDialogConfig = reactive({
  title: '',
  message: '',
  confirmLabel: 'Confirm',
  variant: 'primary' as 'danger' | 'primary' | 'warning',
  action: () => {},
});
const isSubmittingConfirm = ref(false);

// Active filter count
const activeFilterCount = computed(() => {
  let count = 0;
  if (filters.department) count++;
  if (filters.status) count++;
  if (filters.section) count++;
  if (filters.assignment_state) count++;
  return count;
});

// Total pages
const totalPages = computed(() => {
  return Math.ceil(totalCount.value / filters.pageSize) || 1;
});

// Load Summary
async function loadSummary() {
  isSummaryLoading.value = true;
  try {
    const data = await subjectService.getSummary();
    summary.value = data;
  } catch (err: any) {
    console.error('Failed to load subject statistics:', err);
  } finally {
    isSummaryLoading.value = false;
  }
}

// Load Departments list
async function loadDepartments() {
  try {
    departments.value = await subjectService.getDepartments();
  } catch (err) {
    console.error('Failed to load departments:', err);
  }
}

// Load Subjects
let searchDebounceTimeout: any = null;
async function loadSubjects() {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    const data = await subjectService.getSubjects({
      query: filters.query || undefined,
      department: filters.department || undefined,
      status: filters.status || undefined,
      section: filters.section || undefined,
      assignment_state: filters.assignment_state || undefined,
      page: filters.page,
      page_size: filters.pageSize,
    });
    subjects.value = data;
    // Update count approximation
    if (summary.value && !filters.query && !filters.department && !filters.status && !filters.assignment_state) {
      totalCount.value = summary.value.total_subjects;
    } else {
      totalCount.value = data.length >= filters.pageSize ? filters.page * filters.pageSize + 1 : (filters.page - 1) * filters.pageSize + data.length;
    }
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to load subjects from database.';
  } finally {
    isLoading.value = false;
  }
}

// Debounced search watcher
watch(
  () => filters.query,
  () => {
    clearTimeout(searchDebounceTimeout);
    searchDebounceTimeout = setTimeout(() => {
      filters.page = 1;
      loadSubjects();
    }, 280);
  }
);

// Filter watchers
watch(
  [() => filters.department, () => filters.status, () => filters.section, () => filters.assignment_state],
  () => {
    filters.page = 1;
    loadSubjects();
  }
);

onMounted(() => {
  loadSummary();
  loadDepartments();
  loadSubjects();
});

// Modals Triggers
function openCreateModal() {
  selectedSubject.value = null;
  isEditing.value = false;
  isFormModalOpen.value = true;
}

function openEditModal(sub: Subject) {
  selectedSubject.value = sub;
  isEditing.value = true;
  isFormModalOpen.value = true;
}

async function handleSaveSubject(payload: Partial<Subject>) {
  isSubmittingForm.value = true;
  try {
    if (isEditing.value && selectedSubject.value) {
      await subjectService.updateSubject(selectedSubject.value.id, payload);
      showSuccess(`Subject "${payload.name}" updated successfully.`);
    } else {
      await subjectService.createSubject(payload);
      clearFormDraft('sms_draft_subject_create');
      showSuccess(`Subject "${payload.name}" created successfully.`);
    }
    isFormModalOpen.value = false;
    loadSubjects();
    loadSummary();
    loadDepartments();
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to save subject.';
  } finally {
    isSubmittingForm.value = false;
  }
}

// Class Assignment Modal
function openAssignClassModal(sub: Subject) {
  selectedSubject.value = sub;
  isAssignClassModalOpen.value = true;
}

async function handleAssignClass(payload: {
  class_id: number;
  teacher_id?: number | null;
  academic_year: string;
  periods_per_week?: number | null;
}) {
  if (!selectedSubject.value) return;
  isSubmittingAssignClass.value = true;
  try {
    await subjectService.assignClass(selectedSubject.value.id, payload);
    showSuccess(`Subject assigned to class successfully.`);
    isAssignClassModalOpen.value = false;
    loadSubjects();
    loadSummary();
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to assign subject to class.';
  } finally {
    isSubmittingAssignClass.value = false;
  }
}

// Teacher Assignment Modal
function openAssignTeacherModal(sub: Subject) {
  selectedSubject.value = sub;
  isAssignTeacherModalOpen.value = true;
}

async function handleAssignTeacher(payload: {
  teacher_id: number;
  class_id: number;
  academic_year: string;
  section?: string | null;
}) {
  if (!selectedSubject.value) return;
  isSubmittingAssignTeacher.value = true;
  try {
    await subjectService.assignTeacher(selectedSubject.value.id, payload);
    showSuccess(`Teacher allocated to subject successfully.`);
    isAssignTeacherModalOpen.value = false;
    loadSubjects();
    loadSummary();
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to allocate teacher to subject.';
  } finally {
    isSubmittingAssignTeacher.value = false;
  }
}

// Status Toggle
function handleToggleStatus(sub: Subject) {
  const nextStatus = sub.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE';
  confirmDialogConfig.title = `${nextStatus === 'ACTIVE' ? 'Activate' : 'Deactivate'} Subject`;
  confirmDialogConfig.message = `Are you sure you want to change the status of ${sub.name} (${sub.code}) to ${nextStatus}?`;
  confirmDialogConfig.confirmLabel = nextStatus === 'ACTIVE' ? 'Activate' : 'Deactivate';
  confirmDialogConfig.variant = nextStatus === 'ACTIVE' ? 'primary' : 'warning';
  confirmDialogConfig.action = async () => {
    isSubmittingConfirm.value = true;
    try {
      await subjectService.updateStatus(sub.id, nextStatus);
      showSuccess(`Subject status updated to ${nextStatus}.`);
      isConfirmDialogOpen.value = false;
      loadSubjects();
      loadSummary();
    } catch (err: any) {
      errorMessage.value = err.response?.data?.detail || 'Failed to update subject status.';
    } finally {
      isSubmittingConfirm.value = false;
    }
  };
  isConfirmDialogOpen.value = true;
}

// Delete Subject
function handleDelete(sub: Subject) {
  confirmDialogConfig.title = 'Delete Subject';
  confirmDialogConfig.message = `Are you sure you want to delete ${sub.name} (${sub.code})? This will remove all timetable allocations and class assignments.`;
  confirmDialogConfig.confirmLabel = 'Delete Subject';
  confirmDialogConfig.variant = 'danger';
  confirmDialogConfig.action = async () => {
    isSubmittingConfirm.value = true;
    try {
      await subjectService.deleteSubject(sub.id);
      showSuccess(`Subject "${sub.name}" deleted successfully.`);
      isConfirmDialogOpen.value = false;
      loadSubjects();
      loadSummary();
      loadDepartments();
    } catch (err: any) {
      errorMessage.value = err.response?.data?.detail || 'Failed to delete subject.';
    } finally {
      isSubmittingConfirm.value = false;
    }
  };
  isConfirmDialogOpen.value = true;
}

// Reset Filters
function handleResetFilters() {
  filters.query = '';
  filters.department = '';
  filters.status = '';
  filters.section = '';
  filters.assignment_state = '';
  filters.page = 1;
}

// Toast helper
function showSuccess(msg: string) {
  successMessage.value = msg;
  setTimeout(() => {
    if (successMessage.value === msg) successMessage.value = '';
  }, 4000);
}

function handleApplyDrawerFilters(payload: {
  department: string;
  status: string;
  section: string;
  assignmentState: string;
}) {
  filters.department = payload.department;
  filters.status = payload.status;
  filters.section = payload.section;
  filters.assignment_state = payload.assignmentState;
}
</script>

<template>
  <div class="subjects-view-container">
    <!-- Feedback Alerts -->
    <div v-if="successMessage" class="alert-banner alert-success">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
        <polyline points="22 4 12 14.01 9 11.01" />
      </svg>
      <span>{{ successMessage }}</span>
      <button type="button" class="alert-dismiss" @click="successMessage = ''">&times;</button>
    </div>

    <div v-if="errorMessage" class="alert-banner alert-error">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
      <span>{{ errorMessage }}</span>
      <button type="button" class="alert-dismiss" @click="errorMessage = ''">&times;</button>
    </div>

    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">Subjects</h1>
        <p class="page-subtitle">
          Manage curriculum subjects, codes, departments, teachers and class assignments.
        </p>
      </div>
      <div class="header-actions">
        <button
          type="button"
          class="btn-primary"
          @click="openCreateModal"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          <span>Add Subject</span>
        </button>
      </div>
    </div>

    <!-- Subject Statistics Summary Strip -->
    <SubjectSummary
      :summary="summary"
      :is-loading="isSummaryLoading"
    />

    <!-- Toolbar & Search -->
    <SubjectToolbar
      :search-query="filters.query"
      :selected-department="filters.department"
      :selected-status="filters.status"
      :selected-section="filters.section"
      :selected-assignment-state="filters.assignment_state"
      :active-filter-count="activeFilterCount"
      :departments="departments"
      @update:search-query="filters.query = $event"
      @update:selected-department="filters.department = $event"
      @update:selected-status="filters.status = $event"
      @update:selected-section="filters.section = $event"
      @update:selected-assignment-state="filters.assignment_state = $event"
      @open-filters="isFilterDrawerOpen = true"
      @reset-filters="handleResetFilters"
    />

    <!-- Active Filter Chips -->
    <SubjectActiveChips
      :department="filters.department"
      :status="filters.status"
      :section="filters.section"
      :assignment-state="filters.assignment_state"
      :search="filters.query"
      @remove-department="filters.department = ''"
      @remove-status="filters.status = ''"
      @remove-section="filters.section = ''"
      @remove-assignment-state="filters.assignment_state = ''"
      @remove-search="filters.query = ''"
      @clear-all="handleResetFilters"
    />

    <!-- Main Content State -->
    <div class="main-content-section">
      <!-- Skeleton Loading -->
      <SubjectSkeleton v-if="isLoading" :rows="6" />

      <!-- Empty State -->
      <SubjectEmptyState
        v-else-if="subjects.length === 0"
        :has-filters="Boolean(filters.query || filters.department || filters.status || filters.section || filters.assignment_state)"
        @create="openCreateModal"
        @reset="handleResetFilters"
      />

      <!-- Directory Content (Desktop Table & Mobile Cards) -->
      <template v-else>
        <!-- Desktop / Tablet Table (visible > 640px) -->
        <div class="desktop-directory-wrap">
          <SubjectTable
            :subjects="subjects"
            @edit="openEditModal"
            @assign-class="openAssignClassModal"
            @assign-teacher="openAssignTeacherModal"
            @toggle-status="handleToggleStatus"
            @delete="handleDelete"
          />
        </div>

        <!-- Mobile Card List (visible <= 640px) -->
        <div class="mobile-directory-wrap">
          <SubjectCardList
            :subjects="subjects"
            @edit="openEditModal"
            @assign-class="openAssignClassModal"
            @assign-teacher="openAssignTeacherModal"
            @toggle-status="handleToggleStatus"
            @delete="handleDelete"
          />
        </div>

        <!-- Pagination Controls -->
        <div class="pagination-container">
          <div class="pagination-info">
            Showing {{ (filters.page - 1) * filters.pageSize + 1 }} to
            {{ Math.min(filters.page * filters.pageSize, totalCount || subjects.length) }} of
            {{ totalCount || subjects.length }} subjects
          </div>
          <div class="pagination-actions">
            <button
              type="button"
              class="pagination-btn"
              :disabled="filters.page <= 1"
              @click="filters.page--"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="m15 18-6-6 6-6" />
              </svg>
              <span>Previous</span>
            </button>
            <span class="pagination-current-page">
              Page {{ filters.page }} of {{ totalPages }}
            </span>
            <button
              type="button"
              class="pagination-btn"
              :disabled="subjects.length < filters.pageSize || filters.page >= totalPages"
              @click="filters.page++"
            >
              <span>Next</span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="m9 18 6-6-6-6" />
              </svg>
            </button>
          </div>
        </div>
      </template>
    </div>

    <!-- Filter Drawer (Mobile & Tablet extended filters) -->
    <SubjectFilterDrawer
      :is-open="isFilterDrawerOpen"
      :departments="departments"
      :initial-department="filters.department"
      :initial-status="filters.status"
      :initial-section="filters.section"
      :initial-assignment-state="filters.assignment_state"
      @close="isFilterDrawerOpen = false"
      @apply="handleApplyDrawerFilters"
      @reset="handleResetFilters"
    />

    <!-- Subject Form Modal (Create / Edit) -->
    <SubjectFormModal
      :is-open="isFormModalOpen"
      :is-editing="isEditing"
      :subject="selectedSubject"
      :departments="departments"
      :is-submitting="isSubmittingForm"
      @close="isFormModalOpen = false"
      @save="handleSaveSubject"
    />

    <!-- Assign Class Modal -->
    <SubjectAssignClassModal
      :is-open="isAssignClassModalOpen"
      :subject="selectedSubject"
      :is-submitting="isSubmittingAssignClass"
      @close="isAssignClassModalOpen = false"
      @assign="handleAssignClass"
    />

    <!-- Assign Teacher Modal -->
    <SubjectAssignTeacherModal
      :is-open="isAssignTeacherModalOpen"
      :subject="selectedSubject"
      :is-submitting="isSubmittingAssignTeacher"
      @close="isAssignTeacherModalOpen = false"
      @assign="handleAssignTeacher"
    />

    <!-- Confirmation Dialog -->
    <SubjectConfirmDialog
      :is-open="isConfirmDialogOpen"
      :title="confirmDialogConfig.title"
      :message="confirmDialogConfig.message"
      :confirm-label="confirmDialogConfig.confirmLabel"
      :confirm-variant="confirmDialogConfig.variant"
      :is-submitting="isSubmittingConfirm"
      @close="isConfirmDialogOpen = false"
      @confirm="confirmDialogConfig.action"
    />
  </div>
</template>

<style scoped>
.subjects-view-container {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

/* Alerts */
.alert-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.25rem;
  border-radius: var(--radius-md, 0.5rem);
  font-size: 0.875rem;
  font-weight: 500;
  box-sizing: border-box;
  animation: fadeIn 0.2s ease-out;
}

.alert-banner svg {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

.alert-banner span {
  flex: 1;
}

.alert-dismiss {
  background: none;
  border: none;
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
  color: inherit;
  opacity: 0.7;
}

.alert-dismiss:hover {
  opacity: 1;
}

.alert-success {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #166534;
}

.alert-error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
}

/* Page Header */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--text-main, #0f172a);
  margin: 0;
  letter-spacing: -0.025em;
}

.page-subtitle {
  font-size: 0.875rem;
  color: var(--text-muted, #64748b);
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  height: 2.375rem;
  padding: 0 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #ffffff;
  background: var(--brand-primary, #1e40af);
  border: none;
  border-radius: var(--radius-md, 0.5rem);
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-primary svg {
  width: 1rem;
  height: 1rem;
}

/* Main Content Section */
.main-content-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
}

.desktop-directory-wrap {
  display: block;
}

.mobile-directory-wrap {
  display: none;
}

/* Pagination */
.pagination-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.75rem 0.25rem;
  flex-wrap: wrap;
}

.pagination-info {
  font-size: 0.8125rem;
  color: var(--text-muted, #64748b);
}

.pagination-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.pagination-current-page {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #334155;
  padding: 0 0.5rem;
}

.pagination-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  height: 2rem;
  padding: 0 0.75rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #334155;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: var(--radius-md, 0.5rem);
  cursor: pointer;
  transition: all 0.15s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: #f1f5f9;
  border-color: #94a3b8;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-btn svg {
  width: 0.875rem;
  height: 0.875rem;
}

/* Responsive Breakpoints */
@media (max-width: 640px) {
  .desktop-directory-wrap {
    display: none;
  }

  .mobile-directory-wrap {
    display: block;
  }

  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .btn-primary {
    width: 100%;
    justify-content: center;
  }

  .pagination-container {
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
