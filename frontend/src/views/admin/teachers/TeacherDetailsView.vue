<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { teacherService, AssignTeacherPayload, CreateTeacherPayload } from '../../../services/teacherService';
import { classService } from '../../../services/classService';
import { subjectService } from '../../../services/subjectService';
import { TeacherFullProfile, SchoolClass, Subject } from '../../../types/school';
import TeacherStatusBadge from './components/TeacherStatusBadge.vue';
import TeacherFormModal from './components/TeacherFormModal.vue';
import TeacherAssignmentModal from './components/TeacherAssignmentModal.vue';
import TeacherPortalModal from './components/TeacherPortalModal.vue';
import TeacherConfirmDialog from './components/TeacherConfirmDialog.vue';

const route = useRoute();
const router = useRouter();

const teacherId = computed(() => Number(route.params.id));
const profile = ref<TeacherFullProfile | null>(null);
const availableClasses = ref<SchoolClass[]>([]);
const availableSubjects = ref<Subject[]>([]);
const isLoading = ref(true);
const errorMessage = ref('');
const successMessage = ref('');

const activeTab = ref<'overview' | 'personal' | 'professional' | 'assignments' | 'timetable' | 'portal'>('overview');

// Modals
const isEditModalOpen = ref(false);
const isAssignModalOpen = ref(false);
const isPortalModalOpen = ref(false);
const isConfirmStatusOpen = ref(false);
const isSubmitting = ref(false);

function getInitials(name: string): string {
  if (!name) return 'TC';
  const parts = name.trim().split(/\s+/);
  if (parts.length >= 2) {
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }
  return name.slice(0, 2).toUpperCase();
}

function getAvatarBg(name: string): string {
  const colors = [
    '#2563eb', '#0891b2', '#059669', '#d97706',
    '#7c3aed', '#db2777', '#4f46e5', '#0284c7'
  ];
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return colors[Math.abs(hash) % colors.length];
}

const uniqueClassesCount = computed(() => {
  if (!profile.value?.assignments || profile.value.assignments.length === 0) return 0;
  return new Set(profile.value.assignments.map((a) => a.class_id)).size;
});

const uniqueSubjectsCount = computed(() => {
  if (!profile.value?.assignments || profile.value.assignments.length === 0) return 0;
  return new Set(profile.value.assignments.map((a) => a.subject_id)).size;
});

async function loadProfile() {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    const [prof, classesRes, subjectsRes]: any = await Promise.all([
      teacherService.getFullProfile(teacherId.value),
      classService.getClasses({ page_size: 100 }),
      subjectService.getSubjects({ page_size: 100 }),
    ]);
    profile.value = prof;
    availableClasses.value = Array.isArray(classesRes) ? classesRes : classesRes?.items || [];
    availableSubjects.value = Array.isArray(subjectsRes) ? subjectsRes : subjectsRes?.items || [];
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to load teacher profile from database.';
  } finally {
    isLoading.value = false;
  }
}

async function handleSaveEdit(payload: CreateTeacherPayload) {
  if (!profile.value) return;
  isSubmitting.value = true;
  try {
    await teacherService.updateTeacher(profile.value.id, payload);
    successMessage.value = 'Teacher profile updated successfully.';
    isEditModalOpen.value = false;
    await loadProfile();
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Failed to update teacher profile.');
  } finally {
    isSubmitting.value = false;
  }
}

async function handleSaveAssignment(payload: AssignTeacherPayload) {
  if (!profile.value) return;
  isSubmitting.value = true;
  try {
    await teacherService.assignTeacher(profile.value.id, payload);
    successMessage.value = 'Teaching assignment added successfully.';
    isAssignModalOpen.value = false;
    await loadProfile();
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Failed to allocate teacher to class.');
  } finally {
    isSubmitting.value = false;
  }
}

async function handleRemoveAssignment(assignmentId: number) {
  if (!profile.value) return;
  try {
    await teacherService.removeAssignment(assignmentId);
    successMessage.value = 'Teaching allocation removed.';
    await loadProfile();
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Failed to remove assignment.');
  }
}

