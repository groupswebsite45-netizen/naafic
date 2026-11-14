<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { classService } from '../../../services/classService';
import { SchoolClass, ClassSummary as ClassSummaryType } from '../../../types/school';

import ClassSummary from './components/ClassSummary.vue';
import ClassToolbar from './components/ClassToolbar.vue';
import ClassActiveChips from './components/ClassActiveChips.vue';
import ClassFilterDrawer from './components/ClassFilterDrawer.vue';
import ClassTable from './components/ClassTable.vue';
import ClassCardList from './components/ClassCardList.vue';
import ClassFormModal from './components/ClassFormModal.vue';
import ClassEnrollStudentModal from './components/ClassEnrollStudentModal.vue';
import ClassAssignTeacherModal from './components/ClassAssignTeacherModal.vue';
import ClassLevelPromotionModal from './components/ClassLevelPromotionModal.vue';
import ClassConfirmDialog from './components/ClassConfirmDialog.vue';
import ClassSkeleton from './components/ClassSkeleton.vue';
import ClassEmptyState from './components/ClassEmptyState.vue';
import { clearFormDraft } from '../../../composables/useFormDraft';

const router = useRouter();

// State
const classes = ref<SchoolClass[]>([]);
const summary = ref<ClassSummaryType | null>(null);
const isLoading = ref(false);
const isLoadingSummary = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

// Pagination
const currentPage = ref(1);
const pageSize = ref(15);
const totalClasses = ref(0);

// Filters
const filters = reactive({
  query: '',
  academic_year: '',
  division: '',
  status: '',
  level: '',
  section: '',
  capacity_filter: '',
});

const isFilterDrawerOpen = ref(false);
const availableYears = ref<string[]>(['2026/2027']);

// Modal States
const isFormModalOpen = ref(false);
const isEditing = ref(false);
const selectedClass = ref<SchoolClass | null>(null);
const isSubmittingForm = ref(false);

const isEnrollModalOpen = ref(false);
const isSubmittingEnroll = ref(false);

const isAssignTeacherModalOpen = ref(false);
const isSubmittingAssign = ref(false);

const isClassLevelPromotionModalOpen = ref(false);
const classToPromote = ref<SchoolClass | null>(null);

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
  if (filters.academic_year) count++;
  if (filters.division) count++;
  if (filters.status) count++;
  if (filters.level) count++;
  if (filters.section) count++;
  if (filters.capacity_filter) count++;
  return count;
});

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(totalClasses.value / pageSize.value));
});

const paginatedClasses = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return classes.value.slice(start, start + pageSize.value);
});

// Load summary from API
async function loadSummary() {
  isLoadingSummary.value = true;
  try {
    const data = await classService.getSummary();
    summary.value = data;
  } catch (err: any) {
    console.error('Failed to load class summary:', err);
  } finally {
    isLoadingSummary.value = false;
  }
}

// Load classes from API
async function loadClasses() {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    const data = await classService.getClasses({
      query: filters.query.trim() || undefined,
      academic_year: filters.academic_year || undefined,
      division: filters.division || undefined,
      status: filters.status || undefined,
      level: filters.level || undefined,
      section: filters.section || undefined,
      capacity_filter: filters.capacity_filter || undefined,
      skip: 0,
      limit: 100,
    });
    classes.value = Array.isArray(data) ? data : [];
    totalClasses.value = classes.value.length;

    // Collect available years dynamically
    const yearsSet = new Set(availableYears.value);
    classes.value.forEach((c) => {
      if (c.academic_year) yearsSet.add(c.academic_year);
    });
    availableYears.value = Array.from(yearsSet);
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Unable to load classes from database.';
  } finally {
    isLoading.value = false;
  }
}

// Debounced search
let searchTimer: any = null;
watch(
  () => filters.query,
  () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      currentPage.value = 1;
      loadClasses();
    }, 280);
  }
);

watch(
  [
    () => filters.academic_year,
    () => filters.division,
    () => filters.status,
    () => filters.level,
    () => filters.section,
    () => filters.capacity_filter
  ],
  () => {
    currentPage.value = 1;
    loadClasses();
  }
);

onMounted(() => {
  loadSummary();
  loadClasses();
});

// Actions
function handleCreateClass() {
  isEditing.value = false;
  selectedClass.value = null;
  isFormModalOpen.value = true;
}

function handleEditClass(c: SchoolClass) {
  isEditing.value = true;
  selectedClass.value = c;
  isFormModalOpen.value = true;
}

