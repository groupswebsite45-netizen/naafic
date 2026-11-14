<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import {
  TimetableEntry,
  TimetableSummary as ITimetableSummary,
  TimetableFilterOptions,
  SchoolClass,
  Teacher,
  Subject,
  TimetableConflictDetail
} from '../../../types/school';
import { timetableService, CreateTimetablePayload } from '../../../services/timetableService';
import { classService } from '../../../services/classService';
import { teacherService } from '../../../services/teacherService';
import { subjectService } from '../../../services/subjectService';

import TimetableSummary from './components/TimetableSummary.vue';
import TimetableConflictBanner from './components/TimetableConflictBanner.vue';
import TimetableToolbar from './components/TimetableToolbar.vue';
import TimetableActiveChips from './components/TimetableActiveChips.vue';
import TimetableFilterDrawer from './components/TimetableFilterDrawer.vue';
import TimetableWeeklyGrid from './components/TimetableWeeklyGrid.vue';
import TimetableClassView from './components/TimetableClassView.vue';
import TimetableTeacherView from './components/TimetableTeacherView.vue';
import TimetableMobileDayView from './components/TimetableMobileDayView.vue';
import TimetableSlotModal from './components/TimetableSlotModal.vue';
import TimetableConfirmDialog from './components/TimetableConfirmDialog.vue';
import TimetableSkeleton from './components/TimetableSkeleton.vue';
import TimetableEmptyState from './components/TimetableEmptyState.vue';
import TimetableGenerateModal from './components/TimetableGenerateModal.vue';
import TimetableTeacherAvailabilityModal from './components/TimetableTeacherAvailabilityModal.vue';
import { ClassTimetableOverview } from '../../../types/school';

// State
const entries = ref<TimetableEntry[]>([]);
const summary = ref<ITimetableSummary | null>(null);
const filterOptions = ref<TimetableFilterOptions | null>(null);

const availableClasses = ref<SchoolClass[]>([]);
const availableTeachers = ref<Teacher[]>([]);
const availableSubjects = ref<Subject[]>([]);

const isLoading = ref(true);
const isSummaryLoading = ref(true);
const successMessage = ref('');
const errorMessage = ref('');

// Active View Mode
const currentView = ref<'weekly' | 'class' | 'teacher' | 'day'>('weekly');

// Active Filters
const filters = reactive({
  academic_year: '2026/2027',
  class_id: undefined as number | undefined,
  teacher_id: undefined as number | undefined,
  subject_id: undefined as number | undefined,
  day_of_week: undefined as string | undefined,
  room: undefined as string | undefined,
  status: 'ACTIVE',
});

// Modals State
const isSlotModalOpen = ref(false);
const isEditing = ref(false);
const selectedSlot = ref<TimetableEntry | null>(null);
const modalDefaultDay = ref<string | undefined>(undefined);
const modalDefaultClassId = ref<number | undefined>(undefined);
const modalDefaultTeacherId = ref<number | undefined>(undefined);
const isSubmittingSlot = ref(false);
const slotModalError = ref('');

const isFilterDrawerOpen = ref(false);

// Advanced Class-First & Modals State
const isGenerateModalOpen = ref(false);
const isAvailabilityModalOpen = ref(false);
const isPublishing = ref(false);
const isDownloadingPdf = ref(false);
const selectedEducationLevel = ref<'ALL' | 'PRIMARY' | 'SECONDARY'>('ALL');
const classOverview = ref<ClassTimetableOverview | null>(null);
const isLoadingOverview = ref(false);

const selectedClassObj = computed(() => {
  return availableClasses.value.find((c) => c.id === filters.class_id) || null;
});

