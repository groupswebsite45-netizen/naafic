<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { studentService } from '../../../services/studentService';
import { classService } from '../../../services/classService';
import { StudentFullProfile, SchoolClass } from '../../../types/school';
import StudentStatusBadge from './components/StudentStatusBadge.vue';
import StudentFormModal from './components/StudentFormModal.vue';
import ChangeClassModal from './components/ChangeClassModal.vue';
import ManagePortalModal from './components/ManagePortalModal.vue';
import StudentConfirmDialog from './components/StudentConfirmDialog.vue';

const route = useRoute();
const router = useRouter();

const studentId = computed(() => Number(route.params.id));
const profile = ref<StudentFullProfile | null>(null);
const availableClasses = ref<SchoolClass[]>([]);
const isLoading = ref(true);
const errorMessage = ref('');
const successMessage = ref('');

const activeTab = ref<'overview' | 'personal' | 'enrollment' | 'fees' | 'exams' | 'portal'>('overview');

// Modals
const isEditModalOpen = ref(false);
const isChangeClassModalOpen = ref(false);
const isPortalModalOpen = ref(false);
const isConfirmStatusOpen = ref(false);
const isSubmitting = ref(false);

function getInitials(name: string): string {
  if (!name) return 'ST';
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

const hasEnrollmentConflict = computed(() => {
  if (!profile.value?.enrollments || profile.value.enrollments.length <= 1) return false;
  const activeCount = profile.value.enrollments.filter((e) => e.status === 'ACTIVE').length;
  return activeCount > 1;
});

async function loadProfile() {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    const [prof, classesRes]: any = await Promise.all([
      studentService.getFullProfile(studentId.value),
      classService.getClasses({ page_size: 100 }),
    ]);
    profile.value = prof;
    availableClasses.value = Array.isArray(classesRes) ? classesRes : classesRes?.items || [];
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to load student profile from database.';
  } finally {
    isLoading.value = false;
  }
}

async function handleSaveEdit(payload: any) {
  if (!profile.value) return;
  isSubmitting.value = true;
  try {
    const { photoFile, shouldRemovePhoto, ...studentData } = payload;
    await studentService.updateStudent(profile.value.id, studentData);
    if (shouldRemovePhoto) {
      await studentService.deletePhoto(profile.value.id);
    } else if (photoFile) {
      await studentService.uploadPhoto(profile.value.id, photoFile);
    }
    successMessage.value = 'Student profile updated successfully.';
    isEditModalOpen.value = false;
    await loadProfile();
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Failed to update student profile.');
  } finally {
    isSubmitting.value = false;
  }
}

async function handleSaveClass(payload: any) {
  if (!profile.value) return;
  isSubmitting.value = true;
  try {
    await studentService.enrollStudent(profile.value.id, payload);
    successMessage.value = 'Student class assignment updated.';
    isChangeClassModalOpen.value = false;
    await loadProfile();
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Failed to enroll student.');
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
    await studentService.updateStatus(profile.value.id, targetStatus, `Admin ${actionName}d student`);
    successMessage.value = `Student status successfully updated to ${targetStatus}.`;
    isConfirmStatusOpen.value = false;
    await loadProfile();
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Failed to change student status.');
  } finally {
    isSubmitting.value = false;
  }
}

function goBack() {
  router.push('/admin/students');
}

onMounted(() => {
  loadProfile();
});
</script>