async function handleSaveClass(payload: Partial<SchoolClass>) {
  isSubmittingForm.value = true;
  errorMessage.value = '';
  try {
    if (isEditing.value && selectedClass.value) {
      await classService.updateClass(selectedClass.value.id, payload);
      successMessage.value = `Class '${payload.name}' updated successfully.`;
    } else {
      await classService.createClass(payload);
      clearFormDraft('sms_draft_class_create');
      successMessage.value = `Class '${payload.name}' created successfully.`;
    }
    isFormModalOpen.value = false;
    loadSummary();
    loadClasses();
    setTimeout(() => { successMessage.value = ''; }, 4000);
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to save class.';
  } finally {
    isSubmittingForm.value = false;
  }
}

function handleManageStudents(c: SchoolClass) {
  selectedClass.value = c;
  isEnrollModalOpen.value = true;
}

async function handleEnrollStudent(payload: { studentId: number; academicYear: string; enrollmentDate?: string }) {
  if (!selectedClass.value) return;
  isSubmittingEnroll.value = true;
  errorMessage.value = '';
  try {
    await classService.enrollStudent(
      selectedClass.value.id,
      payload.studentId,
      payload.academicYear,
      payload.enrollmentDate
    );
    successMessage.value = 'Student successfully enrolled in class.';
    isEnrollModalOpen.value = false;
    loadSummary();
    loadClasses();
    setTimeout(() => { successMessage.value = ''; }, 4000);
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to enroll student.';
  } finally {
    isSubmittingEnroll.value = false;
  }
}

function handleAssignTeacher(c: SchoolClass) {
  selectedClass.value = c;
  isAssignTeacherModalOpen.value = true;
}

function handlePromoteClass(c: SchoolClass) {
  classToPromote.value = c;
  isClassLevelPromotionModalOpen.value = true;
}

function handlePromotionSuccess(msg: string) {
  successMessage.value = msg;
  loadSummary();
  loadClasses();
  setTimeout(() => { successMessage.value = ''; }, 5000);
}

async function handleSaveTeacherAssignment(payload: { teacher_id: number; subject_id: number; academic_year: string }) {
  if (!selectedClass.value) return;
  isSubmittingAssign.value = true;
  errorMessage.value = '';
  try {
    await classService.assignTeacher(selectedClass.value.id, payload);
    successMessage.value = 'Teacher assigned to class and subject successfully.';
    isAssignTeacherModalOpen.value = false;
    loadSummary();
    loadClasses();
    setTimeout(() => { successMessage.value = ''; }, 4000);
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to assign teacher.';
  } finally {
    isSubmittingAssign.value = false;
  }
}

function handleToggleStatus(c: SchoolClass) {
  const isDeactivating = c.status === 'ACTIVE';
  confirmDialogConfig.title = isDeactivating ? 'Deactivate Class' : 'Activate Class';
  confirmDialogConfig.message = isDeactivating
    ? `Are you sure you want to deactivate ${c.name} (${c.code})? Historical enrollments and grades will remain intact.`
    : `Activate ${c.name} (${c.code}) to allow active student enrollments and scheduling?`;
  confirmDialogConfig.confirmLabel = isDeactivating ? 'Deactivate' : 'Activate';
  confirmDialogConfig.variant = isDeactivating ? 'danger' : 'primary';

  confirmDialogConfig.action = async () => {
    isSubmittingConfirm.value = true;
    try {
      await classService.updateStatus(c.id, isDeactivating ? 'INACTIVE' : 'ACTIVE');
      successMessage.value = `Class status updated to ${isDeactivating ? 'INACTIVE' : 'ACTIVE'}.`;
      isConfirmDialogOpen.value = false;
      loadSummary();
      loadClasses();
      setTimeout(() => { successMessage.value = ''; }, 4000);
    } catch (err: any) {
      errorMessage.value = err.response?.data?.detail || 'Failed to update class status.';
    } finally {
      isSubmittingConfirm.value = false;
    }
  };

  isConfirmDialogOpen.value = true;
}

function handleApplyDrawerFilters(newFilters: {
  academic_year: string;
  status: string;
  level: string;
  section: string;
  capacity_filter: string;
}) {
  filters.academic_year = newFilters.academic_year;
  filters.status = newFilters.status;
  filters.level = newFilters.level;
  filters.section = newFilters.section;
  filters.capacity_filter = newFilters.capacity_filter;
}