async function handleCreatePortal(payload: any) {
  if (!profile.value) return;
  isSubmitting.value = true;
  try {
    await teacherService.createPortalAccount(profile.value.id, payload);
    successMessage.value = 'Teacher portal account activated successfully.';
    isPortalModalOpen.value = false;
    await loadProfile();
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Failed to create portal account.');
  } finally {
    isSubmitting.value = false;
  }
}

async function handleConfirmStatusChange() {
  if (!profile.value) return;
  isSubmitting.value = true;
  const isCurrentlyActive = profile.value.status === 'ACTIVE';
  const targetStatus = isCurrentlyActive ? 'INACTIVE' : 'ACTIVE';
  const actionName = isCurrentlyActive ? 'deactivate' : 'activate';

  try {
    await teacherService.updateStatus(profile.value.id, targetStatus, `Admin ${actionName}d teacher`);
    successMessage.value = `Teacher status updated to ${targetStatus}.`;
    isConfirmStatusOpen.value = false;
    await loadProfile();
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Failed to change teacher status.');
  } finally {
    isSubmitting.value = false;
  }
}

function goBack() {
  router.push('/admin/teachers');
}

onMounted(() => {
  loadProfile();
});
</script>

<template>
  <div class="teacher-profile-page">
    <!-- Compact Back Navigation -->
    <div class="top-nav-bar">
      <button type="button" class="btn-back" @click="goBack">
        <span class="back-arrow">&larr;</span>
        <span class="desktop-back-label">Back to Teachers</span>
        <span class="mobile-back-label">Teachers</span>
      </button>
    </div>

    <!-- Alert Notifications -->
    <div v-if="successMessage" class="alert-box success">
      <span>{{ successMessage }}</span>
      <button class="alert-close" @click="successMessage = ''">&times;</button>
    </div>
    <div v-if="errorMessage" class="alert-box error">
      <span>{{ errorMessage }}</span>
      <button class="btn-retry" @click="loadProfile">Retry</button>
    </div>

    <!-- Loading Skeleton State -->
    <div v-if="isLoading" class="loading-state-card">
      <div class="spinner" />
      <p>Loading teacher profile from PostgreSQL...</p>
    </div>

    <!-- Main Profile View -->
    <div v-else-if="profile" class="profile-content">
      <!-- Profile Header Hero Card -->
      <div class="profile-hero-card">
        <div class="hero-top-layout">
          <!-- Identity block -->
          <div class="hero-identity">
            <div
              class="hero-avatar"
              :style="{ backgroundColor: getAvatarBg(profile.full_name || `${profile.first_name} ${profile.last_name}`) }"
            >
              {{ getInitials(profile.full_name || `${profile.first_name} ${profile.last_name}`) }}
            </div>
            <div class="hero-name-block">
              <div class="hero-title-row">
                <h1 class="hero-name">{{ profile.full_name || `${profile.first_name} ${profile.last_name}` }}</h1>
                <TeacherStatusBadge :status="profile.status" size="sm" />
                <span class="portal-badge" :class="profile.has_portal_access ? 'enabled' : 'disabled'">
                  {{ profile.has_portal_access ? 'Portal Enabled' : 'No Portal' }}
                </span>
              </div>
              <div class="hero-meta-row">
                <span class="meta-chip id-chip">{{ profile.teacher_number || profile.employee_id || `TCH-${String(profile.id).padStart(4, '0')}` }}</span>
                <span class="meta-sep">&bull;</span>
                <span class="meta-text">{{ profile.qualification || 'Faculty Member' }}</span>
                <span class="meta-sep">&bull;</span>
                <span class="meta-text">{{ profile.gender }}</span>
                <span class="meta-sep">&bull;</span>
                <span class="meta-text">{{ profile.email }}</span>
              </div>
            </div>
          </div>

          <!-- Hero Actions Hierarchy -->
          <div class="hero-actions">
            <button type="button" class="btn-action primary" @click="isEditModalOpen = true">
              <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              <span>Edit Profile</span>
            </button>
            <button type="button" class="btn-action secondary" @click="isAssignModalOpen = true">
              <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              <span>Assign Classes</span>
            </button>
            <button type="button" class="btn-action secondary" @click="isPortalModalOpen = true">
              <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
              </svg>
              <span>Portal Access</span>
            </button>
            <button
              type="button"
              class="btn-action"
              :class="profile.status === 'ACTIVE' ? 'outline-danger' : 'outline-success'"
              @click="isConfirmStatusOpen = true"
            >
              <span>{{ profile.status === 'ACTIVE' ? 'Deactivate' : 'Activate' }}</span>
            </button>
          </div>
        </div>

        <!-- Compact Workload Overview Strip -->
        <div class="hero-stats-grid">
          <div class="hero-stat-card">
            <span class="hero-stat-label">Assigned Classes</span>
            <span class="hero-stat-val text-blue">
              {{ uniqueClassesCount }} {{ uniqueClassesCount === 1 ? 'Class' : 'Classes' }}
            </span>
            <span class="hero-stat-sub">Academic Year 2025-2026</span>
          </div>

          <div class="hero-stat-card">
            <span class="hero-stat-label">Teaching Subjects</span>
            <span class="hero-stat-val text-purple">
              {{ uniqueSubjectsCount }} {{ uniqueSubjectsCount === 1 ? 'Subject' : 'Subjects' }}
            </span>
            <span class="hero-stat-sub">Subject Allocations</span>
          </div>

          <div class="hero-stat-card">
            <span class="hero-stat-label">Timetable Slots</span>
            <span class="hero-stat-val text-slate">
              {{ profile.timetables?.length || 0 }} Slots
            </span>
            <span class="hero-stat-sub">Scheduled Periods</span>
          </div>

          <div class="hero-stat-card">
            <span class="hero-stat-label">Portal Account</span>
            <span
              class="hero-stat-val"
              :class="profile.has_portal_access ? 'text-green' : 'text-slate-500'"
            >
              {{ profile.has_portal_access ? 'Enabled' : 'Not Provisioned' }}
            </span>
            <span class="hero-stat-sub">{{ profile.has_portal_access ? `User: ${profile.portal_username || profile.email}` : 'No Credentials' }}</span>
          </div>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div class="profile-tabs-bar">
        <button
          class="profile-tab"
          :class="{ active: activeTab === 'overview' }"
          @click="activeTab = 'overview'"
        >
          Overview
        </button>
        <button
          class="profile-tab"
          :class="{ active: activeTab === 'personal' }"
          @click="activeTab = 'personal'"
        >
          Personal Info
        </button>
        <button
          class="profile-tab"
          :class="{ active: activeTab === 'professional' }"
          @click="activeTab = 'professional'"
        >
          Professional Profile
        </button>
        <button
          class="profile-tab"
          :class="{ active: activeTab === 'assignments' }"
          @click="activeTab = 'assignments'"
        >
          Teaching Assignments ({{ profile.assignments?.length || 0 }})
        </button>
        <button
          class="profile-tab"
          :class="{ active: activeTab === 'timetable' }"
          @click="activeTab = 'timetable'"
        >
          Timetable ({{ profile.timetables?.length || 0 }})
        </button>
        <button
          class="profile-tab"
          :class="{ active: activeTab === 'portal' }"
          @click="activeTab = 'portal'"
        >
          Portal Account
        </button>
      </div>

      <!-- Tab Content Panes -->
      <div class="tab-content-area">
        <!-- TAB 1: Overview -->
        <div v-if="activeTab === 'overview'" class="tab-pane-layout">
          <div class="overview-grid">
            <div class="card detail-card">
              <h3 class="card-section-title">Faculty Information Snapshot</h3>
              <div class="info-list">
                <div class="info-row">
                  <span class="info-label">Full Name</span>
                  <span class="info-val font-semibold">{{ profile.full_name }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Teacher Number</span>
                  <span class="info-val"><code class="code-tag">{{ profile.teacher_number || profile.employee_id }}</code></span>
                </div>
                <div class="info-row">
                  <span class="info-label">Gender</span>
                  <span class="info-val">{{ profile.gender }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Email</span>
                  <span class="info-val">{{ profile.email }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Phone</span>
                  <span class="info-val">{{ profile.phone || '—' }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Qualification</span>
                  <span class="info-val">{{ profile.qualification || '—' }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Hire Date</span>
                  <span class="info-val">{{ profile.hire_date || '—' }}</span>
                </div>
              </div>
            </div>

            <div class="card detail-card">
              <div class="section-header-row">
                <h3 class="card-section-title">Teaching Workload Snapshot</h3>
                <button class="btn-sm-primary" @click="isAssignModalOpen = true">
                  + Add Allocation
                </button>
              </div>

              <div v-if="!profile.assignments || profile.assignments.length === 0" class="empty-tab-state">
                <p>No active classes or subjects allocated yet.</p>
              </div>

              <div v-else class="workload-overview-list">
                <div v-for="a in profile.assignments" :key="a.id" class="workload-item">
                  <div class="workload-item-info">
                    <span class="font-semibold text-slate-800 text-xs">{{ a.subject?.name || a.subject_name || `Subject #${a.subject_id}` }}</span>
                    <span class="alloc-class-pill">{{ a.school_class?.name || a.class_name || `Class #${a.class_id}` }}</span>
                  </div>
                  <span class="text-xs text-slate-500">{{ a.academic_year }}</span>
                </div>
              </div>

              <!-- Portal Quick Card -->
              <div class="portal-quick-card mt-3">
                <div class="portal-quick-header">
                  <span class="font-semibold text-slate-800 text-sm">Teacher Portal Access</span>
                  <span class="portal-pill" :class="profile.has_portal_access ? 'enabled' : 'disabled'">
                    {{ profile.has_portal_access ? 'Active' : 'Not Provisioned' }}
                  </span>
                </div>
                <p v-if="profile.has_portal_access" class="text-xs text-slate-600 mt-1">
                  Username: <code>{{ profile.portal_username || profile.email }}</code>
                </p>
                <p v-else class="text-xs text-slate-500 mt-1">
                  No login credentials created yet for this teacher.
                </p>
                <button class="btn-portal-action mt-2" @click="isPortalModalOpen = true">
                  {{ profile.has_portal_access ? 'Manage Portal Account' : 'Provision Portal Login' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- TAB 2: Personal Information -->
        <div v-if="activeTab === 'personal'" class="card detail-card">
          <h3 class="card-section-title">Personal & Contact Details</h3>
          <div class="form-display-grid">
            <div class="display-field">
              <span class="display-label">First Name</span>
              <span class="display-value">{{ profile.first_name }}</span>
            </div>
            <div class="display-field">
              <span class="display-label">Middle Name</span>
              <span class="display-value">{{ profile.middle_name || '—' }}</span>
            </div>
            <div class="display-field">
              <span class="display-label">Last / Family Name</span>
              <span class="display-value">{{ profile.last_name }}</span>
            </div>
            <div class="display-field">
              <span class="display-label">Gender</span>
              <span class="display-value">{{ profile.gender }}</span>
            </div>
            <div class="display-field">
              <span class="display-label">Date of Birth</span>
              <span class="display-value">{{ profile.date_of_birth || '—' }}</span>
            </div>
            <div class="display-field">
              <span class="display-label">Email Address</span>
              <span class="display-value">{{ profile.email }}</span>
            </div>
            <div class="display-field">
              <span class="display-label">Phone Number</span>
              <span class="display-value">{{ profile.phone || '—' }}</span>
            </div>
            <div class="display-field col-span-full">
              <span class="display-label">Residential Address</span>
              <span class="display-value">{{ profile.address || '—' }}</span>
            </div>
          </div>
        </div>

        <!-- TAB 3: Professional Profile -->
        <div v-if="activeTab === 'professional'" class="card detail-card">
          <h3 class="card-section-title">Academic & Professional Credentials</h3>
          <div class="form-display-grid">
            <div class="display-field">
              <span class="display-label">Teacher Identification</span>
              <span class="display-value"><code class="code-tag">{{ profile.teacher_number || profile.employee_id }}</code></span>
            </div>
            <div class="display-field">
              <span class="display-label">Employment Status</span>
              <span class="display-value">
                <TeacherStatusBadge :status="profile.status" size="sm" />
              </span>
            </div>
            <div class="display-field col-span-full">
              <span class="display-label">Qualification & Degrees</span>
              <span class="display-value">{{ profile.qualification || '—' }}</span>
            </div>
            <div class="display-field">
              <span class="display-label">Hire Date</span>
              <span class="display-value">{{ profile.hire_date || '—' }}</span>
            </div>
            <div class="display-field">
              <span class="display-label">Record Created</span>
              <span class="display-value">{{ profile.created_at ? profile.created_at.split('T')[0] : '—' }}</span>
            </div>
          </div>
        </div>

        <!-- TAB 4: Teaching Assignments -->
        <div v-if="activeTab === 'assignments'" class="card detail-card">
          <div class="section-header-row">
            <h3 class="card-section-title">Assigned Classes & Subjects</h3>
            <button class="btn-sm-primary" @click="isAssignModalOpen = true">
              + Add Teaching Assignment
            </button>
          </div>

          <div v-if="!profile.assignments || profile.assignments.length === 0" class="empty-tab-state">
            <p>No active class or subject allocations for this teacher.</p>
          </div>

          <div v-else class="subtable-wrapper" tabindex="0" role="region" aria-label="Teaching assignments table">
            <table class="enterprise-subtable">
              <thead>
                <tr>
                  <th>Subject</th>
                  <th>Subject Code</th>
                  <th>Class</th>
                  <th>Academic Year</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="a in profile.assignments" :key="a.id">
                  <td class="font-semibold">{{ a.subject?.name || a.subject_name || `Subject #${a.subject_id}` }}</td>
                  <td><code class="code-tag">{{ a.subject?.code || a.subject_code || '—' }}</code></td>
                  <td>
                    <span class="alloc-class-pill">{{ a.school_class?.name || a.class_name || `Class #${a.class_id}` }}</span>
                  </td>
                  <td>{{ a.academic_year }}</td>
                  <td>
                    <TeacherStatusBadge :status="a.status" size="sm" />
                  </td>
                  <td>
                    <button
                      type="button"
                      class="btn-table-remove"
                      @click="handleRemoveAssignment(a.id)"
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- TAB 5: Timetable Schedule -->
        <div v-if="activeTab === 'timetable'" class="card detail-card">
          <h3 class="card-section-title">Weekly Scheduled Periods</h3>

          <div v-if="!profile.timetables || profile.timetables.length === 0" class="empty-tab-state">
            <p>No scheduled timetable periods recorded for this teacher.</p>
          </div>

          <div v-else class="subtable-wrapper" tabindex="0" role="region" aria-label="Weekly timetable table">
            <table class="enterprise-subtable">
              <thead>
                <tr>
                  <th>Day</th>
                  <th>Time Slot</th>
                  <th>Class</th>
                  <th>Subject</th>
                  <th>Room</th>
                  <th>Academic Year</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="tt in profile.timetables" :key="tt.id">
                  <td class="font-bold text-blue-800">{{ tt.day_of_week }}</td>
                  <td class="font-mono text-xs">{{ tt.start_time }} – {{ tt.end_time }}</td>
                  <td>
                    <span class="alloc-class-pill">{{ tt.school_class?.name || `Class #${tt.class_id}` }}</span>
                  </td>
                  <td class="font-semibold">{{ tt.subject?.name || `Subject #${tt.subject_id}` }}</td>
                  <td>{{ tt.room || '—' }}</td>
                  <td>{{ tt.academic_year }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- TAB 6: Portal Account -->
        <div v-if="activeTab === 'portal'" class="card detail-card">
          <h3 class="card-section-title">Teacher Portal Authentication Settings</h3>
          <div v-if="profile.has_portal_access" class="portal-settings-box">
            <div class="portal-info-row">
              <span class="label">Portal Access Status:</span>
              <span class="portal-pill enabled">Active & Enabled</span>
            </div>
            <div class="portal-info-row">
              <span class="label">Portal Username:</span>
              <span class="val"><code>{{ profile.portal_username || profile.email }}</code></span>
            </div>
            <div class="portal-info-row">
              <span class="label">Assigned Role:</span>
              <span class="val font-semibold text-slate-800">TEACHER</span>
            </div>
            <div class="portal-info-row">
              <span class="label">Portal Login URL:</span>
              <span class="val"><code>/login</code></span>
            </div>
          </div>
          <div v-else class="empty-portal-box">
            <p class="text-sm text-slate-600">This teacher does not have an active portal login account.</p>
            <button class="btn-sm-primary mt-3" @click="isPortalModalOpen = true">
              Provision Teacher Portal Account
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <TeacherFormModal
      :is-open="isEditModalOpen"
      :is-editing="true"
      :teacher="profile"
      :is-submitting="isSubmitting"
      @close="isEditModalOpen = false"
      @save="handleSaveEdit"
    />

    <TeacherAssignmentModal
      :is-open="isAssignModalOpen"
      :teacher="profile"
      :available-classes="availableClasses"
      :available-subjects="availableSubjects"
      :is-submitting="isSubmitting"
      @close="isAssignModalOpen = false"
      @assign="handleSaveAssignment"
      @remove-assignment="handleRemoveAssignment"
    />

    <TeacherPortalModal
      :is-open="isPortalModalOpen"
      :teacher="profile"
      :is-submitting="isSubmitting"
      @close="isPortalModalOpen = false"
      @create-account="handleCreatePortal"
    />

    <TeacherConfirmDialog
      :is-open="isConfirmStatusOpen"
      :title="profile?.status === 'ACTIVE' ? 'Deactivate Faculty Record?' : 'Re-activate Faculty Record?'"
      :message="profile?.status === 'ACTIVE' ? `Deactivating ${profile?.full_name} will suspend active portal login and teaching permissions while preserving historical student grading and timetable data.` : `Re-activating ${profile?.full_name} will restore active teaching and portal access.`"
      :confirm-text="profile?.status === 'ACTIVE' ? 'Deactivate Teacher' : 'Activate Teacher'"
      :variant="profile?.status === 'ACTIVE' ? 'danger' : 'primary'"
      :is-loading="isSubmitting"
      @confirm="handleConfirmStatusChange"
      @cancel="isConfirmStatusOpen = false"
    />
  </div>
</template>

<style scoped>
.teacher-profile-page {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  min-width: 0;
}

.top-nav-bar {
  display: flex;
  align-items: center;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  background: transparent;
  border: 1px solid transparent;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  transition: all 0.12s ease;
}

.btn-back:hover {
  color: #0f172a;
  background: #f1f5f9;
  border-color: #e2e8f0;
}

.back-arrow {
  font-size: 1rem;
  line-height: 1;
}

.mobile-back-label {
  display: none;
}

.profile-hero-card {
  padding: 1.125rem 1.25rem;
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  min-width: 0;
}

.hero-top-layout {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  width: 100%;
  box-sizing: border-box;
}

.hero-identity {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  min-width: 0;
  flex: 1 1 auto;
}

.hero-avatar {
  width: 46px;
  height: 46px;
  border-radius: 9999px;
  color: #ffffff;
  font-size: 1.05rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.hero-name-block {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  min-width: 0;
}

.hero-title-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  min-width: 0;
}

.hero-name {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
  line-height: 1.2;
  letter-spacing: -0.01em;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.hero-meta-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
  font-size: 0.75rem;
  color: #64748b;
  min-width: 0;
}

.meta-chip {
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.7rem;
  font-weight: 600;
  color: #334155;
  white-space: nowrap;
}

.id-chip {
  background: #eff6ff;
  border-color: #bfdbfe;
  color: #1d4ed8;
}

.meta-sep {
  color: #cbd5e1;
}

.meta-text {
  white-space: nowrap;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  flex-wrap: wrap;
}

.btn-action {
  height: 34px;
  padding: 0 0.75rem;
  border-radius: 6px;
  font-size: 0.78125rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  cursor: pointer;
  transition: all 0.12s ease;
  box-sizing: border-box;
  white-space: nowrap;
}

.btn-icon {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

.btn-action.primary {
  background: #2563eb;
  border: 1px solid #2563eb;
  color: #ffffff;
}

.btn-action.primary:hover {
  background: #1d4ed8;
}

.btn-action.secondary {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #334155;
}

.btn-action.secondary:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.btn-action.outline-danger {
  background: #fff1f2;
  border: 1px solid #fecdd3;
  color: #e11d48;
}

.btn-action.outline-danger:hover {
  background: #ffe4e6;
}

.btn-action.outline-success {
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  color: #059669;
}

.hero-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.625rem;
  margin-top: 1rem;
  padding-top: 0.875rem;
  border-top: 1px solid #f1f5f9;
  width: 100%;
  box-sizing: border-box;
}

.hero-stat-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.625rem 0.75rem;
  display: flex;
  flex-direction: column;
  min-width: 0;
  box-sizing: border-box;
}

.hero-stat-label {
  font-size: 0.65rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  overflow-wrap: anywhere;
}

.hero-stat-val {
  font-size: 1.125rem;
  font-weight: 700;
  margin-top: 0.125rem;
  overflow-wrap: anywhere;
}

.hero-stat-sub {
  font-size: 0.65rem;
  color: #94a3b8;
  margin-top: 0.1rem;
  overflow-wrap: anywhere;
}

.text-blue { color: #2563eb; }
.text-purple { color: #7c3aed; }
.text-green { color: #16a34a; }
.text-slate { color: #334155; }

.profile-tabs-bar {
  display: flex;
  gap: 0.25rem;
  border-bottom: 2px solid #e2e8f0;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  width: 100%;
  box-sizing: border-box;
}

.profile-tab {
  padding: 0.5rem 0.875rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.12s ease;
  flex-shrink: 0;
}

.profile-tab:hover {
  color: #0f172a;
}

.profile-tab.active {
  color: #2563eb;
  border-bottom-color: #2563eb;
}

.tab-content-area {
  margin-top: 0.125rem;
  width: 100%;
  box-sizing: border-box;
  min-width: 0;
}

.detail-card {
  padding: 1.125rem 1.25rem;
  background: #ffffff;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  min-width: 0;
}

.card-section-title {
  font-size: 0.9375rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.75rem;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.875rem;
  width: 100%;
  box-sizing: border-box;
}

.info-list {
  display: flex;
  flex-direction: column;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.45rem 0;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.8125rem;
  gap: 0.5rem;
}

.info-label {
  color: #64748b;
  font-weight: 500;
  flex-shrink: 0;
}

.info-val {
  color: #0f172a;
  text-align: right;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.code-tag {
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  font-family: monospace;
  font-weight: 600;
  color: #334155;
  font-size: 0.75rem;
}

.workload-overview-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.workload-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.45rem 0.65rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
}

.workload-item-info {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.alloc-class-pill {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1d4ed8;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  font-size: 0.72rem;
  font-weight: 600;
}

.portal-quick-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.75rem;
  box-sizing: border-box;
}

.portal-quick-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-portal-action {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  padding: 0.3rem 0.65rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #2563eb;
  cursor: pointer;
  box-sizing: border-box;
}

.form-display-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.875rem;
  width: 100%;
  box-sizing: border-box;
}

.col-span-full {
  grid-column: 1 / -1;
}

.display-field {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  min-width: 0;
}

.display-label {
  font-size: 0.65rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.display-value {
  font-size: 0.84375rem;
  font-weight: 600;
  color: #0f172a;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.section-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-sm-primary {
  height: 30px;
  padding: 0 0.65rem;
  background: #2563eb;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  box-sizing: border-box;
}

.subtable-wrapper {
  width: 100%;
  max-width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  box-sizing: border-box;
}

.enterprise-subtable {
  width: 100%;
  min-width: 520px;
  border-collapse: collapse;
  font-size: 0.8125rem;
}

.enterprise-subtable th {
  background: #f8fafc;
  color: #475569;
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 0.55rem 0.75rem;
  border-bottom: 1px solid #e2e8f0;
  text-align: left;
  white-space: nowrap;
}

.enterprise-subtable td {
  padding: 0.55rem 0.75rem;
  border-bottom: 1px solid #f1f5f9;
  color: #1e293b;
  white-space: nowrap;
}

.btn-table-remove {
  background: #fff1f2;
  border: 1px solid #fecdd3;
  color: #e11d48;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  font-size: 0.72rem;
  font-weight: 600;
  cursor: pointer;
}

.portal-settings-box {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.portal-info-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.8125rem;
  flex-wrap: wrap;
}

.portal-info-row .label {
  width: 160px;
  color: #64748b;
  font-weight: 500;
  flex-shrink: 0;
}

.empty-tab-state {
  padding: 1.75rem 1rem;
  text-align: center;
  color: #94a3b8;
  font-size: 0.8125rem;
}

.portal-badge {
  padding: 0.15rem 0.45rem;
  border-radius: 9999px;
  font-size: 0.65rem;
  font-weight: 600;
}

.portal-badge.enabled { background: #dcfce7; color: #166534; }
.portal-badge.disabled { background: #f1f5f9; color: #64748b; }

.portal-pill {
  padding: 0.125rem 0.4rem;
  border-radius: 9999px;
  font-size: 0.65rem;
  font-weight: 600;
}

.portal-pill.enabled { background: #dcfce7; color: #166534; }
.portal-pill.disabled { background: #f1f5f9; color: #64748b; }

.alert-box {
  padding: 0.625rem 0.875rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.8125rem;
  font-weight: 500;
  box-sizing: border-box;
}

.alert-box.success { background: #ecfdf5; border: 1px solid #a7f3d0; color: #065f46; }
.alert-box.error { background: #fff1f2; border: 1px solid #fecdd3; color: #9f1239; }

.alert-close {
  background: none;
  border: none;
  font-size: 1.25rem;
  color: currentColor;
  cursor: pointer;
}

.btn-retry {
  background: #ffffff;
  border: 1px solid #fecdd3;
  color: #9f1239;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
}

.loading-state-card {
  padding: 3rem 1.5rem;
  text-align: center;
  color: #64748b;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

/* Tablet Layout (640px - 1023px) */
@media (max-width: 1023px) {
  .hero-stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

/* Mobile Layout (<640px) */
@media (max-width: 640px) {
  .desktop-back-label {
    display: none;
  }
  .mobile-back-label {
    display: inline;
  }

  .profile-hero-card {
    padding: 0.875rem;
  }

  .detail-card {
    padding: 0.875rem;
  }

  .hero-top-layout {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }

  .hero-identity {
    gap: 0.625rem;
  }

  .hero-avatar {
    width: 40px;
    height: 40px;
    font-size: 0.95rem;
  }

  .hero-name {
    font-size: 1.125rem;
  }

  .hero-actions {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.375rem;
  }

  .hero-actions .btn-action.primary {
    grid-column: 1 / -1;
    width: 100%;
  }

  .btn-action {
    width: 100%;
    padding: 0 0.4rem;
    font-size: 0.75rem;
    height: 32px;
  }

  .hero-stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.375rem;
  }

  .overview-grid {
    grid-template-columns: 1fr;
  }

  .form-display-grid {
    grid-template-columns: 1fr;
  }

  .portal-info-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.2rem;
  }

  .portal-info-row .label {
    width: 100%;
  }
}

/* Ultra-compact screen (<360px) */
@media (max-width: 359px) {
  .hero-stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.35rem;
  }
}
</style>
