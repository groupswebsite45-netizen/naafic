<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import {
  formMasterService,
  type ClassFormMasterItem,
  type AvailableTeacherItem,
  type FormMasterAdminOverview,
} from '../../../services/formMasterService';

// State
const loading = ref(false);
const errorMsg = ref('');
const successMsg = ref('');

const overview = ref<FormMasterAdminOverview>({
  total_classes: 0,
  assigned_classes_count: 0,
  unassigned_classes_count: 0,
  total_form_masters: 0,
  academic_year: '2026/2027',
});

const classesList = ref<ClassFormMasterItem[]>([]);
const availableTeachers = ref<AvailableTeacherItem[]>([]);

// Filters
const searchQuery = ref('');
const selectedYear = ref('2026/2027');
const selectedDivision = ref('ALL');
const selectedStatus = ref<'ALL' | 'ASSIGNED' | 'UNASSIGNED'>('ALL');

// Modals
const showAppointModal = ref(false);
const showReplaceModal = ref(false);
const showRevokeModal = ref(false);

// Appoint Form State
const appointTeacherId = ref<number | null>(null);
const appointClassIds = ref<number[]>([]);
const appointNotes = ref('');
const appointSubmitting = ref(false);

// Replace Form State
const targetClassItem = ref<ClassFormMasterItem | null>(null);
const replaceTeacherId = ref<number | null>(null);
const replaceNotes = ref('');
const replaceSubmitting = ref(false);

// Revoke Form State
const revokeItem = ref<ClassFormMasterItem | null>(null);
const revokeNotes = ref('');
const revokeSubmitting = ref(false);

onMounted(() => {
  fetchData();
});

async function fetchData() {
  loading.value = true;
  errorMsg.value = '';
  try {
    const [overviewData, classesData, teachersData] = await Promise.all([
      formMasterService.getOverview(selectedYear.value),
      formMasterService.listClasses({ academic_year: selectedYear.value }),
      formMasterService.listAvailableTeachers(selectedYear.value),
    ]);
    overview.value = overviewData;
    classesList.value = classesData;
    availableTeachers.value = teachersData;
  } catch (err: any) {
    errorMsg.value = err?.response?.data?.detail || 'Failed to load Form Master data.';
  } finally {
    loading.value = false;
  }
}

// Filtered Classes
const filteredClasses = computed(() => {
  return classesList.value.filter((c) => {
    // Search query
    if (searchQuery.value.trim()) {
      const q = searchQuery.value.toLowerCase();
      const matchName = c.class_name.toLowerCase().includes(q);
      const matchCode = c.class_code.toLowerCase().includes(q);
      const matchMaster = c.form_master_name?.toLowerCase().includes(q) || false;
      const matchNumber = c.form_master_number?.toLowerCase().includes(q) || false;
      if (!matchName && !matchCode && !matchMaster && !matchNumber) return false;
    }

    // Division
    if (selectedDivision.value !== 'ALL' && c.division !== selectedDivision.value) {
      return false;
    }

    // Status
    if (selectedStatus.value !== 'ALL' && c.status !== selectedStatus.value) {
      return false;
    }

    return true;
  });
});

// Eligible teachers for new appointments (active classes < 2)
const eligibleTeachers = computed(() => {
  return availableTeachers.value.filter((t) => t.can_assign);
});

// Open Appoint Modal
function openAppointModal(preselectedClassId?: number) {
  appointTeacherId.value = null;
  appointClassIds.value = preselectedClassId ? [preselectedClassId] : [];
  appointNotes.value = '';
  showAppointModal.value = true;
}

// Toggle class selection in Appoint Modal
function toggleClassSelection(classId: number) {
  const index = appointClassIds.value.indexOf(classId);
  if (index > -1) {
    appointClassIds.value.splice(index, 1);
  } else {
    if (appointClassIds.value.length >= 2) {
      errorMsg.value = 'A teacher can be assigned to at most two classes.';
      setTimeout(() => (errorMsg.value = ''), 4000);
      return;
    }
    appointClassIds.value.push(classId);
  }
}