function handleResetAllFilters() {
  filters.query = '';
  filters.academic_year = '';
  filters.status = '';
  filters.level = '';
  filters.section = '';
  filters.capacity_filter = '';
}
</script>

<template>
  <div class="classes-page-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-text-group">
        <div class="page-title-with-badge">
          <h1 class="page-title">Classes</h1>
          <span class="page-count-badge">{{ totalClasses }} Classes</span>
        </div>
        <p class="page-description">
          Manage academic classes, sections, capacity, teachers and student enrollment.
        </p>
      </div>

      <div class="header-actions">
        <button
          type="button"
          class="bulk-promote-btn"
          @click="router.push('/admin/class-promotion')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="17 1 21 5 17 9" />
            <path d="M3 11V9a4 4 0 0 1 4-4h14" />
            <polyline points="7 23 3 19 7 15" />
            <path d="M21 13v2a4 4 0 0 1-4 4H3" />
          </svg>
          <span>Bulk Class Promotion</span>
        </button>

        <button
          type="button"
          class="add-class-btn"
          @click="handleCreateClass"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12h14" />
            <path d="M12 5v14" />
          </svg>
          <span>Add Class</span>
        </button>
      </div>
    </div>

    <!-- Alert Banners -->
    <div v-if="errorMessage" class="alert-banner alert-danger">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" x2="12" y1="8" y2="12" />
        <line x1="12" x2="12.01" y1="16" y2="16" />
      </svg>
      <span>{{ errorMessage }}</span>
      <button type="button" class="alert-close-btn" @click="errorMessage = ''">×</button>
    </div>

    <div v-if="successMessage" class="alert-banner alert-success">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
        <polyline points="22 4 12 14.01 9 11.01" />
      </svg>
      <span>{{ successMessage }}</span>
      <button type="button" class="alert-close-btn" @click="successMessage = ''">×</button>
    </div>

    <!-- Class Statistics -->
    <ClassSummary
      :summary="summary"
      :is-loading="isLoadingSummary"
    />

    <!-- Academic Division Navigation Tabs -->
    <div class="division-tabs-container">
      <button
        type="button"
        class="division-tab-btn"
        :class="{ active: !filters.division }"
        @click="filters.division = ''"
      >
        <span class="tab-label">All Academic Divisions</span>
        <span class="tab-badge">{{ totalClasses }}</span>
      </button>

      <button
        type="button"
        class="division-tab-btn"
        :class="{ active: filters.division === 'PRIMARY' }"
        @click="filters.division = 'PRIMARY'"
      >
        <span class="tab-icon">🏫</span>
        <span class="tab-label">Primary Division</span>
        <span class="tab-sub">(Grades 1–8)</span>
      </button>

      <button
        type="button"
        class="division-tab-btn"
        :class="{ active: filters.division === 'SECONDARY' }"
        @click="filters.division = 'SECONDARY'"
      >
        <span class="tab-icon">🎓</span>
        <span class="tab-label">Secondary Division</span>
        <span class="tab-sub">(Forms 1–4)</span>
      </button>
    </div>

    <!-- Search & Filter Toolbar -->
    <ClassToolbar
      v-model:search-query="filters.query"
      v-model:selected-year="filters.academic_year"
      v-model:selected-division="filters.division"
      v-model:selected-status="filters.status"
      v-model:selected-capacity="filters.capacity_filter"
      :active-filter-count="activeFilterCount"
      :years="availableYears"
      @open-filters="isFilterDrawerOpen = true"
      @reset-filters="handleResetAllFilters"
    />

    <!-- Active Filter Chips -->
    <ClassActiveChips
      :search-query="filters.query"
      :selected-year="filters.academic_year"
      :selected-division="filters.division"
      :selected-status="filters.status"
      :selected-level="filters.level"
      :selected-section="filters.section"
      :selected-capacity="filters.capacity_filter"
      @remove-search="filters.query = ''"
      @remove-year="filters.academic_year = ''"
      @remove-division="filters.division = ''"
      @remove-status="filters.status = ''"
      @remove-level="filters.level = ''"
      @remove-section="filters.section = ''"
      @remove-capacity="filters.capacity_filter = ''"
      @clear-all="handleResetAllFilters"
    />

    <!-- Main Content Area -->
    <div class="directory-content">
      <!-- Loading State -->
      <ClassSkeleton v-if="isLoading" :rows="6" />

      <!-- Empty State -->
      <ClassEmptyState
        v-else-if="classes.length === 0"
        :has-filters="Boolean(filters.query || filters.academic_year || filters.status || filters.level || filters.section || filters.capacity_filter)"
        @create="handleCreateClass"
        @reset="handleResetAllFilters"
      />

      <!-- Desktop & Tablet Data Table (>= 768px) -->
      <div v-else class="table-view-wrapper">
        <ClassTable
          :classes="paginatedClasses"
          @edit="handleEditClass"
          @manage-students="handleManageStudents"
          @assign-teacher="handleAssignTeacher"
          @promote-class="handlePromoteClass"
          @toggle-status="handleToggleStatus"
        />
      </div>

      <!-- Mobile Card List (< 768px) -->
      <div v-if="!isLoading && classes.length > 0" class="cards-view-wrapper">
        <ClassCardList
          :classes="paginatedClasses"
          @edit="handleEditClass"
          @manage-students="handleManageStudents"
          @assign-teacher="handleAssignTeacher"
          @promote-class="handlePromoteClass"
          @toggle-status="handleToggleStatus"
        />
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="!isLoading && totalClasses > 0" class="pagination-container">
      <div class="pagination-info">
        Showing
        <strong>{{ (currentPage - 1) * pageSize + 1 }}</strong>
        –
        <strong>{{ Math.min(currentPage * pageSize, totalClasses) }}</strong>
        of
        <strong>{{ totalClasses }}</strong>
        classes
      </div>

      <div class="pagination-controls">
        <button
          type="button"
          class="page-btn"
          :disabled="currentPage <= 1"
          @click="currentPage--"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="m15 18-6-6 6-6" />
          </svg>
          <span class="btn-text">Previous</span>
        </button>

        <span class="page-indicator">
          Page <strong>{{ currentPage }}</strong> of <strong>{{ totalPages }}</strong>
        </span>

        <button
          type="button"
          class="page-btn"
          :disabled="currentPage >= totalPages"
          @click="currentPage++"
        >
          <span class="btn-text">Next</span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="m9 18 6-6-6-6" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Slide-over Filter Drawer -->
    <ClassFilterDrawer
      :is-open="isFilterDrawerOpen"
      :years="availableYears"
      :initial-filters="filters"
      @close="isFilterDrawerOpen = false"
      @apply="handleApplyDrawerFilters"
      @reset="handleResetAllFilters"
    />

    <!-- Class Form Modal (Create / Edit) -->
    <ClassFormModal
      :is-open="isFormModalOpen"
      :is-editing="isEditing"
      :school-class="selectedClass"
      :is-submitting="isSubmittingForm"
      :years="availableYears"
      @close="isFormModalOpen = false"
      @save="handleSaveClass"
    />

    <!-- Enroll Student Modal -->
    <ClassEnrollStudentModal
      :is-open="isEnrollModalOpen"
      :school-class="selectedClass"
      :is-submitting="isSubmittingEnroll"
      :years="availableYears"
      @close="isEnrollModalOpen = false"
      @enroll="handleEnrollStudent"
    />

    <!-- Assign Teacher Modal -->
    <ClassAssignTeacherModal
      :is-open="isAssignTeacherModalOpen"
      :school-class="selectedClass"
      :is-submitting="isSubmittingAssign"
      :years="availableYears"
      @close="isAssignTeacherModalOpen = false"
      @assign="handleSaveTeacherAssignment"
    />

    <!-- Class-Level Promotion Modal -->
    <ClassLevelPromotionModal
      :is-open="isClassLevelPromotionModalOpen"
      :source-class="classToPromote"
      :available-classes="classes"
      :years="availableYears"
      @close="isClassLevelPromotionModalOpen = false"
      @success="handlePromotionSuccess"
    />

    <!-- Confirmation Dialog -->
    <ClassConfirmDialog
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
.classes-page-container {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  width: 100%;
  box-sizing: border-box;
}

