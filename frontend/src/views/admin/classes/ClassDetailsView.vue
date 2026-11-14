<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { classService } from '../../../services/classService';
import {
  ClassFullProfile,
  ClassEnrollmentStudent,
  ClassTeacherAssignmentItem
} from '../../../types/school';

import ClassStatusBadge from './components/ClassStatusBadge.vue';
import ClassCapacityBar from './components/ClassCapacityBar.vue';
import ClassFormModal from './components/ClassFormModal.vue';
import ClassEnrollStudentModal from './components/ClassEnrollStudentModal.vue';
import ClassAssignTeacherModal from './components/ClassAssignTeacherModal.vue';
import ClassConfirmDialog from './components/ClassConfirmDialog.vue';
import ClassSkeleton from './components/ClassSkeleton.vue';

const route = useRoute();
const router = useRouter();

const classId = computed(() => Number(route.params.id));
const classProfile = ref<ClassFullProfile | null>(null);
const isLoading = ref(true);
const errorMessage = ref('');
const successMessage = ref('');

// Active Tab
const activeTab = ref<'overview' | 'students' | 'teachers' | 'subjects' | 'timetable' | 'exams'>('overview');

// Modals
const isEditModalOpen = ref(false);
const isSubmittingEdit = ref(false);

const isEnrollModalOpen = ref(false);
const isSubmittingEnroll = ref(false);

const isAssignModalOpen = ref(false);
const isSubmittingAssign = ref(false);

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
  if (!classId.value || isNaN(classId.value)) {
    errorMessage.value = 'Invalid class identifier.';
    isLoading.value = false;
    return;
  }

  isLoading.value = true;
  errorMessage.value = '';
  try {
    const data = await classService.getFullProfile(classId.value);
    classProfile.value = data;
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to load class profile from database.';
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  loadProfile();
});

function goBack() {
  router.push('/admin/classes');
}

// Actions
function openEditModal() {
  isEditModalOpen.value = true;
}

async function handleSaveEdit(payload: any) {
  if (!classProfile.value) return;
  isSubmittingEdit.value = true;
  try {
    await classService.updateClass(classProfile.value.id, payload);
    successMessage.value = 'Class details updated successfully.';
    isEditModalOpen.value = false;
    loadProfile();
    setTimeout(() => { successMessage.value = ''; }, 4000);
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to update class.';
  } finally {
    isSubmittingEdit.value = false;
  }
}

function openEnrollModal() {
  isEnrollModalOpen.value = true;
}

async function handleEnrollStudent(payload: { studentId: number; academicYear: string; enrollmentDate?: string }) {
  if (!classProfile.value) return;
  isSubmittingEnroll.value = true;
  try {
    await classService.enrollStudent(
      classProfile.value.id,
      payload.studentId,
      payload.academicYear,
      payload.enrollmentDate
    );
    successMessage.value = 'Student enrolled successfully.';
    isEnrollModalOpen.value = false;
    loadProfile();
    setTimeout(() => { successMessage.value = ''; }, 4000);
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to enroll student.';
  } finally {
    isSubmittingEnroll.value = false;
  }
}

function confirmRemoveStudent(student: ClassEnrollmentStudent) {
  confirmConfig.value = {
    title: 'Remove Student from Class',
    message: `Are you sure you want to remove ${student.full_name} (${student.admission_number}) from ${classProfile.value?.name}? Historical grades and attendance will be preserved.`,
    confirmLabel: 'Remove Student',
    variant: 'danger',
    action: async () => {
      isSubmittingConfirm.value = true;
      try {
        await classService.removeStudent(classProfile.value!.id, student.student_id);
        successMessage.value = `${student.full_name} removed from class enrollment.`;
        isConfirmDialogOpen.value = false;
        loadProfile();
        setTimeout(() => { successMessage.value = ''; }, 4000);
      } catch (err: any) {
        errorMessage.value = err.response?.data?.detail || 'Failed to remove student.';
      } finally {
        isSubmittingConfirm.value = false;
      }
    },
  };
  isConfirmDialogOpen.value = true;
}

function openAssignTeacherModal() {
  isAssignModalOpen.value = true;
}

async function handleAssignTeacher(payload: { teacher_id: number; subject_id: number; academic_year: string }) {
  if (!classProfile.value) return;
  isSubmittingAssign.value = true;
  try {
    await classService.assignTeacher(classProfile.value.id, payload);
    successMessage.value = 'Teacher and subject assigned successfully.';
    isAssignModalOpen.value = false;
    loadProfile();
    setTimeout(() => { successMessage.value = ''; }, 4000);
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to assign teacher.';
  } finally {
    isSubmittingAssign.value = false;
  }
}

