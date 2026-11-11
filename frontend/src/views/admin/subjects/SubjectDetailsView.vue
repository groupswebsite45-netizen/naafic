<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { subjectService } from '../../../services/subjectService';
import {
  SubjectFullProfile,
  SubjectClassAssignmentItem,
  SubjectTeacherAssignmentItem
} from '../../../types/school';

import SubjectStatusBadge from './components/SubjectStatusBadge.vue';
import SubjectFormModal from './components/SubjectFormModal.vue';
import SubjectAssignClassModal from './components/SubjectAssignClassModal.vue';
import SubjectAssignTeacherModal from './components/SubjectAssignTeacherModal.vue';
import SubjectConfirmDialog from './components/SubjectConfirmDialog.vue';
import SubjectSkeleton from './components/SubjectSkeleton.vue';

const route = useRoute();
const router = useRouter();

const subjectId = computed(() => Number(route.params.id));
const subjectProfile = ref<SubjectFullProfile | null>(null);
const isLoading = ref(true);
const errorMessage = ref('');
const successMessage = ref('');
const departments = ref<string[]>([]);

// Active Tab
const activeTab = ref<'overview' | 'classes' | 'teachers' | 'curriculum' | 'timetable' | 'exams'>('overview');

// Modals
const isEditModalOpen = ref(false);
const isSubmittingEdit = ref(false);

const isAssignClassModalOpen = ref(false);
const isSubmittingAssignClass = ref(false);

const isAssignTeacherModalOpen = ref(false);
const isSubmittingAssignTeacher = ref(false);

const isConfirmDialogOpen = ref(false);
const confirmConfig = ref({
  title: '',
  message: '',
  confirmLabel: 'Confirm',
  variant: 'primary' as 'danger' | 'primary' | 'warning',
  action: () => {},
});
const isSubmittingConfirm = ref(false);

// Load Full Profile
async function loadProfile() {
  if (!subjectId.value || isNaN(subjectId.value)) {
    errorMessage.value = 'Invalid subject identifier.';
    isLoading.value = false;
    return;
  }

  isLoading.value = true;
  errorMessage.value = '';
  try {
    const data = await subjectService.getFullProfile(subjectId.value);
    subjectProfile.value = data;
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to load subject profile from database.';
  } finally {
    isLoading.value = false;
  }
}

async function loadDepartments() {
  try {
    departments.value = await subjectService.getDepartments();
  } catch (err) {
    console.error('Failed to load departments:', err);
  }
}

onMounted(() => {
  loadProfile();
  loadDepartments();
});

function goBack() {
  router.push('/admin/subjects');
}

// Edit Subject
function openEditModal() {
  isEditModalOpen.value = true;
}

async function handleSaveEdit(payload: any) {
  if (!subjectProfile.value) return;
  isSubmittingEdit.value = true;
  try {
    await subjectService.updateSubject(subjectProfile.value.id, payload);
    showSuccess('Subject details updated successfully.');
    isEditModalOpen.value = false;
    loadProfile();
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to update subject.';
  } finally {
    isSubmittingEdit.value = false;
  }
}

// Assign to Class
function openAssignClassModal() {
  isAssignClassModalOpen.value = true;
}

async function handleAssignClass(payload: {
  class_id: number;
  teacher_id?: number | null;
  academic_year: string;
  periods_per_week?: number | null;
}) {
  if (!subjectProfile.value) return;
  isSubmittingAssignClass.value = true;
  try {
    await subjectService.assignClass(subjectProfile.value.id, payload);
    showSuccess('Subject allocated to class successfully.');
    isAssignClassModalOpen.value = false;
    loadProfile();
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to allocate subject to class.';
  } finally {
    isSubmittingAssignClass.value = false;
  }
}

// Assign Teacher
function openAssignTeacherModal() {
  isAssignTeacherModalOpen.value = true;
}