.header-text-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
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

.page-description {
  font-size: 0.86rem;
  color: #64748b;
  margin: 0;
  line-height: 1.4;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.bulk-promote-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  height: 44px;
  padding: 0 1.25rem;
  background-color: #ffffff;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  font-size: 0.86rem;
  font-weight: 600;
  color: #1e293b;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
  box-sizing: border-box;
}

.bulk-promote-btn:hover {
  background-color: #f8fafc;
  border-color: #cbd5e1;
  color: #0f172a;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
}

.bulk-promote-btn svg {
  width: 1.1rem;
  height: 1.1rem;
  color: #4f46e5;
}

.add-class-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  height: 44px;
  padding: 0 1.35rem;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  border: none;
  border-radius: 12px;
  font-size: 0.86rem;
  font-weight: 700;
  color: #ffffff;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(37, 99, 235, 0.35);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
  box-sizing: border-box;
}

.add-class-btn:hover {
  background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
  box-shadow: 0 6px 22px rgba(37, 99, 235, 0.45);
  transform: translateY(-1px);
}

.add-class-btn svg {
  width: 1.1rem;
  height: 1.1rem;
}

/* Division Tabs */
.division-tabs-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #f1f5f9;
  border: 1.5px solid #e2e8f0;
  padding: 0.4rem;
  border-radius: 14px;
  width: 100%;
  max-width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  flex-wrap: nowrap;
  box-sizing: border-box;
  scrollbar-width: thin;
}

