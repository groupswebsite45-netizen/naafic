<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { studentPortalService } from '../../services/studentPortalService';
import { StudentProfileData } from '../../types/studentPortal';

const profile = ref<StudentProfileData | null>(null);
const isLoading = ref(true);
const errorMessage = ref('');

async function loadProfile() {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    profile.value = await studentPortalService.getProfile();
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Unable to retrieve student profile.';
  } finally {
    isLoading.value = false;
  }
}

function formatDate(dateStr?: string | null) {
  if (!dateStr) return '—';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { day: 'numeric', month: 'long', year: 'numeric' });
  } catch {
    return dateStr;
  }
}

onMounted(() => {
  loadProfile();
});
</script>

<template>
  <div class="portal-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">My Student Profile</h1>
        <p class="page-subtitle">Your official bio-data, guardian contacts, and institutional enrollment records.</p>
      </div>
    </div>

    <!-- Mandatory Read-Only Notification Banner -->
    <div class="readonly-banner">
      <div class="banner-icon-wrap">
        <svg class="banner-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
      </div>
      <div class="banner-text">
        <strong class="banner-title">PROFILE INFORMATION &bull; READ-ONLY</strong>
        <p class="banner-desc">
          To maintain academic record integrity, personal and academic details cannot be edited directly by students.
          For corrections or updates to your records, please contact the Education Management System Administration Office.
        </p>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="card loading-card">
      <div class="spinner" />
      <span>Loading official profile records from PostgreSQL...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage" class="card error-card">
      <p class="error-title">Unable to Load Profile</p>
      <p class="error-desc">{{ errorMessage }}</p>
      <button class="retry-btn" @click="loadProfile">Try Again</button>
    </div>

    <!-- Profile Content -->
    <div v-else-if="profile" class="profile-grid">
      <!-- Profile Hero Card -->
      <div class="card hero-card">
        <div class="avatar-wrap">
          <div class="avatar-initials">
            {{ profile.first_name?.[0] }}{{ profile.last_name?.[0] }}
          </div>
        </div>
        <div class="hero-info">
          <div class="hero-header-row">
            <h2 class="student-name">{{ profile.full_name }}</h2>
            <span class="status-badge" :class="profile.status.toLowerCase()">
              {{ profile.status }}
            </span>
          </div>
          <div class="hero-meta-row">
            <span class="meta-item">
              Admission No: <strong>{{ profile.admission_number }}</strong>
            </span>
            <span class="meta-sep">&bull;</span>
            <span class="meta-item">
              Class: <strong>{{ profile.current_class_name || 'Unassigned' }}</strong>
            </span>
            <span class="meta-sep">&bull;</span>
            <span class="meta-item">
              Academic Year: <strong>{{ profile.academic_year || 'Current' }}</strong>
            </span>
          </div>
        </div>
      </div>

      <!-- Detail Cards 2-Column Grid -->
      <div class="details-two-column">
        <!-- 1. Personal Information Card -->
        <div class="card info-card">
          <div class="card-header">
            <svg class="section-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <h3 class="section-title">Personal Information</h3>
          </div>
          <div class="info-list">
            <div class="info-row">
              <span class="info-label">Full Name</span>
              <span class="info-val font-semibold">{{ profile.full_name }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Admission Number</span>
              <span class="info-val font-mono">{{ profile.admission_number }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Gender</span>
              <span class="info-val">{{ profile.gender }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Date of Birth</span>
              <span class="info-val">{{ formatDate(profile.date_of_birth) }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Phone</span>
              <span class="info-val">{{ profile.phone || 'Not registered' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Email</span>
              <span class="info-val">{{ profile.email || 'Not registered' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Residential Address</span>
              <span class="info-val">{{ profile.address || 'Mogadishu, Somalia' }}</span>
            </div>
          </div>
        </div>

        <!-- 2. Guardian Details Card -->
        <div class="card info-card">
          <div class="card-header">
            <svg class="section-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <h3 class="section-title">Guardian & Emergency Contacts</h3>
          </div>
          <div class="info-list">
            <div class="info-row">
              <span class="info-label">Guardian Name</span>
              <span class="info-val font-semibold">{{ profile.guardian_name || '—' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Relationship</span>
              <span class="info-val">{{ profile.guardian_relationship || 'Parent / Guardian' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Guardian Phone</span>
              <span class="info-val font-mono">{{ profile.guardian_phone || '—' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Guardian Email</span>
              <span class="info-val">{{ profile.guardian_email || '—' }}</span>
            </div>
          </div>
        </div>

        <!-- 3. Academic Enrollment Details Card -->
        <div class="card info-card full-width">
          <div class="card-header">
            <svg class="section-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
            <h3 class="section-title">Enrollment & Institutional Status</h3>
          </div>
          <div class="academic-stats-grid">
            <div class="stat-box">
              <span class="stat-lbl">CURRENT GRADE</span>
              <span class="stat-val">{{ profile.current_class_name || 'Unassigned' }}</span>
              <span class="stat-sub">Code: {{ profile.current_class_code || 'N/A' }}</span>
            </div>
            <div class="stat-box">
              <span class="stat-lbl">ACADEMIC YEAR</span>
              <span class="stat-val">{{ profile.academic_year || '2025-2026' }}</span>
              <span class="stat-sub">Standard Curriculum</span>
            </div>
            <div class="stat-box">
              <span class="stat-lbl">ADMISSION DATE</span>
              <span class="stat-val">{{ formatDate(profile.admission_date) }}</span>
              <span class="stat-sub">Official Registration</span>
            </div>
            <div class="stat-box">
              <span class="stat-lbl">PORTAL ACCESS</span>
              <span class="stat-val text-emerald">{{ profile.portal_account_status }}</span>
              <span class="stat-sub">Authenticated Session</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.portal-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-title {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}

.page-subtitle {
  font-size: 0.88rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

/* Mandatory Read-Only Notification */
.readonly-banner {
  background: linear-gradient(135deg, rgba(2, 132, 199, 0.08) 0%, rgba(16, 185, 129, 0.08) 100%);
  border: 1px solid rgba(2, 132, 199, 0.25);
  border-left: 4px solid #0284c7;
  border-radius: 8px;
  padding: 1rem 1.25rem;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.banner-icon-wrap {
  width: 36px;
  height: 36px;
  background-color: rgba(2, 132, 199, 0.15);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.banner-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: #0284c7;
}

.banner-title {
  font-size: 0.82rem;
  letter-spacing: 0.05em;
  color: #0284c7;
  display: block;
}

.banner-desc {
  font-size: 0.82rem;
  color: var(--text-secondary);
  margin: 0.2rem 0 0 0;
  line-height: 1.45;
}

/* Hero Card */
.hero-card {
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.25rem;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
}

.avatar-wrap {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, #047857 0%, #10b981 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 800;
  font-size: 1.6rem;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
}

.hero-info {
  flex: 1;
}

.hero-header-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.student-name {
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}

.status-badge {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  text-transform: uppercase;
}

.status-badge.active {
  background-color: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.hero-meta-row {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-top: 0.35rem;
  flex-wrap: wrap;
}

.meta-item strong {
  color: var(--text-primary);
}

.meta-sep {
  color: var(--border-subtle);
}

/* Two Column Details */
.details-two-column {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
  margin-top: 1.25rem;
}

.info-card {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
}

.full-width {
  grid-column: span 2;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  border-bottom: 1px solid var(--border-subtle);
  padding-bottom: 0.65rem;
}

.section-icon {
  width: 1.2rem;
  height: 1.2rem;
  color: #10b981;
}

.section-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 0.5rem;
  border-bottom: 1px dashed var(--border-subtle);
  font-size: 0.88rem;
}

.info-label {
  color: var(--text-muted);
}

.info-val {
  color: var(--text-primary);
  text-align: right;
}

.font-semibold {
  font-weight: 600;
}

.font-mono {
  font-family: monospace;
  background-color: var(--bg-surface-secondary);
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}

/* Academic stats */
.academic-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.stat-box {
  background-color: var(--bg-surface-secondary);
  padding: 1rem;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  border-left: 3px solid #10b981;
}

.stat-lbl {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--text-muted);
}

.stat-val {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--text-primary);
}

.stat-sub {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.text-emerald {
  color: #10b981;
}

/* Common states */
.loading-card, .error-card {
  padding: 3rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-subtle);
  border-top-color: #10b981;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #dc2626;
  margin: 0;
}

.error-desc {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin: 0;
}

.retry-btn {
  background-color: #0f172a;
  color: #fff;
  border: 1px solid #334155;
  padding: 0.4rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

@media (max-width: 820px) {
  .details-two-column {
    grid-template-columns: 1fr;
  }
  .full-width {
    grid-column: span 1;
  }
  .academic-stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .hero-card {
    flex-direction: column;
    text-align: center;
  }
  .hero-header-row {
    justify-content: center;
  }
  .hero-meta-row {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .academic-stats-grid {
    grid-template-columns: 1fr;
  }
  .info-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.2rem;
  }
  .info-val {
    text-align: left;
  }
}
</style>