async function handleAssignTeacher(payload: {
  teacher_id: number;
  class_id: number;
  academic_year: string;
  section?: string | null;
}) {
  if (!subjectProfile.value) return;
  isSubmittingAssignTeacher.value = true;
  try {
    await subjectService.assignTeacher(subjectProfile.value.id, payload);
    showSuccess('Teacher assigned to subject successfully.');
    isAssignTeacherModalOpen.value = false;
    loadProfile();
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to assign teacher.';
  } finally {
    isSubmittingAssignTeacher.value = false;
  }
}

// Remove Class Assignment
function confirmRemoveClass(assignment: SubjectClassAssignmentItem) {
  confirmConfig.value = {
    title: 'Remove Class Allocation',
    message: `Remove allocation of this subject for ${assignment.class_name} (${assignment.academic_year})?`,
    confirmLabel: 'Remove Allocation',
    variant: 'danger',
    action: async () => {
      isSubmittingConfirm.value = true;
      try {
        await subjectService.removeClass(subjectProfile.value!.id, assignment.id);
        showSuccess('Class allocation removed.');
        isConfirmDialogOpen.value = false;
        loadProfile();
      } catch (err: any) {
        errorMessage.value = err.response?.data?.detail || 'Failed to remove class allocation.';
      } finally {
        isSubmittingConfirm.value = false;
      }
    },
  };
  isConfirmDialogOpen.value = true;
}

// Remove Teacher Assignment
function confirmRemoveTeacher(assignment: SubjectTeacherAssignmentItem) {
  confirmConfig.value = {
    title: 'Remove Teacher Allocation',
    message: `Remove ${assignment.full_name || assignment.teacher_name || 'this teacher'} from teaching this subject for ${assignment.class_name}?`,
    confirmLabel: 'Remove Teacher',
    variant: 'danger',
    action: async () => {
      isSubmittingConfirm.value = true;
      try {
        await subjectService.removeTeacher(subjectProfile.value!.id, assignment.id);
        showSuccess('Teacher allocation removed.');
        isConfirmDialogOpen.value = false;
        loadProfile();
      } catch (err: any) {
        errorMessage.value = err.response?.data?.detail || 'Failed to remove teacher.';
      } finally {
        isSubmittingConfirm.value = false;
      }
    },
  };
  isConfirmDialogOpen.value = true;
}

// Toggle Status
function handleToggleStatus() {
  if (!subjectProfile.value) return;
  const nextStatus = subjectProfile.value.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE';
  confirmConfig.value = {
    title: `${nextStatus === 'ACTIVE' ? 'Activate' : 'Deactivate'} Subject`,
    message: `Change the status of ${subjectProfile.value.name} to ${nextStatus}?`,
    confirmLabel: nextStatus === 'ACTIVE' ? 'Activate' : 'Deactivate',
    variant: nextStatus === 'ACTIVE' ? 'primary' : 'warning',
    action: async () => {
      isSubmittingConfirm.value = true;
      try {
        await subjectService.updateStatus(subjectProfile.value!.id, nextStatus);
        showSuccess(`Subject status updated to ${nextStatus}.`);
        isConfirmDialogOpen.value = false;
        loadProfile();
      } catch (err: any) {
        errorMessage.value = err.response?.data?.detail || 'Failed to update status.';
      } finally {
        isSubmittingConfirm.value = false;
      }
    },
  };
  isConfirmDialogOpen.value = true;
}

function showSuccess(msg: string) {
  successMessage.value = msg;
  setTimeout(() => {
    if (successMessage.value === msg) successMessage.value = '';
  }, 4000);
}
</script>