.division-tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.55rem 1.15rem;
  min-height: 42px;
  border-radius: 10px;
  border: 1.5px solid transparent;
  background-color: transparent;
  font-size: 0.84rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
  flex-shrink: 0;
  box-sizing: border-box;
}

.division-tab-btn:hover {
  color: #0f172a;
  background-color: rgba(255, 255, 255, 0.7);
}

.division-tab-btn.active {
  background-color: #ffffff;
  color: #1d4ed8;
  border-color: #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  font-weight: 700;
}

.tab-icon {
  font-size: 1rem;
}

.tab-badge {
  font-size: 0.72rem;
  font-weight: 700;
  background-color: #e2e8f0;
  color: #475569;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
}

.division-tab-btn.active .tab-badge {
  background-color: #eff6fe;
  color: #1d4ed8;
}

.tab-sub {
  font-size: 0.72rem;
  font-weight: 500;
  color: #94a3b8;
}

.division-tab-btn.active .tab-sub {
  color: #3b82f6;
}

/* Alerts */
.alert-banner {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  font-size: 0.8125rem;
  font-weight: 500;
  animation: fadeIn 0.15s ease-out;
  width: 100%;
  box-sizing: border-box;
}

.alert-banner svg {
  width: 1.125rem;
  height: 1.125rem;
  flex-shrink: 0;
}

.alert-banner span {
  flex: 1;
  min-width: 0;
  word-break: break-word;
}

.alert-close-btn {
  background: transparent;
  border: none;
  font-size: 1.125rem;
  line-height: 1;
  color: currentColor;
  cursor: pointer;
  padding: 0 0.25rem;
  opacity: 0.7;
}

.alert-close-btn:hover {
  opacity: 1;
}

.alert-danger {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
}

.alert-success {
  background-color: #ecfdf5;
  border: 1px solid #a7f3d0;
  color: #065f46;
}

/* Directory Layouts */
.directory-content {
  background: #ffffff;
  border-radius: 20px;
  border: 1.5px solid #e2e8f0;
  box-shadow: 0 10px 30px -5px rgba(15, 23, 42, 0.05), 0 2px 6px -1px rgba(15, 23, 42, 0.02);
  overflow: hidden;
  width: 100%;
  box-sizing: border-box;
}

.table-view-wrapper {
  display: block;
  width: 100%;
}

.cards-view-wrapper {
  display: none;
  width: 100%;
}

/* Responsive View Switcher */
@media (max-width: 768px) {
  .table-view-wrapper {
    display: none;
  }

  .cards-view-wrapper {
    display: block;
  }

  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }
}

@media (max-width: 500px) {
  .header-actions {
    flex-direction: column;
    width: 100%;
  }

  .bulk-promote-btn,
  .add-class-btn {
    width: 100%;
    height: 44px;
  }
}

/* Pagination */
.pagination-container {
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

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.page-btn {
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
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.page-btn:hover:not(:disabled) {
  background: #f1f5f9;
  border-color: #94a3b8;
  color: #0f172a;
  transform: translateY(-1px);
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-btn svg {
  width: 0.95rem;
  height: 0.95rem;
}

.page-indicator {
  font-size: 0.81rem;
  font-weight: 700;
  color: #1e293b;
  padding: 0 0.4rem;
  white-space: nowrap;
}

.page-indicator strong {
  color: #0f172a;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@media (max-width: 480px) {
  .pagination-container {
    flex-direction: column;
    align-items: center;
    gap: 0.625rem;
  }

  .page-btn .btn-text {
    display: none;
  }
}
</style>