async function handleAppointSubmit() {
  if (!appointTeacherId.value) {
    errorMsg.value = 'Please select a teacher to appoint.';
    return;
  }
  if (appointClassIds.value.length === 0) {
    errorMsg.value = 'Please select at least one class.';
    return;
  }

  appointSubmitting.value = true;
  errorMsg.value = '';
  try {
    await formMasterService.appoint({
      teacher_id: appointTeacherId.value,
      class_ids: appointClassIds.value,
      academic_year: selectedYear.value,
      notes: appointNotes.value.trim() || undefined,
    });
    successMsg.value = 'Form Master successfully appointed!';
    showAppointModal.value = false;
    await fetchData();
    setTimeout(() => (successMsg.value = ''), 4000);
  } catch (err: any) {
    errorMsg.value = err?.response?.data?.detail || 'Failed to appoint Form Master.';
  } finally {
    appointSubmitting.value = false;
  }
}

// Open Replace Modal
function openReplaceModal(item: ClassFormMasterItem) {
  targetClassItem.value = item;
  replaceTeacherId.value = null;
  replaceNotes.value = '';
  showReplaceModal.value = true;
}

async function handleReplaceSubmit() {
  if (!targetClassItem.value?.assignment_id || !replaceTeacherId.value) {
    errorMsg.value = 'Please select a replacement teacher.';
    return;
  }

  replaceSubmitting.value = true;
  errorMsg.value = '';
  try {
    await formMasterService.replace(targetClassItem.value.assignment_id, {
      new_teacher_id: replaceTeacherId.value,
      notes: replaceNotes.value.trim() || undefined,
    });
    successMsg.value = `Form Master for ${targetClassItem.value.class_name} replaced successfully!`;
    showReplaceModal.value = false;
    await fetchData();
    setTimeout(() => (successMsg.value = ''), 4000);
  } catch (err: any) {
    errorMsg.value = err?.response?.data?.detail || 'Failed to replace Form Master.';
  } finally {
    replaceSubmitting.value = false;
  }
}

// Open Revoke Modal
function openRevokeModal(item: ClassFormMasterItem) {
  revokeItem.value = item;
  revokeNotes.value = '';
  showRevokeModal.value = true;
}

async function handleRevokeSubmit() {
  if (!revokeItem.value?.assignment_id) return;

  revokeSubmitting.value = true;
  errorMsg.value = '';
  try {
    await formMasterService.revoke(revokeItem.value.assignment_id, {
      notes: revokeNotes.value.trim() || undefined,
    });
    successMsg.value = `Form Master appointment for ${revokeItem.value.class_name} has been revoked.`;
    showRevokeModal.value = false;
    await fetchData();
    setTimeout(() => (successMsg.value = ''), 4000);
  } catch (err: any) {
    errorMsg.value = err?.response?.data?.detail || 'Failed to revoke Form Master appointment.';
  } finally {
    revokeSubmitting.value = false;
  }
}

function formatDate(dateStr?: string) {
  if (!dateStr) return '—';
  try {
    return new Date(dateStr).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return dateStr;
  }
}
</script>