function confirmRemoveTeacher(assignment: ClassTeacherAssignmentItem) {
  confirmConfig.value = {
    title: 'Remove Teacher Assignment',
    message: `Remove ${assignment.full_name} from teaching ${assignment.subject_name} for this class?`,
    confirmLabel: 'Remove Assignment',
    variant: 'danger',
    action: async () => {
      isSubmittingConfirm.value = true;
      try {
        await classService.removeTeacher(classProfile.value!.id, assignment.id);
        successMessage.value = 'Teacher assignment removed successfully.';
        isConfirmDialogOpen.value = false;
        loadProfile();
        setTimeout(() => { successMessage.value = ''; }, 4000);
      } catch (err: any) {
        errorMessage.value = err.response?.data?.detail || 'Failed to remove teacher.';
      } finally {
        isSubmittingConfirm.value = false;
      }
    },
  };
  isConfirmDialogOpen.value = true;
}

function handleToggleStatus() {
  if (!classProfile.value) return;
  const isDeactivating = classProfile.value.status === 'ACTIVE';
  confirmConfig.value = {
    title: isDeactivating ? 'Deactivate Class' : 'Activate Class',
    message: isDeactivating
      ? `Are you sure you want to deactivate ${classProfile.value.name}? Active enrollments and timetables will be suspended.`
      : `Activate ${classProfile.value.name} to reopen enrollments and scheduling?`,
    confirmLabel: isDeactivating ? 'Deactivate' : 'Activate',
    variant: isDeactivating ? 'danger' : 'primary',
    action: async () => {
      isSubmittingConfirm.value = true;
      try {
        await classService.updateStatus(classProfile.value!.id, isDeactivating ? 'INACTIVE' : 'ACTIVE');
        successMessage.value = `Class marked as ${isDeactivating ? 'INACTIVE' : 'ACTIVE'}.`;
        isConfirmDialogOpen.value = false;
        loadProfile();
        setTimeout(() => { successMessage.value = ''; }, 4000);
      } catch (err: any) {
        errorMessage.value = err.response?.data?.detail || 'Failed to update status.';
      } finally {
        isSubmittingConfirm.value = false;
      }
    },
  };
  isConfirmDialogOpen.value = true;
}
</script>

