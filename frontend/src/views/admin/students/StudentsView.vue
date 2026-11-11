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

async function loadStudents(retryCount = 0) {
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
      totalCount.value = (res as any).total ?? (summary.value?.total_students && !hasActiveFiltersOrSearch.value ? summary.value.total_students : res.length);
    } else if (res && Array.isArray(res.items)) {
      students.value = res.items;
      totalCount.value = res.total ?? res.items.length;
    } else {
      students.value = [];
      totalCount.value = 0;
    }
  } catch (err: any) {
    if (retryCount < 1) {
      await new Promise(r => setTimeout(r, 450));
      return loadStudents(retryCount + 1);
    }
    errorMessage.value = err.response?.data?.detail || err.response?.data?.message || 'Unable to load students from database. Please try again.';
  } finally {
    isLoading.value = false;
  }
}

function handleRetry() {
  loadStudents(0);
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
    const { photoFile, shouldRemovePhoto, ...studentData } = payload;
    let savedStudent: Student;

    if (isEditing.value && activeStudent.value) {
      savedStudent = await studentService.updateStudent(activeStudent.value.id, studentData);
      if (shouldRemovePhoto) {
        await studentService.deletePhoto(savedStudent.id);
      } else if (photoFile) {
        await studentService.uploadPhoto(savedStudent.id, photoFile);
      }
      successMessage.value = `Student ${payload.first_name} ${payload.last_name} updated successfully.`;
    } else {
      savedStudent = await studentService.createStudent(studentData);
      if (photoFile) {
        try {
          await studentService.uploadPhoto(savedStudent.id, photoFile);
        } catch (photoErr: any) {
          console.warn('Student admitted, but photo upload encountered an issue:', photoErr);
        }
      }
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

// Batch Enable Portals State
const isBatchEnableModalOpen = ref(false);
const isBatchEnabling = ref(false);
const batchPassword = ref('Student@123');
const batchResult = ref<any>(null);

function openBatchEnableModal() {
  batchResult.value = null;
  batchPassword.value = 'Student@123';
  isBatchEnableModalOpen.value = true;
}

async function confirmBatchEnable() {
  isBatchEnabling.value = true;
  errorMessage.value = '';
  try {
    const res = await studentService.batchEnablePortals({
      academic_year: filters.academic_year || undefined,
      class_id: filters.class_id || undefined,
      default_password: batchPassword.value.trim() || 'Student@123',
    });
    batchResult.value = res;
    successMessage.value = res.message;
    await Promise.all([loadStudents(), loadSummary()]);
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to batch enable student portals.';
    isBatchEnableModalOpen.value = false;
  } finally {
    isBatchEnabling.value = false;
  }
}

async function handleTogglePortalQuick(student: Student) {
  try {
    const targetStatus = !student.has_portal_access;
    const res = await studentService.togglePortalQuick(student.id, targetStatus);
    student.has_portal_access = res.has_portal_access;
    if (res.portal_username) {
      student.portal_username = res.portal_username;
    }
    successMessage.value = res.message || `Portal ${targetStatus ? 'enabled' : 'disabled'} for ${student.full_name}.`;
    setTimeout(() => {
      if (successMessage.value && student.full_name && successMessage.value.includes(student.full_name)) {
        successMessage.value = '';
      }
    }, 4000);
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to update student portal access.';
  }
}

async function handleLoginAsStudent(student: Student) {
  try {
    isLoading.value = true;
    const res = await studentService.loginAsStudent(student.id);
    const targetUrl = `/student/exams?impersonate_token=${encodeURIComponent(res.access_token)}`;
    const win = window.open(targetUrl, '_blank');
    if (!win) {
      window.location.href = targetUrl;
    }
    successMessage.value = `Logged in as student ${student.full_name} (${res.username}) in a new tab.`;
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to authenticate as student.';
  } finally {
    isLoading.value = false;
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
          class="btn-portal-batch-header"
          title="Enable student portal for all enrolled students with one click"
          :disabled="isBatchEnabling"
          @click="openBatchEnableModal"
        >
          <svg class="btn-hdr-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <span>{{ isBatchEnabling ? 'Enabling Portals...' : '⚡ Enable All Portals' }}</span>
        </button>
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
      <button class="btn-retry" @click="handleRetry">Retry</button>
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
            @toggle-portal="handleTogglePortalQuick"
            @login-portal="handleLoginAsStudent"
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
            @toggle-portal="handleTogglePortalQuick"
            @login-portal="handleLoginAsStudent"
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

    <!-- Batch Enable Portals Modal -->
    <div
      v-if="isBatchEnableModalOpen"
      class="batch-portal-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="batch-portal-title"
      @keydown.esc="isBatchEnableModalOpen = false"
    >
      <div class="batch-portal-backdrop" @click="isBatchEnableModalOpen = false" />
      <div class="batch-portal-modal">
        <!-- Header -->
        <div class="batch-modal-header">
          <div class="batch-header-icon-wrap">
            <svg class="batch-header-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div class="batch-header-text">
            <h2 id="batch-portal-title" class="batch-modal-title">One-Click Batch Enable Student Portals</h2>
            <p class="batch-modal-subtitle">Automatically provision and activate student portal accounts in bulk.</p>
          </div>
          <button
            type="button"
            class="batch-close-btn"
            aria-label="Close dialog"
            @click="isBatchEnableModalOpen = false"
          >
            &times;
          </button>
        </div>

        <!-- Body -->
        <div class="batch-modal-body">
          <!-- Step 1: Pre-Execution Confirmation -->
          <div v-if="!batchResult" class="batch-prep-state">
            <div class="batch-banner-info">
              <svg class="banner-svg-info" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <strong class="banner-title">Instant School-Wide Provisioning</strong>
                <p class="banner-text">
                  This action will check all enrolled students in <strong>{{ filters.academic_year || 'all years' }}</strong>.
                  Any student without portal credentials will instantly receive a standardized username and active credentials with the <strong>STUDENT</strong> role.
                </p>
              </div>
            </div>

            <!-- Scope Details Grid -->
            <div class="scope-grid">
              <div class="scope-box">
                <span class="scope-label">TARGET STUDENTS</span>
                <span class="scope-val">{{ totalCount }} Students</span>
              </div>
              <div class="scope-box">
                <span class="scope-label">ACADEMIC YEAR</span>
                <span class="scope-val">{{ filters.academic_year || 'All Enrolled' }}</span>
              </div>
              <div class="scope-box">
                <span class="scope-label">CLASS FILTER</span>
                <span class="scope-val">{{ availableClasses.find(c => c.id === filters.class_id)?.name || 'All Classes' }}</span>
              </div>
            </div>

            <!-- Form: Default Password Setting -->
            <div class="batch-form-group">
              <label for="batch-default-pwd" class="batch-label">Default Initial Password for New Accounts</label>
              <input
                id="batch-default-pwd"
                v-model="batchPassword"
                type="text"
                class="batch-input"
                placeholder="e.g. Student@123"
                :disabled="isBatchEnabling"
              />
              <span class="batch-help-text">
                Students can log in with their Admission Number / Username and this password, then change it anytime.
              </span>
            </div>

            <div class="batch-note-box">
              <svg class="note-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              <span>Students who already have configured passwords will keep their existing passwords. Inactive portals will be re-activated without credential loss.</span>
            </div>
          </div>

          <!-- Step 2: Post-Execution Summary -->
          <div v-else class="batch-success-state">
            <div class="batch-banner-success">
              <svg class="banner-svg-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <strong class="banner-title">Batch Provisioning Completed!</strong>
                <p class="banner-text">{{ batchResult.message }}</p>
              </div>
            </div>

            <!-- Result KPI Grid -->
            <div class="batch-stats-grid">
              <div class="batch-stat-card">
                <span class="stat-number">{{ batchResult.total_students }}</span>
                <span class="stat-title">Total Processed</span>
              </div>
              <div class="batch-stat-card new">
                <span class="stat-number">{{ batchResult.newly_created }}</span>
                <span class="stat-title">Newly Created</span>
              </div>
              <div class="batch-stat-card active">
                <span class="stat-number">{{ batchResult.already_active + (batchResult.reactivated || 0) }}</span>
                <span class="stat-title">Active Portals</span>
              </div>
            </div>

            <!-- Scrollable Student Roster -->
            <div v-if="batchResult.students && batchResult.students.length > 0" class="batch-roster-section">
              <h4 class="roster-heading">Updated Student Roster ({{ batchResult.students.length }} Students)</h4>
              <div class="roster-scroll-box">
                <table class="roster-table">
                  <thead>
                    <tr>
                      <th>Adm #</th>
                      <th>Student Name</th>
                      <th>Portal Username</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="st in batchResult.students" :key="st.student_id">
                      <td class="roster-adm">{{ st.admission_number }}</td>
                      <td class="roster-name">{{ st.full_name }}</td>
                      <td class="roster-username">
                        <code>{{ st.portal_username }}</code>
                      </td>
                      <td>
                        <span class="portal-badge-enabled">● Active</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="batch-modal-footer">
          <template v-if="!batchResult">
            <button
              type="button"
              class="btn-batch-cancel"
              :disabled="isBatchEnabling"
              @click="isBatchEnableModalOpen = false"
            >
              Cancel
            </button>
            <button
              type="button"
              class="btn-batch-confirm"
              :disabled="isBatchEnabling"
              @click="confirmBatchEnable"
            >
              <svg v-if="isBatchEnabling" class="spin-icon" viewBox="0 0 24 24" fill="none">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <span>{{ isBatchEnabling ? 'Provisioning Portals...' : '⚡ Confirm & Enable All Portals' }}</span>
            </button>
          </template>
          <template v-else>
            <button
              type="button"
              class="btn-batch-confirm"
              @click="isBatchEnableModalOpen = false"
            >
              Done & Return to Students
            </button>
          </template>
        </div>
      </div>
    </div>
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

/* Header Batch Button */
.btn-portal-batch-header {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.125rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #065f46;
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  border: 1px solid #a7f3d0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 2px rgba(16, 185, 129, 0.08);
}

.btn-portal-batch-header:hover:not(:disabled) {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  border-color: #6ee7b7;
  color: #047857;
  transform: translateY(-1px);
  box-shadow: 0 3px 6px rgba(16, 185, 129, 0.15);
}

.btn-portal-batch-header:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-hdr-icon {
  width: 18px;
  height: 18px;
  color: #059669;
}

/* Batch Portal Modal */
.batch-portal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1050;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.batch-portal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(4px);
}

.batch-portal-modal {
  position: relative;
  width: 100%;
  max-width: 640px;
  background: #ffffff;
  border-radius: 14px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  max-height: 90vh;
  overflow: hidden;
  animation: modalFadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: scale(0.97) translateY(8px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.batch-modal-header {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #f1f5f9;
  background: #fafaf9;
}

.batch-header-icon-wrap {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  background: #ecfdf5;
  color: #059669;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.batch-header-icon {
  width: 22px;
  height: 22px;
}

.batch-header-text {
  flex: 1;
}

.batch-modal-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.batch-modal-subtitle {
  font-size: 0.8125rem;
  color: #64748b;
  margin: 0.2rem 0 0 0;
}

.batch-close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  line-height: 1;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  transition: all 0.15s;
}

.batch-close-btn:hover {
  color: #0f172a;
  background: #f1f5f9;
}

.batch-modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.batch-banner-info,
.batch-banner-success {
  display: flex;
  gap: 0.875rem;
  padding: 1rem;
  border-radius: 10px;
}

.batch-banner-info {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #166534;
}

.banner-svg-info {
  width: 24px;
  height: 24px;
  color: #16a34a;
  flex-shrink: 0;
}

.batch-banner-success {
  background: #ecfdf5;
  border: 1px solid #6ee7b7;
  color: #065f46;
}

.banner-svg-success {
  width: 24px;
  height: 24px;
  color: #059669;
  flex-shrink: 0;
}

.banner-title {
  display: block;
  font-size: 0.9375rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.banner-text {
  font-size: 0.8125rem;
  line-height: 1.45;
  margin: 0;
}

.scope-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.scope-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.scope-label {
  font-size: 0.6875rem;
  font-weight: 700;
  color: #64748b;
  letter-spacing: 0.04em;
}

.scope-val {
  font-size: 0.875rem;
  font-weight: 700;
  color: #0f172a;
}

.batch-form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.batch-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #334155;
}

.batch-input {
  width: 100%;
  padding: 0.625rem 0.875rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.875rem;
  font-family: monospace;
  box-sizing: border-box;
}

.batch-input:focus {
  outline: none;
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15);
}

.batch-help-text {
  font-size: 0.75rem;
  color: #64748b;
}

.batch-note-box {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.75rem 0.875rem;
  background: #fffbeb;
  border: 1px solid #fef3c7;
  border-radius: 8px;
  font-size: 0.75rem;
  color: #92400e;
  line-height: 1.4;
}

.note-svg {
  width: 16px;
  height: 16px;
  color: #d97706;
  flex-shrink: 0;
  margin-top: 1px;
}

/* Success State Stats */
.batch-stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.batch-stat-card {
  padding: 1rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.batch-stat-card.new {
  background: #eff6ff;
  border-color: #bfdbfe;
}

.batch-stat-card.active {
  background: #ecfdf5;
  border-color: #a7f3d0;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 800;
  color: #0f172a;
}

.batch-stat-card.new .stat-number { color: #1d4ed8; }
.batch-stat-card.active .stat-number { color: #047857; }

.stat-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
}

/* Roster Section */
.batch-roster-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.roster-heading {
  font-size: 0.875rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.roster-scroll-box {
  max-height: 220px;
  overflow-y: auto;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.roster-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8125rem;
}

.roster-table th {
  background: #f8fafc;
  padding: 0.5rem 0.75rem;
  font-weight: 600;
  color: #475569;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
  position: sticky;
  top: 0;
}

.roster-table td {
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid #f1f5f9;
  color: #1e293b;
}

.roster-username code {
  background: #f1f5f9;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  font-size: 0.75rem;
  color: #0f172a;
}

.portal-badge-enabled {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.2rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.6875rem;
  font-weight: 600;
  background: #ecfdf5;
  color: #065f46;
}

/* Modal Footer */
.batch-modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}

.btn-batch-cancel {
  padding: 0.625rem 1.125rem;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #475569;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-batch-cancel:hover {
  background: #f1f5f9;
  color: #1e293b;
}

.btn-batch-confirm {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  background: #059669;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.15s;
  box-shadow: 0 1px 2px rgba(5, 150, 105, 0.2);
}

.btn-batch-confirm:hover:not(:disabled) {
  background: #047857;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(5, 150, 105, 0.25);
}

.btn-batch-confirm:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spin-icon {
  width: 16px;
  height: 16px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