const filteredClassesByLevel = computed(() => {
  if (selectedEducationLevel.value === 'ALL') return availableClasses.value;
  return availableClasses.value.filter((c) => {
    const name = (c.name || '').toLowerCase();
    if (selectedEducationLevel.value === 'PRIMARY') {
      return (
        name.includes('grade 1') ||
        name.includes('grade 2') ||
        name.includes('grade 3') ||
        name.includes('grade 4') ||
        name.includes('grade 5') ||
        name.includes('grade 6') ||
        name.includes('grade 7') ||
        name.includes('grade 8') ||
        name.includes('primary') ||
        name.includes('class 1') ||
        name.includes('class 2') ||
        name.includes('class 3') ||
        name.includes('class 4') ||
        name.includes('class 5') ||
        name.includes('class 6') ||
        name.includes('class 7') ||
        name.includes('class 8')
      );
    }
    if (selectedEducationLevel.value === 'SECONDARY') {
      return (
        name.includes('grade 9') ||
        name.includes('grade 10') ||
        name.includes('grade 11') ||
        name.includes('grade 12') ||
        name.includes('form 1') ||
        name.includes('form 2') ||
        name.includes('form 3') ||
        name.includes('form 4') ||
        name.includes('secondary')
      );
    }
    return true;
  });
});

async function loadClassOverview(classId?: number) {
  if (!classId) {
    classOverview.value = null;
    return;
  }
  isLoadingOverview.value = true;
  try {
    const data = await timetableService.getClassOverview(classId, filters.academic_year);
    classOverview.value = data;
  } catch (err) {
    console.error('Failed to load class overview:', err);
  } finally {
    isLoadingOverview.value = false;
  }
}

async function handlePublishClass() {
  if (!filters.class_id) return;
  isPublishing.value = true;
  try {
    const res = await timetableService.publishTimetable({
      class_id: filters.class_id,
      academic_year: filters.academic_year
    });
    showSuccess(res.message || 'Timetable published successfully. Live in student & teacher portals.');
    await loadTimetable();
    await loadSummary();
    await loadClassOverview(filters.class_id);
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to publish timetable.';
  } finally {
    isPublishing.value = false;
  }
}

async function handleUnpublishClass() {
  if (!filters.class_id) return;
  isPublishing.value = true;
  try {
    const res = await timetableService.unpublishTimetable({
      class_id: filters.class_id,
      academic_year: filters.academic_year
    });
    showSuccess(res.message || 'Timetable unpublished to draft status.');
    await loadTimetable();
    await loadSummary();
    await loadClassOverview(filters.class_id);
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to unpublish timetable.';
  } finally {
    isPublishing.value = false;
  }
}