<template>
  <div class="student-profile-page">
    <!-- Compact Back Navigation -->
    <div class="top-nav-bar">
      <button type="button" class="btn-back" @click="goBack">
        <span class="back-arrow">&larr;</span>
        <span class="desktop-back-label">Back to Students</span>
        <span class="mobile-back-label">Students</span>
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
    <div v-if="isLoading" class="loading-state-card card">
      <div class="spinner" />
      <p>Loading student profile from PostgreSQL...</p>
    </div>

    <!-- Main Profile View -->
    <div v-else-if="profile" class="profile-content">
      <!-- Profile Header Hero Card -->
      <div class="profile-hero-card">
        <div class="hero-top-layout">
          <!-- Identity block -->
          <div class="hero-identity">
            <div class="hero-avatar-container">
              <div
                class="hero-avatar"
                :class="{ 'has-photo': !!profile.photo_path }"
                :style="!profile.photo_path ? { backgroundColor: getAvatarBg(profile.full_name || profile.first_name) } : {}"
              >
                <img
                  v-if="profile.photo_path"
                  :src="studentService.getPhotoUrl(profile.id, profile.photo_path) || ''"
                  :alt="profile.full_name || profile.first_name"
                  class="hero-avatar-img"
                  @error="profile.photo_path = null"
                />
                <span v-else>{{ getInitials(profile.full_name || profile.first_name) }}</span>
              </div>
              <button
                type="button"
                class="avatar-edit-badge"
                title="Update Profile Photo"
                aria-label="Update Profile Photo"
                @click="isEditModalOpen = true"
              >
                <svg class="badge-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>
            </div>
            <div class="hero-name-block">
              <div class="hero-title-row">
                <h1 class="hero-name">{{ profile.full_name || `${profile.first_name} ${profile.last_name}` }}</h1>
                <StudentStatusBadge :status="profile.status" size="sm" />
                <span
                  class="portal-badge"
                  :class="{
                    'enabled': profile.has_portal_access && profile.portal_is_active !== false,
                    'suspended': profile.has_portal_access && profile.portal_is_active === false,
                    'disabled': !profile.has_portal_access
                  }"
                >
                  {{ !profile.has_portal_access ? 'No Portal' : profile.portal_is_active !== false ? 'Portal Enabled' : 'Portal Disabled' }}
                </span>
              </div>
              <div class="hero-meta-row">
                <span class="meta-chip">ADM-{{ profile.admission_number.replace(/^ADM-/, '') }}</span>
                <span class="meta-sep">&bull;</span>
                <span class="meta-chip id-chip">STU-{{ String(profile.id).padStart(4, '0') }}</span>
                <span class="meta-sep">&bull;</span>
                <span class="meta-text">{{ profile.gender }}</span>
                <span class="meta-sep">&bull;</span>
                <span class="meta-text font-semibold">{{ profile.current_class ? profile.current_class.name : 'Unassigned' }}</span>
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
            <button type="button" class="btn-action secondary" @click="isChangeClassModalOpen = true">
              <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
              </svg>
              <span>Change Class</span>
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

        <!-- Compact Metrics Overview Strip -->
        <div class="hero-stats-grid">
          <div class="hero-stat-card">
            <span class="hero-stat-label">Enrolled Class</span>
            <span class="hero-stat-val text-blue">
              {{ profile.current_class ? profile.current_class.name : 'Unassigned' }}
            </span>
            <span class="hero-stat-sub">{{ profile.current_class?.academic_year || 'Academic Year 2025-2026' }}</span>
          </div>

          <div class="hero-stat-card">
            <span class="hero-stat-label">Fee Invoices</span>
            <span class="hero-stat-val text-slate">
              ${{ profile.financial_summary?.total_billed ? profile.financial_summary.total_billed.toFixed(2) : '0.00' }}
            </span>
            <span class="hero-stat-sub">{{ profile.fees?.length || 0 }} Assigned Fees</span>
          </div>

          <div class="hero-stat-card">
            <span class="hero-stat-label">Amount Paid</span>
            <span class="hero-stat-val text-green">
              ${{ profile.financial_summary?.total_paid ? profile.financial_summary.total_paid.toFixed(2) : '0.00' }}
            </span>
            <span class="hero-stat-sub">Receipts Recorded</span>
          </div>

          <div class="hero-stat-card">
            <span class="hero-stat-label">Outstanding Balance</span>
            <span
              class="hero-stat-val"
              :class="(profile.financial_summary?.outstanding_balance || 0) > 0 ? 'text-rose' : 'text-green'"
            >
              ${{ profile.financial_summary?.outstanding_balance ? profile.financial_summary.outstanding_balance.toFixed(2) : '0.00' }}
            </span>
            <span class="hero-stat-sub">{{ (profile.financial_summary?.outstanding_balance || 0) > 0 ? 'Payment Due' : 'All Settled' }}</span>
          </div>
        </div>
      </div>

      <!-- Navigation Tabs (Touch-scrollable on mobile) -->
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
          Personal & Guardian
        </button>
        <button
          class="profile-tab"
          :class="{ active: activeTab === 'enrollment' }"
          @click="activeTab = 'enrollment'"
        >
          Enrollment ({{ profile.enrollments?.length || 0 }})
        </button>
        <button
          class="profile-tab"
          :class="{ active: activeTab === 'fees' }"
          @click="activeTab = 'fees'"
        >
          Fees ({{ profile.fees?.length || 0 }})
        </button>
        <button
          class="profile-tab"
          :class="{ active: activeTab === 'exams' }"
          @click="activeTab = 'exams'"
        >
          Exams ({{ profile.exam_results?.length || 0 }})
        </button>
        <button
          class="profile-tab"
          :class="{ active: activeTab === 'portal' }"
          @click="activeTab = 'portal'"
        >
          Portal
        </button>
      </div>

      <!-- Tab Content Panes -->
      <div class="tab-content-area">
        <!-- TAB 1: Overview -->
        <div v-if="activeTab === 'overview'" class="tab-pane-layout">
          <div class="overview-grid">
            <div class="card detail-card">
              <h3 class="card-section-title">Student Information Snapshot</h3>
              <div class="info-list">
                <div class="info-row">
                  <span class="info-label">Full Name</span>
                  <span class="info-val font-semibold">{{ profile.full_name }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Admission Number</span>
                  <span class="info-val"><code class="code-tag">{{ profile.admission_number }}</code></span>
                </div>
                <div class="info-row">
                  <span class="info-label">Gender</span>
                  <span class="info-val">{{ profile.gender }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Date of Birth</span>
                  <span class="info-val">{{ profile.date_of_birth || 'Not Specified' }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Admission Date</span>
                  <span class="info-val">{{ profile.admission_date || 'Not Specified' }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Phone</span>
                  <span class="info-val">{{ profile.phone || '—' }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Address</span>
                  <span class="info-val">{{ profile.address || '—' }}</span>
                </div>
              </div>
            </div>

            <div class="card detail-card">
              <h3 class="card-section-title">Guardian & Parent Details</h3>
              <div class="info-list">
                <div class="info-row">
                  <span class="info-label">Guardian Name</span>
                  <span class="info-val font-semibold">{{ profile.guardian_name || 'Not Specified' }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Relationship</span>
                  <span class="info-val">{{ profile.guardian_relationship || 'Parent' }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Guardian Phone</span>
                  <span class="info-val font-semibold text-blue">{{ profile.guardian_phone || '—' }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Guardian Email</span>
                  <span class="info-val">{{ profile.guardian_email || '—' }}</span>
                </div>
              </div>

              <div class="portal-quick-card mt-3">
                <div class="portal-quick-header">
                  <span class="font-semibold text-slate-800 text-sm">Student Portal Access</span>
                  <span class="portal-pill" :class="profile.has_portal_access ? 'enabled' : 'disabled'">
                    {{ profile.has_portal_access ? 'Active' : 'Not Provisioned' }}
                  </span>
                </div>
                <p v-if="profile.has_portal_access" class="text-xs text-slate-600 mt-1">
                  Username: <code>{{ profile.portal_username }}</code>
                </p>
                <p v-else class="text-xs text-slate-500 mt-1">
                  No login credentials created yet for this student.
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
          <h3 class="card-section-title">Comprehensive Personal & Contact Records</h3>
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
              <span class="display-label">Contact Phone</span>
              <span class="display-value">{{ profile.phone || '—' }}</span>
            </div>
            <div class="display-field col-span-full">
              <span class="display-label">Residential Address</span>
              <span class="display-value">{{ profile.address || '—' }}</span>
            </div>
            <div class="display-field">
              <span class="display-label">Guardian Name</span>
              <span class="display-value">{{ profile.guardian_name || '—' }}</span>
            </div>
            <div class="display-field">
              <span class="display-label">Guardian Relationship</span>
              <span class="display-value">{{ profile.guardian_relationship || '—' }}</span>
            </div>
            <div class="display-field">
              <span class="display-label">Guardian Phone</span>
              <span class="display-value">{{ profile.guardian_phone || '—' }}</span>
            </div>
            <div class="display-field">
              <span class="display-label">Guardian Email</span>
              <span class="display-value">{{ profile.guardian_email || '—' }}</span>
            </div>
          </div>
        </div>

        <!-- TAB 3: Enrollment History -->
        <div v-if="activeTab === 'enrollment'" class="card detail-card">
          <div class="section-header-row">
            <h3 class="card-section-title">Historical & Current Enrollments</h3>
            <button class="btn-sm-primary" @click="isChangeClassModalOpen = true">
              + Enroll In Class
            </button>
          </div>

          <!-- Conflict Warning Alert if multiple active records exist -->
          <div v-if="hasEnrollmentConflict" class="conflict-alert-box">
            <svg class="w-5 h-5 text-amber-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div class="conflict-text">
              <strong>Enrollment Inconsistency Detected:</strong> This student currently has multiple active class enrollment records. You can update or reassign the class using the <em>Change Class</em> action above.
            </div>
          </div>

          <div v-if="!profile.enrollments || profile.enrollments.length === 0" class="empty-tab-state">
            <p>No enrollment history found for this student.</p>
          </div>

          <div v-else class="subtable-wrapper">
            <table class="enterprise-subtable">
              <thead>
                <tr>
                  <th>Academic Year</th>
                  <th>Class Name</th>
                  <th>Class Code</th>
                  <th>Roll Number</th>
                  <th>Enrollment Date</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="e in profile.enrollments" :key="e.id">
                  <td class="font-semibold">{{ e.academic_year }}</td>
                  <td>{{ e.school_class?.name || 'Class ID ' + e.class_id }}</td>
                  <td><code class="code-tag">{{ e.school_class?.code || '—' }}</code></td>
                  <td>{{ e.roll_number || '—' }}</td>
                  <td>{{ e.start_date || (e.created_at ? e.created_at.split('T')[0] : '—') }}</td>
                  <td>
                    <StudentStatusBadge :status="e.status" size="sm" />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- TAB 4: Fees & Financials -->
        <div v-if="activeTab === 'fees'" class="card detail-card">
          <h3 class="card-section-title">Student Fee Invoices & Payment Ledger</h3>

          <div v-if="!profile.fees || profile.fees.length === 0" class="empty-tab-state">
            <p>No fee records assigned to this student yet.</p>
          </div>

          <div v-else class="subtable-wrapper">
            <table class="enterprise-subtable">
              <thead>
                <tr>
                  <th>Fee Description</th>
                  <th>Academic Year</th>
                  <th>Amount Billed</th>
                  <th>Amount Paid</th>
                  <th>Balance Due</th>
                  <th>Due Date</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="f in profile.fees" :key="f.id">
                  <td class="font-semibold">{{ f.fee_name }}</td>
                  <td>{{ f.academic_year }}</td>
                  <td>${{ f.total_amount.toFixed(2) }}</td>
                  <td class="text-green font-semibold">${{ f.paid_amount.toFixed(2) }}</td>
                  <td class="font-semibold" :class="f.balance > 0 ? 'text-rose' : 'text-slate-600'">
                    ${{ f.balance.toFixed(2) }}
                  </td>
                  <td>{{ f.due_date || '—' }}</td>
                  <td>
                    <StudentStatusBadge :status="f.status" size="sm" />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- TAB 5: Exam Results -->
        <div v-if="activeTab === 'exams'" class="card detail-card">
          <h3 class="card-section-title">Academic Examination Report Card</h3>

          <div v-if="!profile.exam_results || profile.exam_results.length === 0" class="empty-tab-state">
            <p>No exam results recorded for this student.</p>
          </div>

          <div v-else class="subtable-wrapper">
            <table class="enterprise-subtable">
              <thead>
                <tr>
                  <th>Exam Name</th>
                  <th>Subject</th>
                  <th>Academic Year</th>
                  <th>Marks Obtained</th>
                  <th>Total Marks</th>
                  <th>Grade</th>
                  <th>Remarks</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="ex in profile.exam_results" :key="ex.id">
                  <td class="font-semibold">{{ ex.exam_name }}</td>
                  <td>{{ ex.subject_name }}</td>
                  <td>{{ ex.academic_year }}</td>
                  <td class="font-bold text-blue">{{ ex.marks_obtained }}</td>
                  <td>{{ ex.total_marks }}</td>
                  <td>
                    <span class="grade-badge">{{ ex.grade || '—' }}</span>
                  </td>
                  <td class="text-slate-600">{{ ex.remarks || '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- TAB 6: Portal Account -->
        <div v-if="activeTab === 'portal'" class="card detail-card">
          <div class="portal-tab-header">
            <h3 class="card-section-title">Student Portal Authentication Settings</h3>
            <button
              v-if="profile.has_portal_access"
              type="button"
              class="btn-portal-manage"
              @click="isPortalModalOpen = true"
            >
              Manage Credentials
            </button>
          </div>
          <div v-if="profile.has_portal_access" class="portal-settings-box">
            <div class="portal-info-row">
              <span class="label">Portal Access Status:</span>
              <span
                class="portal-pill"
                :class="profile.portal_is_active !== false ? 'enabled' : 'suspended'"
              >
                {{ profile.portal_is_active !== false ? 'Active & Enabled' : 'Disabled / Suspended' }}
              </span>
            </div>
            <div class="portal-info-row">
              <span class="label">Portal Username:</span>
              <span class="val"><code>{{ profile.portal_username }}</code></span>
            </div>
            <div class="portal-info-row">
              <span class="label">Assigned Role:</span>
              <span class="val font-semibold text-slate-800">STUDENT</span>
            </div>
            <div class="portal-info-row">
              <span class="label">Portal Login URL:</span>
              <span class="val"><code>/login</code></span>
            </div>
          </div>
          <div v-else class="empty-portal-box">
            <p class="text-sm text-slate-600">This student does not have an active portal login account.</p>
            <button class="btn-sm-primary mt-3" @click="isPortalModalOpen = true">
              Activate Student Portal Account
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <StudentFormModal
      :is-open="isEditModalOpen"
      :is-editing="true"
      :student="profile"
      :available-classes="availableClasses"
      :is-submitting="isSubmitting"
      @close="isEditModalOpen = false"
      @save="handleSaveEdit"
    />

    <ChangeClassModal
      :is-open="isChangeClassModalOpen"
      :student="profile"
      :available-classes="availableClasses"
      :is-submitting="isSubmitting"
      @close="isChangeClassModalOpen = false"
      @save="handleSaveClass"
    />

    <ManagePortalModal
      :is-open="isPortalModalOpen"
      :student="profile"
      :is-submitting="isSubmitting"
      @close="isPortalModalOpen = false"
      @updated="loadProfile"
    />

    <StudentConfirmDialog
      :is-open="isConfirmStatusOpen"
      :title="profile?.status === 'ACTIVE' ? 'Deactivate Student Record?' : 'Re-activate Student Record?'"
      :message="profile?.status === 'ACTIVE' ? `Deactivating ${profile?.full_name} will suspend active student access while preserving all historical enrollment, exam, and fee payment data.` : `Re-activating ${profile?.full_name} will restore active enrollment and portal access.`"
      :confirm-text="profile?.status === 'ACTIVE' ? 'Deactivate Student' : 'Activate Student'"
      :variant="profile?.status === 'ACTIVE' ? 'danger' : 'primary'"
      :is-loading="isSubmitting"
      @confirm="handleConfirmStatusChange"
      @cancel="isConfirmStatusOpen = false"
    />
  </div>
</template>

<style scoped>
.student-profile-page {
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

.hero-avatar-container {
  position: relative;
  flex-shrink: 0;
}

.hero-avatar {
  width: 52px;
  height: 52px;
  border-radius: 9999px;
  color: #ffffff;
  font-size: 1.1rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  border: 2px solid #ffffff;
}

.hero-avatar.has-photo {
  background: #f1f5f9;
}

.hero-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.avatar-edit-badge {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #2563eb;
  border: 2px solid #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
  transition: all 0.2s ease;
  padding: 0;
}

.avatar-edit-badge:hover {
  background: #1d4ed8;
  transform: scale(1.1);
}

.badge-icon {
  width: 12px;
  height: 12px;
  color: #ffffff;
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
  border-color: #1d4ed8;
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
.text-green { color: #16a34a; }
.text-rose { color: #e11d48; }
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

.conflict-alert-box {
  display: flex;
  align-items: flex-start;
  gap: 0.625rem;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 8px;
  padding: 0.625rem 0.875rem;
  font-size: 0.78125rem;
  color: #92400e;
  margin-bottom: 0.875rem;
}

.conflict-text {
  line-height: 1.4;
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

.grade-badge {
  display: inline-flex;
  padding: 0.125rem 0.4rem;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 4px;
  font-weight: 700;
  color: #1d4ed8;
  font-size: 0.72rem;
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

.portal-tab-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-portal-manage {
  height: 32px;
  padding: 0 0.85rem;
  background: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
  border-radius: 6px;
  font-size: 0.78125rem;
  font-weight: 600;
  cursor: pointer;
}
.btn-portal-manage:hover {
  background: #dbeafe;
}

.portal-badge {
  padding: 0.15rem 0.45rem;
  border-radius: 9999px;
  font-size: 0.65rem;
  font-weight: 600;
}

.portal-badge.enabled { background: #dcfce7; color: #166534; }
.portal-badge.suspended { background: #fef3c7; color: #b45309; }
.portal-badge.disabled { background: #f1f5f9; color: #64748b; }

.portal-pill {
  padding: 0.125rem 0.4rem;
  border-radius: 9999px;
  font-size: 0.65rem;
  font-weight: 600;
}

.portal-pill.enabled { background: #dcfce7; color: #166534; }
.portal-pill.suspended { background: #fef3c7; color: #b45309; }
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
    grid-template-columns: 1fr;
  }
}
</style>