<template>
  <div class="profile-container">
    <!-- Back Navigation -->
    <div class="back-nav-bar">
      <button type="button" class="back-link-btn" @click="goBack">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="m15 18-6-6 6-6" />
        </svg>
        <span class="desktop-text">Back to Classes</span>
        <span class="mobile-text">Classes</span>
      </button>
    </div>

    <!-- Alert Messages -->
    <div v-if="errorMessage" class="alert-banner alert-danger">
      <span>{{ errorMessage }}</span>
      <button type="button" class="alert-close" @click="errorMessage = ''">×</button>
    </div>

    <div v-if="successMessage" class="alert-banner alert-success">
      <span>{{ successMessage }}</span>
      <button type="button" class="alert-close" @click="successMessage = ''">×</button>
    </div>

    <!-- Loading Skeleton -->
    <div v-if="isLoading" class="skeleton-wrapper">
      <ClassSkeleton :rows="6" />
    </div>

    <!-- Profile Content -->
    <template v-else-if="classProfile">
      <!-- Hero Header Card -->
      <div class="hero-card">
        <div class="hero-main">
          <div class="hero-avatar">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
              <path d="M6 6h10" />
              <path d="M6 10h10" />
            </svg>
          </div>

          <div class="hero-identity">
            <div class="hero-title-row">
              <h1 class="hero-class-name">{{ classProfile.name }}</h1>
              <div class="hero-badges">
                <ClassStatusBadge :status="classProfile.status" />
                <ClassStatusBadge :capacity-status="classProfile.capacity_metrics?.capacity_status" type="capacity" />
                <span
                  class="division-pill"
                  :class="classProfile.division?.toUpperCase() === 'SECONDARY' ? 'pill-secondary' : 'pill-primary'"
                >
                  {{ classProfile.division || 'PRIMARY' }}
                </span>
              </div>
            </div>

            <div class="hero-meta-row">
              <div class="hero-meta-code-section">
                <span class="hero-code-badge">{{ classProfile.code }}</span>
                <span v-if="classProfile.section" class="hero-meta-item">Section: <strong>{{ classProfile.section }}</strong></span>
              </div>
              <div class="hero-meta-academic-year">
                <span class="hero-meta-item">Academic Year: <strong>{{ classProfile.academic_year }}</strong></span>
              </div>
              <div class="hero-meta-capacity">
                <span class="hero-meta-item">Max Capacity: <strong>{{ classProfile.capacity }} Students</strong></span>
              </div>
            </div>
          </div>
        </div>

        <!-- Hero Actions Container -->
        <div class="hero-actions">
          <!-- Primary Action Button -->
          <button type="button" class="btn-action btn-primary" @click="openEnrollModal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M19 8v6m3-3h-6" />
            </svg>
            <span>Enroll Student</span>
          </button>

          <!-- Secondary Actions Group (2-column pair on mobile) -->
          <div class="hero-secondary-actions">
            <button type="button" class="btn-action btn-outline" @click="openEditModal">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
                <path d="m15 5 4 4" />
              </svg>
              <span>Edit Class</span>
            </button>

            <button type="button" class="btn-action btn-outline" @click="openAssignTeacherModal">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
                <path d="M12 6v6m3-3H9" />
              </svg>
              <span>Assign Teacher</span>
            </button>
          </div>

          <!-- Status Toggle Action (Full-width on mobile) -->
          <button
            type="button"
            class="btn-action btn-status-toggle"
            :class="classProfile.status === 'ACTIVE' ? 'btn-danger-outline' : 'btn-success-outline'"
            @click="handleToggleStatus"
          >
            <svg v-if="classProfile.status === 'ACTIVE'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" />
              <path d="m15 9-6 6m0-6 6 6" />
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" />
              <path d="m9 12 2 2 4-4" />
            </svg>
            <span>{{ classProfile.status === 'ACTIVE' ? 'Deactivate' : 'Activate' }}</span>
          </button>
        </div>
      </div>

      <!-- Quick Metrics Strip -->
      <div class="metrics-strip">
        <!-- Enrolled / Capacity -->
        <div class="metric-card">
          <span class="metric-card-label">ENROLLMENT & CAPACITY</span>
          <div class="metric-capacity-body">
            <div class="metric-big-num">
              <strong>{{ classProfile.capacity_metrics?.enrolled ?? 0 }}</strong>
              <span class="denom">/ {{ classProfile.capacity }}</span>
            </div>
            <span class="metric-badge-pct">
              {{ classProfile.capacity_metrics?.utilization_rate ?? 0 }}% Enrolled
            </span>
          </div>
          <div class="mini-bar-wrap">
            <ClassCapacityBar
              :enrolled="classProfile.capacity_metrics?.enrolled ?? 0"
              :capacity="classProfile.capacity"
              :compact="true"
              :show-label="false"
            />
          </div>
        </div>

        <!-- Available Seats -->
        <div class="metric-card">
          <span class="metric-card-label">AVAILABLE SEATS</span>
          <div class="metric-big-num">
            <strong>{{ classProfile.capacity_metrics?.available_seats ?? 0 }}</strong>
            <span class="denom">Seats Left</span>
          </div>
          <span class="metric-sub-note">Max room capacity: {{ classProfile.capacity }}</span>
        </div>

        <!-- Assigned Faculty -->
        <div class="metric-card">
          <span class="metric-card-label">ASSIGNED FACULTY</span>
          <div class="metric-big-num">
            <strong>{{ classProfile.teachers_count ?? classProfile.teachers?.length ?? 0 }}</strong>
            <span class="denom">Teachers</span>
          </div>
          <span class="metric-sub-note">{{ classProfile.subjects?.length ?? 0 }} Subject Pairings</span>
        </div>

        <!-- Weekly Schedule -->
        <div class="metric-card">
          <span class="metric-card-label">SCHEDULED PERIODS</span>
          <div class="metric-big-num">
            <strong>{{ classProfile.timetables?.length ?? 0 }}</strong>
            <span class="denom">Periods / Wk</span>
          </div>
          <span class="metric-sub-note">{{ classProfile.exams?.length ?? 0 }} Upcoming/Past Exams</span>
        </div>
      </div>

      <!-- Tab Navigation -->
      <div class="tab-nav-container">
        <div class="tab-nav-strip">
          <button
            type="button"
            class="tab-btn"
            :class="{ 'is-active': activeTab === 'overview' }"
            @click="activeTab = 'overview'"
          >
            Overview
          </button>
          <button
            type="button"
            class="tab-btn"
            :class="{ 'is-active': activeTab === 'students' }"
            @click="activeTab = 'students'"
          >
            Students ({{ classProfile.students?.length ?? 0 }})
          </button>
          <button
            type="button"
            class="tab-btn"
            :class="{ 'is-active': activeTab === 'teachers' }"
            @click="activeTab = 'teachers'"
          >
            Teachers ({{ classProfile.teachers?.length ?? 0 }})
          </button>
          <button
            type="button"
            class="tab-btn"
            :class="{ 'is-active': activeTab === 'subjects' }"
            @click="activeTab = 'subjects'"
          >
            Subjects ({{ classProfile.subjects?.length ?? 0 }})
          </button>
          <button
            type="button"
            class="tab-btn"
            :class="{ 'is-active': activeTab === 'timetable' }"
            @click="activeTab = 'timetable'"
          >
            Timetable ({{ classProfile.timetables?.length ?? 0 }})
          </button>
          <button
            type="button"
            class="tab-btn"
            :class="{ 'is-active': activeTab === 'exams' }"
            @click="activeTab = 'exams'"
          >
            Exams ({{ classProfile.exams?.length ?? 0 }})
          </button>
        </div>
      </div>

      <!-- Tab Content Area -->
      <div class="tab-pane-container">
        <!-- 1. OVERVIEW TAB -->
        <div v-if="activeTab === 'overview'" class="overview-pane">
          <div class="overview-grid">
            <!-- Left Column: Specs -->
            <div class="pane-card">
              <h3 class="pane-card-title">Class Specifications</h3>
              <div class="spec-list">
                <div class="spec-item">
                  <span class="spec-label">Class Name:</span>
                  <span class="spec-value">{{ classProfile.name }}</span>
                </div>
                <div class="spec-item">
                  <span class="spec-label">Class Code:</span>
                  <span class="spec-value code-pill">{{ classProfile.code }}</span>
                </div>
                <div class="spec-item">
                  <span class="spec-label">Section / Stream:</span>
                  <span class="spec-value">{{ classProfile.section || 'None' }}</span>
                </div>
                <div class="spec-item">
                  <span class="spec-label">Academic Year:</span>
                  <span class="spec-value">{{ classProfile.academic_year }}</span>
                </div>
                <div class="spec-item">
                  <span class="spec-label">Classroom Capacity:</span>
                  <span class="spec-value">{{ classProfile.capacity }} Students</span>
                </div>
                <div class="spec-item">
                  <span class="spec-label">Enrollment Status:</span>
                  <ClassStatusBadge :capacity-status="classProfile.capacity_metrics?.capacity_status" type="capacity" />
                </div>
                <div v-if="classProfile.description" class="spec-item">
                  <span class="spec-label">Description / Notes:</span>
                  <span class="spec-value">{{ classProfile.description }}</span>
                </div>
              </div>
            </div>

            <!-- Right Column: Teachers & Schedule Summary -->
            <div class="pane-card">
              <div class="pane-card-header">
                <h3 class="pane-card-title">Assigned Teachers Roster</h3>
                <button type="button" class="link-btn" @click="activeTab = 'teachers'">View all</button>
              </div>

              <div v-if="classProfile.teachers && classProfile.teachers.length > 0" class="mini-teacher-list">
                <div v-for="t in classProfile.teachers" :key="t.id" class="mini-teacher-item">
                  <div class="mini-t-avatar">
                    {{ t.full_name ? (t.full_name[0] || 'T') : 'T' }}
                  </div>
                  <div class="mini-t-info">
                    <span class="mini-t-name">{{ t.full_name }}</span>
                    <span class="mini-t-sub">{{ t.subject_name }} ({{ t.subject_code }})</span>
                  </div>
                  <span class="mini-t-id">{{ t.teacher_number }}</span>
                </div>
              </div>
              <div v-else class="empty-tab-sub">
                No faculty members assigned yet.
              </div>
            </div>
          </div>
        </div>

        <!-- 2. STUDENTS TAB -->
        <div v-if="activeTab === 'students'" class="students-pane">
          <div class="tab-action-bar">
            <span class="action-bar-title">Enrolled Students ({{ classProfile.students?.length ?? 0 }})</span>
            <button type="button" class="btn-primary-sm" @click="openEnrollModal">
              + Enroll Student
            </button>
          </div>

          <div v-if="classProfile.students && classProfile.students.length > 0" class="table-card">
            <div class="table-responsive">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Student Name</th>
                    <th>Admission #</th>
                    <th>Gender</th>
                    <th>Portal Access</th>
                    <th>Enrollment Date</th>
                    <th>Status</th>
                    <th style="text-align: right;">Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="s in classProfile.students" :key="s.id">
                    <td>
                      <div class="student-cell">
                        <div class="st-avatar">{{ s.full_name[0] || 'S' }}</div>
                        <span class="st-name">{{ s.full_name }}</span>
                      </div>
                    </td>
                    <td><span class="code-pill">{{ s.admission_number }}</span></td>
                    <td>{{ s.gender }}</td>
                    <td>
                      <span v-if="s.has_portal_access" class="portal-tag tag-enabled">Enabled</span>
                      <span v-else class="portal-tag tag-none">Not created</span>
                    </td>
                    <td>{{ s.enrollment_date }}</td>
                    <td>
                      <span class="status-badge badge-success">
                        <span class="status-dot dot-success"></span>
                        {{ s.status }}
                      </span>
                    </td>
                    <td style="text-align: right;">
                      <button
                        type="button"
                        class="btn-remove-sm"
                        title="Remove student from class"
                        @click="confirmRemoveStudent(s)"
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div v-else class="empty-state-tab">
            <p>No students enrolled in this class yet.</p>
            <button type="button" class="btn-primary-sm" @click="openEnrollModal">Enroll First Student</button>
          </div>
        </div>

        <!-- 3. TEACHERS TAB -->
        <div v-if="activeTab === 'teachers'" class="teachers-pane">
          <div class="tab-action-bar">
            <span class="action-bar-title">Faculty Allocations ({{ classProfile.teachers?.length ?? 0 }})</span>
            <button type="button" class="btn-primary-sm" @click="openAssignTeacherModal">
              + Assign Teacher & Subject
            </button>
          </div>

          <div v-if="classProfile.teachers && classProfile.teachers.length > 0" class="table-card">
            <div class="table-responsive">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Teacher Name</th>
                    <th>Teacher ID</th>
                    <th>Subject Assigned</th>
                    <th>Subject Code</th>
                    <th>Academic Year</th>
                    <th>Status</th>
                    <th style="text-align: right;">Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="t in classProfile.teachers" :key="t.id">
                    <td>
                      <div class="student-cell">
                        <div class="st-avatar bg-indigo">{{ t.full_name[0] || 'T' }}</div>
                        <span class="st-name">{{ t.full_name }}</span>
                      </div>
                    </td>
                    <td><span class="code-pill">{{ t.teacher_number }}</span></td>
                    <td><strong>{{ t.subject_name }}</strong></td>
                    <td>{{ t.subject_code }}</td>
                    <td>{{ t.academic_year }}</td>
                    <td>
                      <span class="status-badge badge-success">
                        <span class="status-dot dot-success"></span>
                        Active
                      </span>
                    </td>
                    <td style="text-align: right;">
                      <button
                        type="button"
                        class="btn-remove-sm"
                        title="Remove teacher assignment"
                        @click="confirmRemoveTeacher(t)"
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div v-else class="empty-state-tab">
            <p>No teachers assigned to this class yet.</p>
            <button type="button" class="btn-primary-sm" @click="openAssignTeacherModal">Assign Teacher</button>
          </div>
        </div>

        <!-- 4. SUBJECTS TAB -->
        <div v-if="activeTab === 'subjects'" class="subjects-pane">
          <div class="tab-action-bar">
            <span class="action-bar-title">Subjects Taught ({{ classProfile.subjects?.length ?? 0 }})</span>
          </div>

          <div v-if="classProfile.subjects && classProfile.subjects.length > 0" class="cards-grid">
            <div v-for="sub in classProfile.subjects" :key="sub.id" class="subject-card">
              <div class="sub-header">
                <span class="sub-code">{{ sub.code }}</span>
                <span class="sub-dept">{{ sub.department || 'Academic' }}</span>
              </div>
              <h4 class="sub-name">{{ sub.name }}</h4>
              <div class="sub-teacher">
                <span class="sub-teacher-label">Assigned Teacher:</span>
                <span class="sub-teacher-val">{{ sub.teacher_name || 'Unassigned' }}</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-state-tab">
            <p>No subjects actively paired with this class yet.</p>
          </div>
        </div>

        <!-- 5. TIMETABLE TAB -->
        <div v-if="activeTab === 'timetable'" class="timetable-pane">
          <div class="tab-action-bar">
            <span class="action-bar-title">Weekly Schedule ({{ classProfile.timetables?.length ?? 0 }} periods)</span>
          </div>

          <div v-if="classProfile.timetables && classProfile.timetables.length > 0" class="table-card">
            <div class="table-responsive">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Day of Week</th>
                    <th>Time Window</th>
                    <th>Subject</th>
                    <th>Assigned Teacher</th>
                    <th>Room / Classroom</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="slot in classProfile.timetables" :key="slot.id">
                    <td><strong>{{ slot.day_of_week }}</strong></td>
                    <td>{{ slot.start_time }} – {{ slot.end_time }}</td>
                    <td><strong>{{ slot.subject_name }}</strong> ({{ slot.subject_code }})</td>
                    <td>{{ slot.teacher_name || 'No teacher assigned' }}</td>
                    <td>{{ slot.room || 'Standard Classroom' }}</td>
                    <td>
                      <span class="status-badge badge-success">
                        <span class="status-dot dot-success"></span>
                        Active
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div v-else class="empty-state-tab">
            <p>No weekly schedule periods mapped to this class yet.</p>
          </div>
        </div>

        <!-- 6. EXAMS TAB -->
        <div v-if="activeTab === 'exams'" class="exams-pane">
          <div class="tab-action-bar">
            <span class="action-bar-title">Examinations & Assessments ({{ classProfile.exams?.length ?? 0 }})</span>
          </div>

          <div v-if="classProfile.exams && classProfile.exams.length > 0" class="table-card">
            <div class="table-responsive">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Exam Name</th>
                    <th>Type</th>
                    <th>Academic Year</th>
                    <th>Date</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="ex in classProfile.exams" :key="ex.id">
                    <td><strong>{{ ex.name }}</strong></td>
                    <td>{{ ex.exam_type }}</td>
                    <td>{{ ex.academic_year }}</td>
                    <td>{{ ex.start_date || 'TBD' }}</td>
                    <td>
                      <span class="status-badge badge-indigo">
                        <span class="status-dot dot-indigo"></span>
                        {{ ex.status }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div v-else class="empty-state-tab">
            <p>No examinations scheduled for this class.</p>
          </div>
        </div>
      </div>
    </template>

    <!-- Modals -->
    <ClassFormModal
      :is-open="isEditModalOpen"
      :is-editing="true"
      :school-class="classProfile"
      :is-submitting="isSubmittingEdit"
      :years="['2026/2027']"
      @close="isEditModalOpen = false"
      @save="handleSaveEdit"
    />

    <ClassEnrollStudentModal
      :is-open="isEnrollModalOpen"
      :school-class="classProfile"
      :is-submitting="isSubmittingEnroll"
      :years="['2026/2027']"
      @close="isEnrollModalOpen = false"
      @enroll="handleEnrollStudent"
    />

    <ClassAssignTeacherModal
      :is-open="isAssignModalOpen"
      :school-class="classProfile"
      :is-submitting="isSubmittingAssign"
      :years="['2026/2027']"
      @close="isAssignModalOpen = false"
      @assign="handleAssignTeacher"
    />

    <ClassConfirmDialog
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
.profile-container {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

/* Back Nav */
.back-nav-bar {
  display: flex;
  align-items: center;
}

.back-link-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: transparent;
  border: none;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  transition: all 0.15s ease;
}

.back-link-btn:hover {
  background-color: #f1f5f9;
  color: #0f172a;
}

.back-link-btn svg {
  width: 1rem;
  height: 1rem;
}

.mobile-text {
  display: none;
}

@media (max-width: 640px) {
  .desktop-text { display: none; }
  .mobile-text { display: inline; }
}

/* Hero Card */
.hero-card {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 0.875rem;
  padding: 1.25rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.25rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04);
}