async function handleDownloadClassPdf() {
  if (!filters.class_id) return;
  isDownloadingPdf.value = true;
  try {
    const blob = await timetableService.downloadClassPdf(filters.class_id, filters.academic_year);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const clsName = (selectedClassObj.value?.name || `Class_${filters.class_id}`).replace(/\s+/g, '_');
    a.download = `Timetable_${clsName}_${filters.academic_year}.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    showSuccess('Timetable PDF downloaded successfully.');
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to generate PDF timetable.';
  } finally {
    isDownloadingPdf.value = false;
  }
}

async function handleGeneratedTimetable() {
  showSuccess('Timetable generated automatically. Review the weekly grid below and publish when ready.');
  await loadTimetable();
  await loadSummary();
  if (filters.class_id) {
    await loadClassOverview(filters.class_id);
  }
}

const isClassPublished = computed(() => {
  if (!entries.value || entries.value.length === 0) return false;
  return entries.value.some((e) => e.status === 'PUBLISHED');
});

const isConfirmDialogOpen = ref(false);
const confirmDialogConfig = reactive({
  title: '',
  message: '',
  confirmLabel: 'Delete Slot',
  variant: 'danger' as 'danger' | 'primary' | 'warning',
  action: () => {},
});
const isSubmittingConfirm = ref(false);

// Active Filter Count
const activeFilterCount = computed(() => {
  let count = 0;
  if (filters.class_id) count++;
  if (filters.teacher_id) count++;
  if (filters.subject_id) count++;
  if (filters.day_of_week) count++;
  if (filters.room) count++;
  return count;
});

// Standard Days
const standardDays = computed(() => {
  return filterOptions.value?.days_of_week || [
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday'
  ];
});

// Load Summary & Options from PostgreSQL
async function loadSummary() {
  isSummaryLoading.value = true;
  try {
    const data = await timetableService.getSummary(filters.academic_year);
    summary.value = data;
  } catch (err: any) {
    console.error('Failed to load timetable summary:', err);
  } finally {
    isSummaryLoading.value = false;
  }
}

async function loadDropdownsAndOptions() {
  try {
    const [optRes, cRes, tRes, sRes] = await Promise.all([
      timetableService.getFilterOptions(filters.academic_year),
      classService.getClasses({ status: 'ACTIVE', academic_year: filters.academic_year }),
      teacherService.getTeachers({ status: 'ACTIVE' }),
      subjectService.getSubjects({ status: 'ACTIVE' }),
    ]);
    filterOptions.value = optRes;
    availableClasses.value = cRes;
    availableTeachers.value = tRes;
    availableSubjects.value = sRes;

    if (optRes.academic_years.length > 0 && !optRes.academic_years.includes(filters.academic_year)) {
      filters.academic_year = optRes.academic_years[0];
    }
  } catch (err: any) {
    console.error('Failed to load dropdown options:', err);
  }
}

async function loadTimetable() {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    const data = await timetableService.getTimetable({
      academic_year: filters.academic_year,
      class_id: filters.class_id,
      teacher_id: filters.teacher_id,
      subject_id: filters.subject_id,
      day_of_week: filters.day_of_week,
      room: filters.room,
      status: filters.status,
      limit: 300,
    });
    entries.value = data;
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to load timetable entries.';
  } finally {
    isLoading.value = false;
  }
}

// Watchers
watch(
  () => filters.academic_year,
  () => {
    loadSummary();
    loadDropdownsAndOptions();
    loadTimetable();
    if (filters.class_id) {
      loadClassOverview(filters.class_id);
    }
  }
);

watch(
  () => filters.class_id,
  (newId) => {
    loadClassOverview(newId);
  }
);

watch(
  [
    () => filters.class_id,
    () => filters.teacher_id,
    () => filters.subject_id,
    () => filters.day_of_week,
    () => filters.room,
  ],
  () => {
    loadTimetable();
  }
);

onMounted(() => {
  loadDropdownsAndOptions();
  loadSummary();
  loadTimetable();
});

// Modal Actions
function openCreateModal(day?: string, classId?: number, teacherId?: number) {
  isEditing.value = false;
  selectedSlot.value = null;
  slotModalError.value = '';
  modalDefaultDay.value = day;
  modalDefaultClassId.value = classId;
  modalDefaultTeacherId.value = teacherId;
  isSlotModalOpen.value = true;
}

function openEditModal(entry: TimetableEntry) {
  isEditing.value = true;
  selectedSlot.value = entry;
  slotModalError.value = '';
  modalDefaultDay.value = entry.day_of_week;
  modalDefaultClassId.value = entry.class_id;
  modalDefaultTeacherId.value = entry.teacher_id || undefined;
  isSlotModalOpen.value = true;
}

async function handleSaveSlot(payload: CreateTimetablePayload) {
  isSubmittingSlot.value = true;
  slotModalError.value = '';
  try {
    if (isEditing.value && selectedSlot.value) {
      await timetableService.updateTimetable(selectedSlot.value.id, payload);
      showSuccess('Timetable slot updated successfully.');
    } else {
      await timetableService.createTimetable(payload);
      showSuccess('Timetable slot scheduled successfully.');
    }
    isSlotModalOpen.value = false;
    loadTimetable();
    loadSummary();
  } catch (err: any) {
    const errDetail = err.response?.data?.detail || 'Failed to save timetable slot.';
    slotModalError.value = errDetail;
    errorMessage.value = errDetail;
  } finally {
    isSubmittingSlot.value = false;
  }
}

function handleDeleteSlot(entry: TimetableEntry) {
  const subj = entry.subject?.name || entry.subject_name || 'Subject';
  const cls = entry.school_class?.name || entry.class_name || 'Class';
  confirmDialogConfig.title = 'Delete Timetable Slot';
  confirmDialogConfig.message = `Are you sure you want to remove the schedule for ${subj} (${cls}) on ${entry.day_of_week} at ${entry.start_time.slice(0, 5)}?`;
  confirmDialogConfig.confirmLabel = 'Delete Slot';
  confirmDialogConfig.variant = 'danger';
  confirmDialogConfig.action = async () => {
    isSubmittingConfirm.value = true;
    try {
      await timetableService.deleteTimetable(entry.id);
      showSuccess('Timetable slot deleted successfully.');
      isConfirmDialogOpen.value = false;
      loadTimetable();
      loadSummary();
    } catch (err: any) {
      errorMessage.value = err.response?.data?.detail || 'Failed to delete timetable slot.';
    } finally {
      isSubmittingConfirm.value = false;
    }
  };
  isConfirmDialogOpen.value = true;
}

function handleResetFilters() {
  filters.class_id = undefined;
  filters.teacher_id = undefined;
  filters.subject_id = undefined;
  filters.day_of_week = undefined;
  filters.room = undefined;
}

function handleApplyDrawer(payload: {
  classId?: number;
  teacherId?: number;
  subjectId?: number;
  day?: string;
  room?: string;
  status?: string;
}) {
  filters.class_id = payload.classId;
  filters.teacher_id = payload.teacherId;
  filters.subject_id = payload.subjectId;
  filters.day_of_week = payload.day;
  filters.room = payload.room;
  if (payload.status) filters.status = payload.status;
}

function handleReviewConflict(c: TimetableConflictDetail) {
  filters.day_of_week = c.day_of_week;
}

function showSuccess(msg: string) {
  successMessage.value = msg;
  setTimeout(() => {
    if (successMessage.value === msg) successMessage.value = '';
  }, 4000);
}
</script>

<template>
  <div class="timetable-page-container">
    <!-- Alerts -->
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
        <h1 class="page-title">Timetable</h1>
        <p class="page-subtitle">
          Plan and manage weekly class schedules, teachers, subjects and periods.
        </p>
      </div>
      <div class="header-actions">
        <button
          type="button"
          class="btn-secondary"
          @click="isAvailabilityModalOpen = true"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <polyline points="16 11 18 13 22 9" />
          </svg>
          <span>Teacher Availability</span>
        </button>

        <button
          v-if="filters.class_id"
          type="button"
          class="btn-generate-action"
          @click="isGenerateModalOpen = true"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
          </svg>
          <span>Auto-Generate</span>
        </button>

        <button
          type="button"
          class="btn-primary"
          @click="openCreateModal()"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          <span>Add Slot</span>
        </button>
      </div>
    </div>

    <!-- Summary Metrics Cards -->
    <TimetableSummary
      :summary="summary"
      :is-loading="isSummaryLoading"
    />

    <!-- Conflicts Warning Banner -->
    <TimetableConflictBanner
      v-if="summary?.conflicts && summary.conflicts.length > 0"
      :conflicts="summary.conflicts"
      @review-conflict="handleReviewConflict"
    />

    <!-- Class-First Schedule Command Bar -->
    <div class="class-first-control-card">
      <div class="class-first-left">
        <!-- Education Level Filter Tabs -->
        <div class="level-tabs">
          <button
            type="button"
            class="level-tab"
            :class="{ active: selectedEducationLevel === 'ALL' }"
            @click="selectedEducationLevel = 'ALL'"
          >
            All Levels
          </button>
          <button
            type="button"
            class="level-tab"
            :class="{ active: selectedEducationLevel === 'PRIMARY' }"
            @click="selectedEducationLevel = 'PRIMARY'"
          >
            Primary
          </button>
          <button
            type="button"
            class="level-tab"
            :class="{ active: selectedEducationLevel === 'SECONDARY' }"
            @click="selectedEducationLevel = 'SECONDARY'"
          >
            Secondary
          </button>
        </div>

        <!-- Class Quick Selector -->
        <div class="class-picker-wrap">
          <label class="class-picker-label">Class & Section:</label>
          <select
            class="class-picker-select"
            :value="filters.class_id || ''"
            @change="filters.class_id = ($event.target as HTMLSelectElement).value ? Number(($event.target as HTMLSelectElement).value) : undefined"
          >
            <option value="">-- Choose Class to View/Generate Timetable --</option>
            <option v-for="c in filteredClassesByLevel" :key="c.id" :value="c.id">
              {{ c.name }} {{ c.section ? `(${c.section})` : '' }}
            </option>
          </select>
        </div>
      </div>

      <!-- Class Actions when a class is selected -->
      <div v-if="selectedClassObj" class="class-first-actions">
        <!-- Status indicator -->
        <div class="class-status-pill" :class="isClassPublished ? 'status-published' : 'status-draft'">
          <span class="status-indicator-dot" />
          <span>{{ isClassPublished ? 'Published' : 'Draft Mode' }}</span>
        </div>

        <!-- Subject Count Pill -->
        <div v-if="classOverview" class="subjects-count-pill">
          <strong>{{ classOverview.assigned_subjects.length }}</strong> Subjects
        </div>

        <button
          type="button"
          class="btn-action-primary"
          title="Automatically generate full schedule using constraints and assigned teachers"
          @click="isGenerateModalOpen = true"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
          </svg>
          <span>Auto-Generate</span>
        </button>

        <button
          v-if="!isClassPublished && entries.length > 0"
          type="button"
          class="btn-action-publish"
          :disabled="isPublishing"
          @click="handlePublishClass"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </svg>
          <span>{{ isPublishing ? 'Publishing...' : 'Publish' }}</span>
        </button>

        <button
          v-else-if="isClassPublished"
          type="button"
          class="btn-action-unpublish"
          :disabled="isPublishing"
          @click="handleUnpublishClass"
        >
          <span>Unpublish</span>
        </button>

        <button
          type="button"
          class="btn-action-secondary"
          :disabled="isDownloadingPdf || entries.length === 0"
          @click="handleDownloadClassPdf"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
          <span>{{ isDownloadingPdf ? 'Exporting...' : 'PDF' }}</span>
        </button>
      </div>
    </div>

    <!-- Toolbar & View Switcher -->
    <TimetableToolbar
      :academic-year="filters.academic_year"
      :selected-class-id="filters.class_id"
      :selected-teacher-id="filters.teacher_id"
      :selected-subject-id="filters.subject_id"
      :selected-day="filters.day_of_week"
      :selected-room="filters.room"
      :current-view="currentView"
      :active-filter-count="activeFilterCount"
      :academic-years="filterOptions?.academic_years || ['2026/2027']"
      :classes="filteredClassesByLevel"
      :teachers="availableTeachers"
      :subjects="availableSubjects"
      :days="standardDays"
      :rooms="filterOptions?.rooms || []"
      @update:academic-year="filters.academic_year = $event"
      @update:selected-class-id="filters.class_id = $event"
      @update:selected-teacher-id="filters.teacher_id = $event"
      @update:selected-subject-id="filters.subject_id = $event"
      @update:selected-day="filters.day_of_week = $event"
      @update:selected-room="filters.room = $event"
      @update:current-view="currentView = $event"
      @open-filters="isFilterDrawerOpen = true"
      @reset-filters="handleResetFilters"
    />

    <!-- Active Filter Chips -->
    <TimetableActiveChips
      :academic-year="filters.academic_year"
      :selected-class-id="filters.class_id"
      :selected-teacher-id="filters.teacher_id"
      :selected-subject-id="filters.subject_id"
      :selected-day="filters.day_of_week"
      :selected-room="filters.room"
      :classes="availableClasses"
      :teachers="availableTeachers"
      :subjects="availableSubjects"
      @remove-class="filters.class_id = undefined"
      @remove-teacher="filters.teacher_id = undefined"
      @remove-subject="filters.subject_id = undefined"
      @remove-day="filters.day_of_week = undefined"
      @remove-room="filters.room = undefined"
      @clear-all="handleResetFilters"
    />

    <!-- Main Schedule Display Area -->
    <div class="timetable-main-body">
      <!-- Loading Skeleton -->
      <TimetableSkeleton v-if="isLoading" :days-count="standardDays.length" />

      <!-- Class-Specific Empty & Generator State -->
      <div v-else-if="entries.length === 0 && selectedClassObj" class="class-empty-generation-card">
        <div class="empty-icon-box">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect width="18" height="18" x="3" y="4" rx="2" ry="2" />
            <line x1="16" y1="2" x2="16" y2="6" />
            <line x1="8" y1="2" x2="8" y2="6" />
            <line x1="3" y1="10" x2="21" y2="10" />
          </svg>
        </div>
        <div class="empty-text-wrap">
          <h3 class="empty-title">
            No Timetable Scheduled for {{ selectedClassObj.name }}
          </h3>
          <p v-if="classOverview && classOverview.assigned_subjects.length > 0" class="empty-desc">
            This class has <strong>{{ classOverview.assigned_subjects.length }} subjects</strong> with authorized teachers assigned in academic year {{ filters.academic_year }}.
            You can automatically generate an optimized weekly schedule in seconds.
          </p>
          <p v-else class="empty-desc text-warning">
            ⚠️ No subjects or teachers are assigned to {{ selectedClassObj.name }} in {{ filters.academic_year }}.
            Please configure academic assignments before generating.
          </p>
        </div>

        <div class="empty-actions-row">
          <button
            v-if="classOverview && classOverview.assigned_subjects.length > 0"
            type="button"
            class="btn-primary-large"
            @click="isGenerateModalOpen = true"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
            </svg>
            <span>Auto-Generate Timetable Now</span>
          </button>
          <button
            type="button"
            class="btn-secondary-large"
            @click="openCreateModal(undefined, selectedClassObj.id)"
          >
            + Add Period Manually
          </button>
        </div>
      </div>

      <!-- General Empty State -->
      <TimetableEmptyState
        v-else-if="entries.length === 0"
        :has-filters="Boolean(filters.class_id || filters.teacher_id || filters.subject_id || filters.day_of_week || filters.room)"
        @add-slot="openCreateModal()"
        @reset="handleResetFilters"
      />

      <!-- Content Views -->
      <template v-else>
        <!-- Desktop / Tablet: Weekly Grid View -->
        <div v-if="currentView === 'weekly'" class="desktop-view-wrap">
          <TimetableWeeklyGrid
            :entries="entries"
            :days="standardDays"
            @edit="openEditModal"
            @delete="handleDeleteSlot"
            @add-slot="openCreateModal($event)"
          />
        </div>

        <!-- Class View -->
        <div v-else-if="currentView === 'class'" class="class-view-wrap">
          <TimetableClassView
            :entries="entries"
            :classes="availableClasses"
            :selected-class-id="filters.class_id"
            :days="standardDays"
            @update:selected-class-id="filters.class_id = $event"
            @edit="openEditModal"
            @delete="handleDeleteSlot"
            @add-slot-for-class="openCreateModal($event.day, $event.classId)"
          />
        </div>

        <!-- Teacher View -->
        <div v-else-if="currentView === 'teacher'" class="teacher-view-wrap">
          <TimetableTeacherView
            :entries="entries"
            :teachers="availableTeachers"
            :selected-teacher-id="filters.teacher_id"
            :days="standardDays"
            @update:selected-teacher-id="filters.teacher_id = $event"
            @edit="openEditModal"
            @delete="handleDeleteSlot"
            @add-slot-for-teacher="openCreateModal($event.day, undefined, $event.teacherId)"
          />
        </div>

        <!-- Mobile Day View (or forced Day View) -->
        <div v-else-if="currentView === 'day'" class="day-view-wrap">
          <TimetableMobileDayView
            :entries="entries"
            :days="standardDays"
            @edit="openEditModal"
            @delete="handleDeleteSlot"
            @add-slot="openCreateModal($event)"
          />
        </div>

        <!-- Mobile automatic fallback (if width <= 640px and on weekly view) -->
        <div class="mobile-auto-fallback">
          <TimetableMobileDayView
            :entries="entries"
            :days="standardDays"
            @edit="openEditModal"
            @delete="handleDeleteSlot"
            @add-slot="openCreateModal($event)"
          />
        </div>
      </template>
    </div>

    <!-- Modals -->
    <!-- Slot Modal (Add / Edit) -->
    <TimetableSlotModal
      :is-open="isSlotModalOpen"
      :is-editing="isEditing"
      :slot="selectedSlot"
      :default-day="modalDefaultDay"
      :default-class-id="modalDefaultClassId"
      :default-teacher-id="modalDefaultTeacherId"
      :academic-year="filters.academic_year"
      :classes="availableClasses"
      :teachers="availableTeachers"
      :subjects="availableSubjects"
      :days="standardDays"
      :rooms="filterOptions?.rooms || []"
      :is-submitting="isSubmittingSlot"
      :submit-error="slotModalError"
      @close="isSlotModalOpen = false"
      @save="handleSaveSlot"
    />

    <!-- Filter Drawer -->
    <TimetableFilterDrawer
      :is-open="isFilterDrawerOpen"
      :academic-year="filters.academic_year"
      :initial-class-id="filters.class_id"
      :initial-teacher-id="filters.teacher_id"
      :initial-subject-id="filters.subject_id"
      :initial-day="filters.day_of_week"
      :initial-room="filters.room"
      :initial-status="filters.status"
      :classes="availableClasses"
      :teachers="availableTeachers"
      :subjects="availableSubjects"
      :days="standardDays"
      :rooms="filterOptions?.rooms || []"
      @close="isFilterDrawerOpen = false"
      @apply="handleApplyDrawer"
      @reset="handleResetFilters"
    />

    <!-- Delete Confirmation Dialog -->
    <TimetableConfirmDialog
      :is-open="isConfirmDialogOpen"
      :title="confirmDialogConfig.title"
      :message="confirmDialogConfig.message"
      :confirm-label="confirmDialogConfig.confirmLabel"
      :confirm-variant="confirmDialogConfig.variant"
      :is-submitting="isSubmittingConfirm"
      @close="isConfirmDialogOpen = false"
      @confirm="confirmDialogConfig.action"
    />

    <!-- Automatic Timetable Generator Modal -->
    <TimetableGenerateModal
      :is-open="isGenerateModalOpen"
      :selected-class="selectedClassObj"
      :academic-year="filters.academic_year"
      @close="isGenerateModalOpen = false"
      @generated="handleGeneratedTimetable"
    />

    <!-- Teacher Availability Modal -->
    <TimetableTeacherAvailabilityModal
      :is-open="isAvailabilityModalOpen"
      :teachers="availableTeachers"
      :academic-year="filters.academic_year"
      @close="isAvailabilityModalOpen = false"
      @saved="loadTimetable"
    />
  </div>
</template>

<style scoped>
.timetable-page-container {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

/* Class-First Command Card */
.class-first-control-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-left: 4px solid var(--brand-primary, #1e40af);
  border-radius: var(--radius-lg, 0.75rem);
  padding: 0.875rem 1.125rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
  gap: 1rem;
  flex-wrap: wrap;
}

.class-first-left {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  flex-wrap: wrap;
}

.level-tabs {
  display: flex;
  background: #f1f5f9;
  padding: 0.2rem;
  border-radius: 0.375rem;
  gap: 0.2rem;
}

.level-tab {
  padding: 0.35rem 0.625rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #475569;
  background: transparent;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.12s ease;
}

.level-tab.active {
  background: #ffffff;
  color: var(--brand-primary, #1e40af);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}

.class-picker-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.class-picker-label {
  font-size: 0.8125rem;
  font-weight: 700;
  color: #334155;
  white-space: nowrap;
}

.class-picker-select {
  padding: 0.45rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #0f172a;
  background: #ffffff;
  min-width: 240px;
}

.class-first-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.class-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.3rem 0.625rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 700;
}

.status-indicator-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
}

.class-status-pill.status-published {
  background: #dcfce7;
  color: #15803d;
}

.class-status-pill.status-published .status-indicator-dot {
  background: #16a34a;
}

.class-status-pill.status-draft {
  background: #fef3c7;
  color: #92400e;
}

.class-status-pill.status-draft .status-indicator-dot {
  background: #d97706;
}

.subjects-count-pill {
  font-size: 0.75rem;
  color: #475569;
  background: #f1f5f9;
  padding: 0.3rem 0.625rem;
  border-radius: 0.375rem;
}

.btn-action-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.45rem 0.875rem;
  background: var(--brand-primary, #1e40af);
  color: #ffffff;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.12s ease;
}

.btn-action-primary:hover {
  background: #1d4ed8;
}

.btn-action-primary svg, .btn-action-publish svg, .btn-action-secondary svg {
  width: 0.875rem;
  height: 0.875rem;
}

.btn-action-publish {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.45rem 0.875rem;
  background: #15803d;
  color: #ffffff;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-action-publish:hover {
  background: #166534;
}

.btn-action-unpublish {
  padding: 0.45rem 0.75rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-action-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.45rem 0.75rem;
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  color: #334155;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-action-secondary:disabled, .btn-action-publish:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-generate-action {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  height: 2.375rem;
  padding: 0 0.875rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #ffffff;
  background: #0284c7;
  border: none;
  border-radius: var(--radius-md, 0.5rem);
  cursor: pointer;
}

.btn-generate-action svg {
  width: 1rem;
  height: 1rem;
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  height: 2.375rem;
  padding: 0 0.875rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #334155;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: var(--radius-md, 0.5rem);
  cursor: pointer;
}

.btn-secondary svg {
  width: 1rem;
  height: 1rem;
}

/* Class Empty Generation Card */
.class-empty-generation-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: var(--radius-lg, 0.75rem);
  padding: 3rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 1.25rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.empty-icon-box {
  width: 4rem;
  height: 4rem;
  border-radius: 1rem;
  background: #eff6ff;
  color: var(--brand-primary, #1e40af);
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-icon-box svg {
  width: 2rem;
  height: 2rem;
}

.empty-title {
  font-size: 1.15rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 0.5rem 0;
}

.empty-desc {
  font-size: 0.875rem;
  color: #64748b;
  max-width: 520px;
  margin: 0 auto;
  line-height: 1.5;
}

.text-warning {
  color: #b45309;
}

.empty-actions-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
}

.btn-primary-large {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  background: var(--brand-primary, #1e40af);
  color: #ffffff;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.9375rem;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(30, 64, 175, 0.2);
}

.btn-primary-large svg {
  width: 1.125rem;
  height: 1.125rem;
}

.btn-secondary-large {
  padding: 0.625rem 1.125rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  color: #334155;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
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

/* Main Display Area */
.timetable-main-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
}

.desktop-view-wrap {
  display: block;
}

.mobile-auto-fallback {
  display: none;
}

@media (max-width: 768px) {
  .class-first-control-card {
    flex-direction: column;
    align-items: stretch;
  }

  .class-first-left {
    flex-direction: column;
    align-items: stretch;
    width: 100%;
  }

  .class-picker-wrap {
    flex-direction: column;
    align-items: flex-start;
    width: 100%;
  }

  .class-picker-select {
    min-width: 0 !important;
    width: 100% !important;
    max-width: 100%;
    box-sizing: border-box;
  }

  .class-first-actions {
    width: 100%;
    flex-wrap: wrap;
    justify-content: flex-start;
  }
}

@media (max-width: 640px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .btn-primary {
    width: 100%;
    justify-content: center;
  }

  .desktop-view-wrap {
    display: none;
  }

  .mobile-auto-fallback {
    display: block;
  }

  .level-tabs {
    width: 100%;
  }

  .level-tab {
    flex: 1;
    text-align: center;
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