<template>
  <div class="form-master-management">
    <!-- Header -->
    <header class="page-header">
      <div class="header-left">
        <div class="title-wrap">
          <div class="icon-badge">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <div>
            <h1 class="page-title">Form Master Management</h1>
            <p class="page-subtitle">
              Appoint and supervise dedicated Form Masters to monitor student academics, attendance, and fee status.
            </p>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <button
          type="button"
          class="btn btn-primary"
          @click="openAppointModal()"
        >
          <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Appoint Form Master
        </button>
      </div>
    </header>

    <!-- Notifications / Alerts -->
    <div v-if="successMsg" class="alert alert-success">
      <svg class="alert-icon" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
      </svg>
      <span>{{ successMsg }}</span>
    </div>

    <div v-if="errorMsg" class="alert alert-error">
      <svg class="alert-icon" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
      </svg>
      <span>{{ errorMsg }}</span>
    </div>

    <!-- Overview Metrics Cards -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-info">
          <span class="metric-label">Total Classes</span>
          <span class="metric-val">{{ overview.total_classes }}</span>
        </div>
        <div class="metric-icon-wrap bg-blue-subtle text-blue">
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-info">
          <span class="metric-label">Assigned Classes</span>
          <span class="metric-val text-green">{{ overview.assigned_classes_count }}</span>
        </div>
        <div class="metric-icon-wrap bg-green-subtle text-green">
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-info">
          <span class="metric-label">Unassigned Classes</span>
          <span class="metric-val text-amber">{{ overview.unassigned_classes_count }}</span>
        </div>
        <div class="metric-icon-wrap bg-amber-subtle text-amber">
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-info">
          <span class="metric-label">Active Form Masters</span>
          <span class="metric-val text-orange">{{ overview.total_form_masters }}</span>
        </div>
        <div class="metric-icon-wrap bg-orange-subtle text-orange">
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
      </div>
    </div>

    <!-- Filter & Search Toolbar -->
    <div class="filter-toolbar">
      <div class="search-wrap">
        <svg class="search-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="Search by class name, code or teacher..."
        />
      </div>

      <div class="filters-row">
        <!-- Division filter -->
        <div class="segmented-control">
          <button
            type="button"
            class="seg-btn"
            :class="{ active: selectedDivision === 'ALL' }"
            @click="selectedDivision = 'ALL'"
          >
            All Divisions
          </button>
          <button
            type="button"
            class="seg-btn"
            :class="{ active: selectedDivision === 'PRIMARY' }"
            @click="selectedDivision = 'PRIMARY'"
          >
            Primary
          </button>
          <button
            type="button"
            class="seg-btn"
            :class="{ active: selectedDivision === 'SECONDARY' }"
            @click="selectedDivision = 'SECONDARY'"
          >
            Secondary
          </button>
        </div>

        <!-- Status filter -->
        <div class="segmented-control">
          <button
            type="button"
            class="seg-btn"
            :class="{ active: selectedStatus === 'ALL' }"
            @click="selectedStatus = 'ALL'"
          >
            All
          </button>
          <button
            type="button"
            class="seg-btn"
            :class="{ active: selectedStatus === 'ASSIGNED' }"
            @click="selectedStatus = 'ASSIGNED'"
          >
            Assigned
          </button>
          <button
            type="button"
            class="seg-btn"
            :class="{ active: selectedStatus === 'UNASSIGNED' }"
            @click="selectedStatus = 'UNASSIGNED'"
          >
            Unassigned
          </button>
        </div>

        <button
          type="button"
          class="btn btn-secondary btn-icon-only"
          title="Refresh"
          @click="fetchData()"
        >
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Table of Classes -->
    <div class="table-card">
      <div v-if="loading" class="loading-state">
        <div class="spinner" />
        <p>Loading class assignments...</p>
      </div>

      <div v-else-if="filteredClasses.length === 0" class="empty-state">
        <svg class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="empty-title">No classes match the criteria</p>
        <p class="empty-subtitle">Try adjusting your search query or filters.</p>
      </div>

      <table v-else class="data-table">
        <thead>
          <tr>
            <th>Class</th>
            <th>Division / Level</th>
            <th>Section</th>
            <th>Students</th>
            <th>Appointed Form Master</th>
            <th>Appointed Date</th>
            <th>Status</th>
            <th class="text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredClasses" :key="item.class_id">
            <td class="font-medium">
              <div class="class-title">{{ item.class_name }}</div>
              <span class="class-code">{{ item.class_code }}</span>
            </td>
            <td>
              <span class="badge" :class="item.division === 'PRIMARY' ? 'badge-primary' : 'badge-secondary'">
                {{ item.division }} &bull; {{ item.level }}
              </span>
            </td>
            <td>
              <span class="section-tag">{{ item.section || '—' }}</span>
            </td>
            <td>
              <span class="student-count">{{ item.student_count }} enrolled</span>
            </td>
            <td>
              <div v-if="item.status === 'ASSIGNED' && item.form_master_name" class="teacher-cell">
                <div class="teacher-avatar">
                  {{ item.form_master_name.slice(0, 2).toUpperCase() }}
                </div>
                <div class="teacher-info">
                  <span class="teacher-name">{{ item.form_master_name }}</span>
                  <span class="teacher-meta">{{ item.form_master_number }} &bull; {{ item.form_master_phone || item.form_master_email }}</span>
                </div>
              </div>
              <span v-else class="unassigned-text">No Form Master appointed</span>
            </td>
            <td>{{ formatDate(item.appointed_at) }}</td>
            <td>
              <span
                class="status-pill"
                :class="item.status === 'ASSIGNED' ? 'status-assigned' : 'status-unassigned'"
              >
                {{ item.status }}
              </span>
            </td>
            <td class="text-right">
              <div class="action-buttons">
                <button
                  v-if="item.status === 'UNASSIGNED'"
                  type="button"
                  class="btn btn-sm btn-primary"
                  @click="openAppointModal(item.class_id)"
                >
                  Appoint
                </button>
                <template v-else>
                  <button
                    type="button"
                    class="btn btn-sm btn-outline"
                    title="Replace with another teacher"
                    @click="openReplaceModal(item)"
                  >
                    Replace
                  </button>
                  <button
                    type="button"
                    class="btn btn-sm btn-danger"
                    title="Revoke appointment"
                    @click="openRevokeModal(item)"
                  >
                    Revoke
                  </button>
                </template>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ================================================================= -->
    <!-- MODAL 1: Appoint Form Master -->
    <!-- ================================================================= -->
    <div v-if="showAppointModal" class="modal-backdrop" @click.self="showAppointModal = false">
      <div class="modal-box">
        <div class="modal-header">
          <div>
            <h2 class="modal-title">Appoint Form Master</h2>
            <p class="modal-subtitle">Assign a qualified teacher to supervise 1 or 2 classes.</p>
          </div>
          <button type="button" class="close-x-btn" @click="showAppointModal = false">&times;</button>
        </div>

        <form @submit.prevent="handleAppointSubmit" class="modal-body">
          <!-- Step 1: Select Teacher -->
          <div class="form-group">
            <label class="form-label">Select Teacher <span class="text-red">*</span></label>
            <select v-model="appointTeacherId" class="form-select" required>
              <option :value="null" disabled>Choose an active teacher...</option>
              <option
                v-for="t in availableTeachers"
                :key="t.teacher_id"
                :value="t.teacher_id"
                :disabled="!t.can_assign"
              >
                {{ t.full_name }} ({{ t.teacher_number }}) &mdash;
                {{ t.active_form_classes_count }}/2 classes currently assigned
                {{ !t.can_assign ? '[MAX LOAD]' : '' }}
              </option>
            </select>
            <p class="form-hint">Only teachers with fewer than 2 active form classes can be selected.</p>
          </div>

          <!-- Step 2: Select Classes (1 or 2) -->
          <div class="form-group">
            <label class="form-label">
              Select Class(es) (Max 2) <span class="text-red">*</span>
              <span class="selected-badge">{{ appointClassIds.length }}/2 selected</span>
            </label>
            <div class="class-selector-list">
              <div
                v-for="c in classesList"
                :key="c.class_id"
                class="class-select-item"
                :class="{
                  selected: appointClassIds.includes(c.class_id),
                  disabled: c.status === 'ASSIGNED' && !appointClassIds.includes(c.class_id)
                }"
                @click="c.status === 'UNASSIGNED' || appointClassIds.includes(c.class_id) ? toggleClassSelection(c.class_id) : null"
              >
                <input
                  type="checkbox"
                  :checked="appointClassIds.includes(c.class_id)"
                  :disabled="c.status === 'ASSIGNED' && !appointClassIds.includes(c.class_id)"
                  @click.stop="toggleClassSelection(c.class_id)"
                />
                <div class="class-select-meta">
                  <span class="class-name-row">{{ c.class_name }}</span>
                  <span class="class-details-row">
                    {{ c.division }} &bull; {{ c.level }} (Sec: {{ c.section || '—' }})
                    <span v-if="c.status === 'ASSIGNED'" class="text-amber ml-1">
                      &bull; Assigned to {{ c.form_master_name }}
                    </span>
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Step 3: Administrative Notes -->
          <div class="form-group">
            <label class="form-label">Administrative Notes (Optional)</label>
            <textarea
              v-model="appointNotes"
              class="form-textarea"
              rows="2"
              placeholder="e.g. Appointed supervisory master for Term 1 & 2..."
            />
          </div>

          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              @click="showAppointModal = false"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="appointSubmitting || !appointTeacherId || appointClassIds.length === 0"
            >
              {{ appointSubmitting ? 'Appointing...' : 'Confirm Appointment' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ================================================================= -->
    <!-- MODAL 2: Replace Form Master -->
    <!-- ================================================================= -->
    <div v-if="showReplaceModal && targetClassItem" class="modal-backdrop" @click.self="showReplaceModal = false">
      <div class="modal-box">
        <div class="modal-header">
          <div>
            <h2 class="modal-title">Replace Form Master</h2>
            <p class="modal-subtitle">Replace the supervisory teacher for <strong>{{ targetClassItem.class_name }}</strong>.</p>
          </div>
          <button type="button" class="close-x-btn" @click="showReplaceModal = false">&times;</button>
        </div>

        <form @submit.prevent="handleReplaceSubmit" class="modal-body">
          <div class="info-banner">
            <span class="info-label">Current Form Master:</span>
            <strong>{{ targetClassItem.form_master_name }} ({{ targetClassItem.form_master_number }})</strong>
          </div>

          <div class="form-group">
            <label class="form-label">New Replacement Teacher <span class="text-red">*</span></label>
            <select v-model="replaceTeacherId" class="form-select" required>
              <option :value="null" disabled>Choose replacement teacher...</option>
              <option
                v-for="t in eligibleTeachers"
                :key="t.teacher_id"
                :value="t.teacher_id"
                :disabled="t.teacher_id === targetClassItem.form_master_id"
              >
                {{ t.full_name }} ({{ t.teacher_number }}) &mdash; {{ t.active_form_classes_count }}/2 classes
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Handover / Replacement Reason</label>
            <textarea
              v-model="replaceNotes"
              class="form-textarea"
              rows="2"
              placeholder="e.g. Schedule adjustment or faculty handover..."
            />
          </div>

          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              @click="showReplaceModal = false"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="replaceSubmitting || !replaceTeacherId"
            >
              {{ replaceSubmitting ? 'Replacing...' : 'Confirm Replacement' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ================================================================= -->
    <!-- MODAL 3: Revoke Appointment -->
    <!-- ================================================================= -->
    <div v-if="showRevokeModal && revokeItem" class="modal-backdrop" @click.self="showRevokeModal = false">
      <div class="modal-box modal-box-sm">
        <div class="modal-header">
          <div>
            <h2 class="modal-title text-red">Revoke Appointment</h2>
            <p class="modal-subtitle">Revoke Form Master appointment for {{ revokeItem.class_name }}.</p>
          </div>
          <button type="button" class="close-x-btn" @click="showRevokeModal = false">&times;</button>
        </div>

        <form @submit.prevent="handleRevokeSubmit" class="modal-body">
          <div class="warning-callout">
            <p>
              Are you sure you want to revoke <strong>{{ revokeItem.form_master_name }}</strong> as Form Master of
              <strong>{{ revokeItem.class_name }}</strong>?
            </p>
            <p class="mt-2 text-xs text-muted">
              Their dedicated "My Form Classes" access to this class's academic, attendance, and fee supervision will be immediately revoked.
            </p>
          </div>

          <div class="form-group mt-3">
            <label class="form-label">Revocation Reason (Optional)</label>
            <textarea
              v-model="revokeNotes"
              class="form-textarea"
              rows="2"
              placeholder="e.g. End of term or reassignment..."
            />
          </div>

          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              @click="showRevokeModal = false"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="btn btn-danger"
              :disabled="revokeSubmitting"
            >
              {{ revokeSubmitting ? 'Revoking...' : 'Revoke Appointment' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.form-master-management {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.title-wrap {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.icon-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #ff6500 0%, #ff8a00 100%);
  color: #fff;
  box-shadow: 0 4px 12px rgba(255, 101, 0, 0.25);
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary, #0f172a);
  margin: 0;
}

.page-subtitle {
  font-size: 0.875rem;
  color: var(--text-muted, #64748b);
  margin: 0.25rem 0 0;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.metric-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem;
  background: var(--bg-surface, #ffffff);
  border: 1px solid var(--border-subtle, #e2e8f0);
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.metric-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.metric-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted, #64748b);
}

.metric-val {
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--text-primary, #0f172a);
}

.metric-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 10px;
}

.bg-blue-subtle { background: #eff6ff; }
.text-blue { color: #2563eb; }
.bg-green-subtle { background: #f0fdf4; }
.text-green { color: #16a34a; }
.bg-amber-subtle { background: #fffbeb; }
.text-amber { color: #d97706; }
.bg-orange-subtle { background: #fff7ed; }
.text-orange { color: #ff6500; }
.text-red { color: #dc2626; }

/* Filter Toolbar */
.filter-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem;
  background: var(--bg-surface, #ffffff);
  border: 1px solid var(--border-subtle, #e2e8f0);
  border-radius: 12px;
}

.search-wrap {
  position: relative;
  flex: 1 1 300px;
  max-width: 450px;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1.125rem;
  height: 1.125rem;
  color: var(--text-muted, #94a3b8);
}

.search-input {
  width: 100%;
  padding: 0.625rem 0.75rem 0.625rem 2.25rem;
  font-size: 0.875rem;
  border: 1px solid var(--border-subtle, #cbd5e1);
  border-radius: 8px;
  background: var(--bg-app, #f8fafc);
  outline: none;
  transition: all 0.15s ease;
}

.search-input:focus {
  border-color: #ff6500;
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(255, 101, 0, 0.15);
}

.filters-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.segmented-control {
  display: flex;
  background: var(--bg-app, #f1f5f9);
  padding: 0.25rem;
  border-radius: 8px;
  gap: 0.25rem;
}

.seg-btn {
  padding: 0.375rem 0.75rem;
  font-size: 0.8125rem;
  font-weight: 600;
  border: none;
  background: transparent;
  color: var(--text-muted, #64748b);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.seg-btn.active {
  background: #ffffff;
  color: #ff6500;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

/* Table Card */
.table-card {
  background: var(--bg-surface, #ffffff);
  border: 1px solid var(--border-subtle, #e2e8f0);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.875rem;
}

.data-table th {
  padding: 0.875rem 1rem;
  background: var(--bg-app, #f8fafc);
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted, #64748b);
  border-bottom: 1px solid var(--border-subtle, #e2e8f0);
}

.data-table td {
  padding: 0.875rem 1rem;
  border-bottom: 1px solid var(--border-subtle, #f1f5f9);
  vertical-align: middle;
}

.data-table tr:hover td {
  background: #f8fafc;
}

.class-title {
  font-weight: 600;
  color: var(--text-primary, #0f172a);
}

.class-code {
  font-size: 0.75rem;
  color: var(--text-muted, #64748b);
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 6px;
}

.badge-primary { background: #eff6ff; color: #1d4ed8; }
.badge-secondary { background: #f5f3ff; color: #6d28d9; }

.section-tag {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  background: #f1f5f9;
  border-radius: 4px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #334155;
}

.student-count {
  font-size: 0.8125rem;
  color: var(--text-muted, #64748b);
}

.teacher-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.teacher-avatar {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: #fff7ed;
  color: #ea580c;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  border: 1px solid #fed7aa;
}

.teacher-info {
  display: flex;
  flex-direction: column;
}

.teacher-name {
  font-weight: 600;
  color: #0f172a;
}

.teacher-meta {
  font-size: 0.75rem;
  color: #64748b;
}

.unassigned-text {
  font-size: 0.8125rem;
  font-style: italic;
  color: #94a3b8;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.625rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.status-assigned {
  background: #dcfce7;
  color: #15803d;
}

.status-unassigned {
  background: #fef3c7;
  color: #b45309;
}

.action-buttons {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  border-radius: 8px;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-primary {
  background: #ff6500;
  color: #ffffff;
}

.btn-primary:hover {
  background: #e05900;
}

.btn-secondary {
  background: #f1f5f9;
  color: #334155;
  border-color: #cbd5e1;
}

.btn-secondary:hover {
  background: #e2e8f0;
}

.btn-outline {
  background: transparent;
  border-color: #cbd5e1;
  color: #334155;
}

.btn-outline:hover {
  background: #f8fafc;
  border-color: #94a3b8;
}

.btn-danger {
  background: #fee2e2;
  color: #b91c1c;
  border-color: #fecaca;
}

.btn-danger:hover {
  background: #fecaca;
  color: #991b1b;
}

.btn-sm {
  padding: 0.25rem 0.625rem;
  font-size: 0.75rem;
}

.btn-icon {
  width: 1.125rem;
  height: 1.125rem;
}

.btn-icon-only {
  padding: 0.5rem;
}

/* Modals */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  padding: 1rem;
}

.modal-box {
  background: #ffffff;
  border-radius: 16px;
  width: 100%;
  max-width: 580px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.modal-box-sm {
  max-width: 460px;
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.modal-subtitle {
  font-size: 0.8125rem;
  color: #64748b;
  margin: 0.25rem 0 0;
}

.close-x-btn {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  line-height: 1;
  color: #94a3b8;
  cursor: pointer;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #334155;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.form-select,
.form-textarea {
  width: 100%;
  padding: 0.625rem 0.75rem;
  font-size: 0.875rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  outline: none;
  background: #ffffff;
}

.form-select:focus,
.form-textarea:focus {
  border-color: #ff6500;
  box-shadow: 0 0 0 3px rgba(255, 101, 0, 0.15);
}

.form-hint {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0.25rem 0 0;
}

.selected-badge {
  font-size: 0.75rem;
  color: #ea580c;
  background: #fff7ed;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
}

.class-selector-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 220px;
  overflow-y: auto;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.5rem;
  background: #f8fafc;
}

.class-select-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.class-select-item:hover {
  border-color: #ff6500;
}

.class-select-item.selected {
  background: #fff7ed;
  border-color: #ff6500;
}

.class-select-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.class-select-meta {
  display: flex;
  flex-direction: column;
}

.class-name-row {
  font-weight: 600;
  font-size: 0.8125rem;
  color: #0f172a;
}

.class-details-row {
  font-size: 0.75rem;
  color: #64748b;
}

.info-banner {
  padding: 0.75rem 1rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.info-label {
  color: #64748b;
}

.warning-callout {
  padding: 1rem;
  background: #fff1f2;
  border: 1px solid #fecdd3;
  border-radius: 8px;
  color: #9f1239;
  font-size: 0.875rem;
}

/* Alerts */
.alert {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.25rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
}

.alert-success {
  background: #dcfce7;
  color: #14532d;
  border: 1px solid #bbf7d0;
}

.alert-error {
  background: #fee2e2;
  color: #7f1d1d;
  border: 1px solid #fecaca;
}

.alert-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1.5rem;
  text-align: center;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e2e8f0;
  border-top-color: #ff6500;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 0.75rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-icon {
  width: 48px;
  height: 48px;
  color: #94a3b8;
  margin-bottom: 0.75rem;
}

.empty-title {
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.empty-subtitle {
  font-size: 0.8125rem;
  color: #64748b;
  margin: 0.25rem 0 0;
}
</style>