<template>
  <div class="subject-profile-container">
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

    <!-- Back Button -->
    <div class="navigation-bar">
      <button type="button" class="back-link-btn" @click="goBack">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="m15 18-6-6 6-6" />
        </svg>
        <span>Back to Subjects</span>
      </button>
    </div>

    <!-- Loading Skeleton -->
    <div v-if="isLoading" class="loading-wrap">
      <SubjectSkeleton :rows="4" />
    </div>

    <!-- Error State -->
    <div v-else-if="!subjectProfile" class="profile-error-card">
      <h3>Subject Not Found</h3>
      <p>The requested curriculum subject could not be located in the database.</p>
      <button type="button" class="btn-primary" @click="goBack">Return to Subjects</button>
    </div>

    <!-- Loaded Subject Profile -->
    <div v-else class="profile-main-layout">
      <!-- Profile Hero Header -->
      <div class="profile-header-card">
        <div class="header-top-row">
          <div class="subject-identity-header">
            <div class="subject-badge-avatar">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
                <path d="M6 6h10" />
                <path d="M6 10h10" />
              </svg>
            </div>
            <div class="subject-title-group">
              <div class="name-status-row">
                <h1 class="profile-subject-name">{{ subjectProfile.name }}</h1>
                <SubjectStatusBadge :status="subjectProfile.status" size="sm" />
              </div>
              <div class="subject-metadata-strip">
                <span class="code-pill">{{ subjectProfile.code }}</span>
                <span class="meta-dot">·</span>
                <span class="dept-text">{{ subjectProfile.department || 'General Curriculum' }}</span>
              </div>
            </div>
          </div>

          <div class="profile-actions-toolbar">
            <button type="button" class="btn-secondary" @click="openEditModal">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
                <path d="m15 5 4 4" />
              </svg>
              <span>Edit Subject</span>
            </button>
            <button type="button" class="btn-primary" @click="openAssignClassModal">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
              </svg>
              <span>Assign Class</span>
            </button>
            <button type="button" class="btn-secondary" @click="openAssignTeacherModal">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
              </svg>
              <span>Assign Teacher</span>
            </button>
            <button
              type="button"
              class="btn-secondary"
              :title="subjectProfile.status === 'ACTIVE' ? 'Deactivate subject' : 'Activate subject'"
              @click="handleToggleStatus"
            >
              <svg v-if="subjectProfile.status === 'ACTIVE'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10" />
                <line x1="10" y1="15" x2="10" y2="9" />
                <line x1="14" y1="15" x2="14" y2="9" />
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10" />
                <polygon points="10 8 16 12 10 16 10 8" />
              </svg>
              <span>{{ subjectProfile.status === 'ACTIVE' ? 'Deactivate' : 'Activate' }}</span>
            </button>
          </div>
        </div>

        <!-- Metric Summary Strip -->
        <div class="profile-metrics-strip">
          <div class="metric-block" @click="activeTab = 'classes'">
            <span class="metric-num">{{ subjectProfile.classes?.length || 0 }}</span>
            <span class="metric-lbl">Assigned Classes</span>
          </div>
          <div class="metric-divider"></div>
          <div class="metric-block" @click="activeTab = 'teachers'">
            <span class="metric-num">{{ subjectProfile.teachers?.length || 0 }}</span>
            <span class="metric-lbl">Assigned Faculty</span>
          </div>
          <div class="metric-divider"></div>
          <div class="metric-block" @click="activeTab = 'timetable'">
            <span class="metric-num">{{ subjectProfile.timetables?.length || 0 }}</span>
            <span class="metric-lbl">Weekly Slots</span>
          </div>
          <div class="metric-divider"></div>
          <div class="metric-block" @click="activeTab = 'exams'">
            <span class="metric-num">{{ subjectProfile.exams?.length || 0 }}</span>
            <span class="metric-lbl">Scheduled Exams</span>
          </div>
        </div>
      </div>

      <!-- Profile Tabs Navigation (Horizontal on desktop, scrollable container on mobile) -->
      <div class="tabs-nav-container">
        <div class="tabs-scroll-strip">
          <button
            type="button"
            class="tab-btn"
            :class="{ active: activeTab === 'overview' }"
            @click="activeTab = 'overview'"
          >
            Overview
          </button>
          <button
            type="button"
            class="tab-btn"
            :class="{ active: activeTab === 'classes' }"
            @click="activeTab = 'classes'"
          >
            <span>Classes</span>
            <span class="tab-badge">{{ subjectProfile.classes?.length || 0 }}</span>
          </button>
          <button
            type="button"
            class="tab-btn"
            :class="{ active: activeTab === 'teachers' }"
            @click="activeTab = 'teachers'"
          >
            <span>Teachers</span>
            <span class="tab-badge">{{ subjectProfile.teachers?.length || 0 }}</span>
          </button>
          <button
            type="button"
            class="tab-btn"
            :class="{ active: activeTab === 'curriculum' }"
            @click="activeTab = 'curriculum'"
          >
            Curriculum
          </button>
          <button
            type="button"
            class="tab-btn"
            :class="{ active: activeTab === 'timetable' }"
            @click="activeTab = 'timetable'"
          >
            <span>Timetable</span>
            <span class="tab-badge">{{ subjectProfile.timetables?.length || 0 }}</span>
          </button>
          <button
            type="button"
            class="tab-btn"
            :class="{ active: activeTab === 'exams' }"
            @click="activeTab = 'exams'"
          >
            <span>Exams</span>
            <span class="tab-badge">{{ subjectProfile.exams?.length || 0 }}</span>
          </button>
        </div>
      </div>

      <!-- Tab Content Panes -->
      <div class="tab-content-container">
        <!-- TAB 1: OVERVIEW -->
        <div v-if="activeTab === 'overview'" class="tab-pane overview-pane">
          <div class="overview-grid">
            <!-- Curriculum Overview Card -->
            <div class="info-card">
              <div class="card-header">
                <h3 class="card-title">Subject & Curriculum Overview</h3>
              </div>
              <div class="card-body">
                <div class="detail-row">
                  <span class="detail-label">Subject Name:</span>
                  <span class="detail-value font-bold">{{ subjectProfile.name }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Code Identifier:</span>
                  <span class="detail-value">
                    <span class="code-pill">{{ subjectProfile.code }}</span>
                  </span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Academic Department:</span>
                  <span class="detail-value">{{ subjectProfile.department || 'General' }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Status:</span>
                  <span class="detail-value">
                    <SubjectStatusBadge :status="subjectProfile.status" size="sm" />
                  </span>
                </div>
                <div class="detail-row full-width">
                  <span class="detail-label">Curriculum Description / Learning Objectives:</span>
                  <div class="description-box">
                    {{ subjectProfile.description || 'No specific curriculum description entered yet. You can add syllabus and learning objectives via the Edit Subject action.' }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Quick Allocation Summary Card -->
            <div class="info-card">
              <div class="card-header">
                <h3 class="card-title">Academic Allocations</h3>
                <button type="button" class="card-action-btn" @click="openAssignClassModal">
                  + Assign Class
                </button>
              </div>
              <div class="card-body">
                <div class="metric-list">
                  <div class="metric-row">
                    <div class="metric-row-left">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
                      </svg>
                      <span>Assigned Classes</span>
                    </div>
                    <span class="metric-row-count">{{ subjectProfile.classes?.length || 0 }}</span>
                  </div>
                  <div class="metric-row">
                    <div class="metric-row-left">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                        <circle cx="9" cy="7" r="4" />
                      </svg>
                      <span>Assigned Faculty Teachers</span>
                    </div>
                    <span class="metric-row-count">{{ subjectProfile.teachers?.length || 0 }}</span>
                  </div>
                  <div class="metric-row">
                    <div class="metric-row-left">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect width="18" height="18" x="3" y="4" rx="2" ry="2" />
                        <line x1="16" x2="16" y1="2" y2="6" />
                        <line x1="8" x2="8" y1="2" y2="6" />
                        <line x1="3" x2="21" y1="10" y2="10" />
                      </svg>
                      <span>Timetable Slots</span>
                    </div>
                    <span class="metric-row-count">{{ subjectProfile.timetables?.length || 0 }}</span>
                  </div>
                  <div class="metric-row">
                    <div class="metric-row-left">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                        <polyline points="14 2 14 8 20 8" />
                        <line x1="16" x2="8" y1="13" y2="13" />
                        <line x1="16" x2="8" y1="17" y2="17" />
                        <polyline points="10 9 9 9 8 9" />
                      </svg>
                      <span>Assessments & Exams</span>
                    </div>
                    <span class="metric-row-count">{{ subjectProfile.exams?.length || 0 }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- TAB 2: CLASSES -->
        <div v-else-if="activeTab === 'classes'" class="tab-pane">
          <div class="pane-header">
            <h3 class="pane-title">Classes Assigned to this Subject</h3>
            <button type="button" class="btn-primary-sm" @click="openAssignClassModal">
              + Assign Class
            </button>
          </div>

          <div v-if="!subjectProfile.classes || subjectProfile.classes.length === 0" class="empty-tab-state">
            <p>No academic classes are currently assigned to this subject.</p>
            <button type="button" class="btn-primary" @click="openAssignClassModal">
              Assign to a Class
            </button>
          </div>

          <div v-else class="table-card">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Class Name</th>
                  <th>Academic Year</th>
                  <th>Assigned Teacher</th>
                  <th>Periods / Week</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="c in subjectProfile.classes" :key="c.id">
                  <td>
                    <div class="table-primary-text">{{ c.class_name }}</div>
                    <span class="code-pill-sm">{{ c.class_code }}</span>
                  </td>
                  <td>{{ c.academic_year }}</td>
                  <td>
                    <span v-if="c.teacher_name" class="teacher-link">{{ c.teacher_name }}</span>
                    <span v-else class="text-muted-italic">Unassigned</span>
                  </td>
                  <td>{{ c.periods_per_week ? `${c.periods_per_week} hrs/wk` : '-' }}</td>
                  <td>
                    <button
                      type="button"
                      class="btn-danger-icon"
                      title="Remove class allocation"
                      @click="confirmRemoveClass(c)"
                    >
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M3 6h18" />
                        <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
                        <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
                      </svg>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- TAB 3: TEACHERS -->
        <div v-else-if="activeTab === 'teachers'" class="tab-pane">
          <div class="pane-header">
            <h3 class="pane-title">Faculty Assigned to this Subject</h3>
            <button type="button" class="btn-primary-sm" @click="openAssignTeacherModal">
              + Assign Teacher
            </button>
          </div>

          <div v-if="!subjectProfile.teachers || subjectProfile.teachers.length === 0" class="empty-tab-state">
            <p>No teachers are currently assigned to teach this subject.</p>
            <button type="button" class="btn-primary" @click="openAssignTeacherModal">
              Assign Faculty Member
            </button>
          </div>

          <div v-else class="table-card">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Teacher</th>
                  <th>Assigned Class</th>
                  <th>Academic Year</th>
                  <th>Section</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="t in subjectProfile.teachers" :key="t.id">
                  <td>
                    <div class="table-primary-text">{{ t.full_name || t.teacher_name }}</div>
                    <div class="meta-subtext">{{ t.teacher_number || 'Faculty' }}</div>
                  </td>
                  <td>{{ t.class_name }}</td>
                  <td>{{ t.academic_year }}</td>
                  <td>{{ t.section || 'All' }}</td>
                  <td>
                    <button
                      type="button"
                      class="btn-danger-icon"
                      title="Remove teacher allocation"
                      @click="confirmRemoveTeacher(t)"
                    >
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M3 6h18" />
                        <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
                        <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
                      </svg>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- TAB 4: CURRICULUM -->
        <div v-else-if="activeTab === 'curriculum'" class="tab-pane">
          <div class="pane-header">
            <h3 class="pane-title">Curriculum & Learning Structure</h3>
          </div>

          <div class="curriculum-content-card">
            <div class="curriculum-section">
              <h4 class="curriculum-subtitle">Syllabus Overview & Description</h4>
              <div class="curriculum-text-body">
                {{ subjectProfile.description || 'Curriculum description and syllabus outlines are not yet configured for this subject. Use the Edit action to specify curriculum objectives.' }}
              </div>
            </div>

            <div class="curriculum-section">
              <h4 class="curriculum-subtitle">Learning Objectives & Course Modules</h4>
              <div class="info-alert">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="8" x2="12" y2="12" />
                  <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
                <span>Curriculum module management is currently organized at the academic subject level. Full interactive syllabus builder will connect to timetable term schedules.</span>
              </div>
            </div>
          </div>
        </div>

        <!-- TAB 5: TIMETABLE -->
        <div v-else-if="activeTab === 'timetable'" class="tab-pane">
          <div class="pane-header">
            <h3 class="pane-title">Weekly Timetable Schedule</h3>
          </div>

          <div v-if="!subjectProfile.timetables || subjectProfile.timetables.length === 0" class="empty-tab-state">
            <p>No active timetable schedule entries found for this subject.</p>
          </div>

          <div v-else class="table-card">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Day</th>
                  <th>Time Slot</th>
                  <th>Class</th>
                  <th>Teacher</th>
                  <th>Room</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="slot in subjectProfile.timetables" :key="slot.id">
                  <td><strong>{{ slot.day_of_week }}</strong></td>
                  <td>{{ slot.start_time }} - {{ slot.end_time }}</td>
                  <td>{{ slot.class_name }}</td>
                  <td>{{ slot.teacher_name || 'Assigned Staff' }}</td>
                  <td>{{ slot.room || 'Classroom' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- TAB 6: EXAMS -->
        <div v-else-if="activeTab === 'exams'" class="tab-pane">
          <div class="pane-header">
            <h3 class="pane-title">Scheduled Examinations & Assessments</h3>
          </div>

          <div v-if="!subjectProfile.exams || subjectProfile.exams.length === 0" class="empty-tab-state">
            <p>No examinations scheduled for this subject yet.</p>
          </div>

          <div v-else class="table-card">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Exam Title</th>
                  <th>Class</th>
                  <th>Term / Academic Year</th>
                  <th>Exam Date</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="exam in subjectProfile.exams" :key="exam.id">
                  <td><strong>{{ exam.exam_title || exam.name }}</strong></td>
                  <td>{{ exam.class_name }}</td>
                  <td>{{ exam.academic_year }} ({{ exam.exam_type }})</td>
                  <td>{{ exam.start_date || exam.exam_date || 'Date Pending' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <SubjectFormModal
      :is-open="isEditModalOpen"
      :is-editing="true"
      :subject="subjectProfile"
      :departments="departments"
      :is-submitting="isSubmittingEdit"
      @close="isEditModalOpen = false"
      @save="handleSaveEdit"
    />

    <SubjectAssignClassModal
      :is-open="isAssignClassModalOpen"
      :subject="subjectProfile"
      :is-submitting="isSubmittingAssignClass"
      @close="isAssignClassModalOpen = false"
      @assign="handleAssignClass"
    />

    <SubjectAssignTeacherModal
      :is-open="isAssignTeacherModalOpen"
      :subject="subjectProfile"
      :is-submitting="isSubmittingAssignTeacher"
      @close="isAssignTeacherModalOpen = false"
      @assign="handleAssignTeacher"
    />

    <SubjectConfirmDialog
      :is-open="isConfirmDialogOpen"
      :title="confirmConfig.title"
      :message="confirmConfig.message"
      :confirm-label="confirmConfig.confirmLabel"
      :confirm-variant="confirmConfig.variant"
      :is-submitting="isSubmittingConfirm"
      @close="isConfirmDialogOpen = false"
      @confirm="confirmConfig.action"
    />
  </div>
</template>

<style scoped>
.subject-profile-container {
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

/* Back Link */
.navigation-bar {
  display: flex;
  align-items: center;
}

.back-link-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  background: none;
  border: none;
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  border-radius: 0.375rem;
  transition: all 0.15s ease;
}

.back-link-btn:hover {
  color: var(--brand-primary, #1e40af);
  background: #eff6ff;
}

.back-link-btn svg {
  width: 1rem;
  height: 1rem;
}

/* Profile Main Layout */
.profile-main-layout {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* Header Card */
.profile-header-card {
  background: #ffffff;
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: var(--radius-lg, 0.75rem);
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  box-sizing: border-box;
}

.header-top-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.subject-identity-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  min-width: 0;
}

.subject-badge-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 3rem;
  height: 3rem;
  border-radius: var(--radius-md, 0.5rem);
  background: #eff6ff;
  color: var(--brand-primary, #1e40af);
  flex-shrink: 0;
}

.subject-badge-avatar svg {
  width: 1.5rem;
  height: 1.5rem;
}

.subject-title-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  min-width: 0;
}

.name-status-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.profile-subject-name {
  font-size: 1.5rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
  letter-spacing: -0.025em;
  word-break: break-word;
}

.subject-metadata-strip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  font-size: 0.8125rem;
  color: #64748b;
}

.code-pill {
  display: inline-flex;
  align-items: center;
  padding: 0.15rem 0.5rem;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 0.25rem;
  font-family: monospace;
  font-weight: 700;
  color: #334155;
  font-size: 0.75rem;
}

.meta-dot {
  color: #cbd5e1;
}

.dept-text {
  font-weight: 500;
}

/* Toolbar Buttons */
.profile-actions-toolbar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-primary,
.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  height: 2.25rem;
  padding: 0 0.875rem;
  font-size: 0.8125rem;
  font-weight: 600;
  border-radius: var(--radius-md, 0.5rem);
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.btn-primary {
  color: #ffffff;
  background: var(--brand-primary, #1e40af);
  border: none;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-secondary {
  color: #334155;
  background: #ffffff;
  border: 1px solid #cbd5e1;
}

.btn-secondary:hover {
  background: #f8fafc;
  border-color: #94a3b8;
}

.btn-primary svg,
.btn-secondary svg {
  width: 0.875rem;
  height: 0.875rem;
}

/* Metric Strip */
.profile-metrics-strip {
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 0.875rem 1rem;
  background: #f8fafc;
  border: 1px solid #f1f5f9;
  border-radius: var(--radius-md, 0.5rem);
  flex-wrap: wrap;
  gap: 0.75rem;
}

.metric-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: transform 0.12s ease;
  padding: 0.25rem 0.5rem;
}

.metric-block:hover {
  transform: translateY(-2px);
}

.metric-num {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--brand-primary, #1e40af);
  line-height: 1.2;
}

.metric-lbl {
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
}

.metric-divider {
  width: 1px;
  height: 2rem;
  background: #e2e8f0;
}

/* Tabs Navigation */
.tabs-nav-container {
  width: 100%;
  border-bottom: 1px solid var(--border-color, #e2e8f0);
}

.tabs-scroll-strip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  padding-bottom: -1px;
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.625rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.tab-btn:hover {
  color: var(--brand-primary, #1e40af);
}

.tab-btn.active {
  color: var(--brand-primary, #1e40af);
  border-bottom-color: var(--brand-primary, #1e40af);
}

.tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.1rem 0.4rem;
  font-size: 0.6875rem;
  font-weight: 700;
  background: #f1f5f9;
  border-radius: 9999px;
  color: #475569;
}

.tab-btn.active .tab-badge {
  background: #eff6ff;
  color: var(--brand-primary, #1e40af);
}

/* Panes */
.tab-content-container {
  width: 100%;
}

.tab-pane {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  animation: fadeIn 0.15s ease-out;
}

.overview-grid {
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: 1.25rem;
}

.info-card {
  background: #ffffff;
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: var(--radius-lg, 0.75rem);
  padding: 1.25rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #f1f5f9;
}

.card-title {
  font-size: 0.9375rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.card-action-btn {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--brand-primary, #1e40af);
  background: none;
  border: none;
  cursor: pointer;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detail-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  font-size: 0.8125rem;
}

.detail-row.full-width {
  flex-direction: column;
  align-items: flex-start;
  gap: 0.375rem;
}

.detail-label {
  color: #64748b;
  font-weight: 500;
}

.detail-value {
  color: #0f172a;
}

.font-bold {
  font-weight: 700;
}

.description-box {
  width: 100%;
  padding: 0.75rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  color: #334155;
  line-height: 1.5;
  box-sizing: border-box;
}

.metric-list {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.metric-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.625rem 0.75rem;
  background: #f8fafc;
  border: 1px solid #f1f5f9;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
}

.metric-row-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #334155;
  font-weight: 500;
}

.metric-row-left svg {
  width: 1rem;
  height: 1rem;
  color: #64748b;
}

.metric-row-count {
  font-weight: 700;
  color: var(--brand-primary, #1e40af);
}

.pane-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.pane-title {
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.btn-primary-sm {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  height: 2rem;
  padding: 0 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #ffffff;
  background: var(--brand-primary, #1e40af);
  border: none;
  border-radius: var(--radius-md, 0.5rem);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-primary-sm:hover {
  background: #1d4ed8;
}

.empty-tab-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 3rem 1rem;
  background: #ffffff;
  border: 1px dashed #cbd5e1;
  border-radius: 0.75rem;
  text-align: center;
  color: #64748b;
  font-size: 0.875rem;
}

.table-card {
  background: #ffffff;
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: var(--radius-lg, 0.75rem);
  overflow-x: auto;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.data-table {
  width: 100%;
  min-width: 660px;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.8125rem;
}

.data-table thead tr {
  background: #f8fafc;
  border-bottom: 1px solid var(--border-color, #e2e8f0);
}

.data-table th {
  padding: 0.75rem 1rem;
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
  white-space: nowrap;
}

.data-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
  color: #1e293b;
}

.table-primary-text {
  font-weight: 600;
  color: #0f172a;
}

.code-pill-sm {
  font-family: monospace;
  font-size: 0.6875rem;
  color: #64748b;
}

.meta-subtext {
  font-size: 0.6875rem;
  color: #64748b;
}

.teacher-link {
  font-weight: 500;
  color: #1e40af;
}

.text-muted-italic {
  color: #94a3b8;
  font-style: italic;
}

.btn-danger-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  background: none;
  border: 1px solid transparent;
  color: #dc2626;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-danger-icon:hover {
  background: #fef2f2;
  border-color: #fecaca;
}

.btn-danger-icon svg {
  width: 0.875rem;
  height: 0.875rem;
}

/* Curriculum Card */
.curriculum-content-card {
  background: #ffffff;
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: var(--radius-lg, 0.75rem);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.curriculum-subtitle {
  font-size: 0.875rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.5rem 0;
}

.curriculum-text-body {
  font-size: 0.875rem;
  color: #334155;
  line-height: 1.6;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  padding: 1rem;
}

.info-alert {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  color: #1e40af;
}

.info-alert svg {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

/* Responsive */
@media (max-width: 912px) {
  .overview-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .header-top-row {
    flex-direction: column;
    align-items: stretch;
  }

  .profile-actions-toolbar {
    width: 100%;
  }

  .profile-actions-toolbar button {
    flex: 1;
    justify-content: center;
  }

  .metric-divider {
    display: none;
  }

  .profile-metrics-strip {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