.hero-main {
  display: flex;
  align-items: center;
  gap: 1rem;
  min-width: 0;
  flex: 1;
}

.hero-avatar {
  width: 3.25rem;
  height: 3.25rem;
  border-radius: 0.75rem;
  background-color: #eff6ff;
  color: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1px solid #dbeafe;
}

.hero-avatar svg {
  width: 1.625rem;
  height: 1.625rem;
}

.hero-identity {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  min-width: 0;
}

.hero-title-row {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  flex-wrap: wrap;
}

.hero-class-name {
  font-size: 1.375rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
  letter-spacing: -0.01em;
  line-height: 1.2;
}

.hero-badges {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  flex-wrap: wrap;
}

.division-pill {
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  line-height: 1.2;
}

.pill-primary {
  background-color: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
}

.pill-secondary {
  background-color: #fdf4ff;
  color: #9333ea;
  border: 1px solid #f5d0fe;
}

.hero-meta-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.8125rem;
  color: #64748b;
  flex-wrap: wrap;
}

.hero-meta-code-section {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.hero-meta-academic-year,
.hero-meta-capacity {
  display: inline-flex;
  align-items: center;
}

.hero-code-badge {
  font-size: 0.75rem;
  font-weight: 700;
  background-color: #f1f5f9;
  color: #334155;
  padding: 0.15rem 0.45rem;
  border-radius: 0.25rem;
  border: 1px solid #e2e8f0;
}

.hero-meta-item {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.hero-meta-item strong {
  color: #1e293b;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.hero-secondary-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  height: 2.25rem;
  padding: 0 0.875rem;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.btn-action svg {
  width: 0.95rem;
  height: 0.95rem;
  flex-shrink: 0;
}

.btn-primary {
  background-color: #2563eb;
  border: 1px solid transparent;
  color: #ffffff;
}

.btn-primary:hover {
  background-color: #1d4ed8;
}

.btn-outline {
  background-color: #ffffff;
  border: 1px solid #cbd5e1;
  color: #334155;
}

.btn-outline:hover {
  background-color: #f8fafc;
  color: #0f172a;
}

.btn-danger-outline {
  background-color: #ffffff;
  border: 1px solid #fecaca;
  color: #dc2626;
}

.btn-danger-outline:hover {
  background-color: #fef2f2;
}

.btn-success-outline {
  background-color: #ffffff;
  border: 1px solid #bbf7d0;
  color: #16a34a;
}

.btn-success-outline:hover {
  background-color: #f0fdf4;
}

/* Metrics Strip */
.metrics-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

.metric-card {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1rem 1.125rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
}

.metric-card-label {
  font-size: 0.6875rem;
  font-weight: 600;
  color: #64748b;
  letter-spacing: 0.04em;
}

.metric-capacity-body {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.5rem;
}

.metric-big-num {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
}

.denom {
  font-size: 0.8125rem;
  font-weight: 500;
  color: #64748b;
}

.metric-badge-pct {
  font-size: 0.75rem;
  font-weight: 600;
  color: #2563eb;
}

.mini-bar-wrap {
  margin-top: 0.25rem;
}

.metric-sub-note {
  font-size: 0.75rem;
  color: #64748b;
}

/* Tabs */
.tab-nav-container {
  border-bottom: 1px solid #e2e8f0;
  width: 100%;
  overflow-x: auto;
}

.tab-nav-strip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: max-content;
}

.tab-btn {
  padding: 0.625rem 1rem;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  font-size: 0.875rem;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.tab-btn:hover {
  color: #0f172a;
}

.tab-btn.is-active {
  color: #2563eb;
  border-bottom-color: #2563eb;
  font-weight: 600;
}

/* Tab Content */
.tab-pane-container {
  width: 100%;
}

.tab-action-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.875rem;
}

.action-bar-title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #0f172a;
}

.btn-primary-sm {
  height: 2rem;
  padding: 0 0.875rem;
  background-color: #2563eb;
  border: 1px solid transparent;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #ffffff;
  cursor: pointer;
}

.btn-primary-sm:hover {
  background-color: #1d4ed8;
}

/* Overview Pane */
.overview-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.pane-card {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1.25rem;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.pane-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.pane-card-title {
  font-size: 0.9375rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.link-btn {
  background: transparent;
  border: none;
  font-size: 0.75rem;
  font-weight: 600;
  color: #2563eb;
  cursor: pointer;
}

.link-btn:hover {
  text-decoration: underline;
}

.spec-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.spec-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.8125rem;
}

.spec-item:last-child {
  border-bottom: none;
}

.spec-label {
  color: #64748b;
  font-weight: 500;
}

.spec-value {
  color: #0f172a;
  font-weight: 600;
}

.code-pill {
  font-size: 0.6875rem;
  font-weight: 600;
  background-color: #f1f5f9;
  color: #334155;
  padding: 0.1rem 0.4rem;
  border-radius: 0.25rem;
  border: 1px solid #e2e8f0;
}

.mini-teacher-list {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.mini-teacher-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.625rem;
  background-color: #f8fafc;
  border: 1px solid #f1f5f9;
  border-radius: 0.5rem;
}

.mini-t-avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background-color: #e0e7ff;
  color: #4338ca;
  font-size: 0.75rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mini-t-info {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  flex: 1;
  min-width: 0;
}

.mini-t-name {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #0f172a;
}

.mini-t-sub {
  font-size: 0.6875rem;
  color: #64748b;
}

.mini-t-id {
  font-size: 0.6875rem;
  color: #64748b;
}

/* Tables */
.table-card {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  overflow: hidden;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
}

.table-responsive {
  width: 100%;
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.8125rem;
}

.data-table thead {
  background-color: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.data-table th {
  padding: 0.625rem 0.875rem;
  font-size: 0.6875rem;
  font-weight: 600;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  white-space: nowrap;
}

.data-table td {
  padding: 0.75rem 0.875rem;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

.student-cell {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.st-avatar {
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 50%;
  background-color: #eff6ff;
  color: #2563eb;
  font-size: 0.6875rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.bg-indigo {
  background-color: #e0e7ff;
  color: #4338ca;
}

.st-name {
  font-weight: 600;
  color: #0f172a;
}

.portal-tag {
  font-size: 0.6875rem;
  padding: 0.1rem 0.4rem;
  border-radius: 0.25rem;
  font-weight: 500;
}

.tag-enabled {
  background-color: #ecfdf5;
  color: #065f46;
}

.tag-none {
  background-color: #f1f5f9;
  color: #64748b;
}

.btn-remove-sm {
  background: transparent;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 0.2rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.6875rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-remove-sm:hover {
  background-color: #fef2f2;
}

/* Subjects Grid */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.875rem;
}

.subject-card {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 0.625rem;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
}

.sub-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sub-code {
  font-size: 0.6875rem;
  font-weight: 700;
  background-color: #eff6ff;
  color: #1d4ed8;
  padding: 0.1rem 0.35rem;
  border-radius: 0.25rem;
}

.sub-dept {
  font-size: 0.6875rem;
  color: #64748b;
}

.sub-name {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.sub-teacher {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.75rem;
}

.sub-teacher-label {
  color: #64748b;
}

.sub-teacher-val {
  color: #1e293b;
  font-weight: 600;
}

.empty-state-tab {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 2.5rem 1rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  color: #64748b;
  font-size: 0.875rem;
}

.empty-tab-sub {
  font-size: 0.8125rem;
  color: #94a3b8;
  text-align: center;
  padding: 1.5rem 0;
}

/* Responsive */
@media (max-width: 1024px) {
  .metrics-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .cards-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 767px) {
  .back-nav-bar {
    margin-bottom: 16px;
  }

  .profile-container {
    gap: 16px;
  }

  /* 1. Class Profile Header Card */
  .hero-card {
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 16px;
    gap: 0;
    width: 100%;
    box-sizing: border-box;
  }

  .hero-main {
    flex-direction: column;
    align-items: center;
    width: 100%;
    gap: 0;
    text-align: center;
  }

  /* 2. Class Icon */
  .hero-avatar {
    width: 3.5rem;
    height: 3.5rem;
    border-radius: 0.875rem;
    margin: 0 auto 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .hero-avatar svg {
    width: 1.75rem;
    height: 1.75rem;
  }

  .hero-identity {
    width: 100%;
    align-items: center;
    text-align: center;
    gap: 0;
  }

  .hero-title-row {
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0;
    width: 100%;
  }

  /* 3. Class Title */
  .hero-class-name {
    text-align: center;
    font-size: clamp(1.625rem, 5.5vw, 1.875rem);
    font-weight: 700;
    color: #0f172a;
    margin: 0;
    line-height: 1.25;
    word-break: break-word;
  }

  /* 4. Status Badges */
  .hero-badges {
    margin-top: 12px;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    width: 100%;
  }

  .hero-meta-row {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100%;
    gap: 0;
  }

  /* 5. Class Code + Section */
  .hero-meta-code-section {
    margin-top: 14px;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    width: 100%;
  }

  /* 6. Academic Year */
  .hero-meta-academic-year {
    margin-top: 16px;
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    font-size: 0.875rem;
  }

  /* 7. Max Capacity */
  .hero-meta-capacity {
    margin-top: 12px;
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    font-size: 0.875rem;
  }

  /* 8. Action Buttons */
  .hero-actions {
    margin-top: 20px;
    display: flex;
    flex-direction: column;
    width: 100%;
    gap: 10px;
  }

  .btn-action {
    min-height: 48px;
    height: 48px;
    font-size: 0.875rem;
    border-radius: 0.625rem;
    font-weight: 600;
  }

  .hero-actions .btn-primary {
    width: 100%;
    justify-content: center;
  }

  .hero-secondary-actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    width: 100%;
  }

  .hero-secondary-actions .btn-action {
    width: 100%;
    justify-content: center;
    padding: 0 0.5rem;
  }

  .btn-status-toggle {
    width: 100%;
    justify-content: center;
  }

  .metrics-strip {
    grid-template-columns: 1fr;
  }

  .overview-grid {
    grid-template-columns: 1fr;
  }

  .cards-grid {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 390px) and (max-width: 767px) {
  .hero-card {
    padding: 18px 20px;
  }
}

@media (max-width: 360px) {
  .hero-card {
    padding: 14px;
  }
}

@media (max-width: 340px) {
  .hero-secondary-actions {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .hero-actions {
    gap: 8px;
  }

  .btn-action {
    min-height: 44px;
    height: 44px;
    font-size: 0.8125rem;
  }
}
</style>
