<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { studentPortalService } from '../../services/studentPortalService';
import { studentService } from '../../services/studentService';
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
  <div class="portal-page student-profile-view">
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
        <strong class="banner-title">OFFICIAL PROFILE RECORD &bull; READ-ONLY ACCESS</strong>
        <p class="banner-desc">
          To maintain institutional record integrity, student personal and academic details cannot be edited directly in the portal.
          For official amendments, please visit the School Registrar or Administration Office.
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
      <div class="error-icon-box">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="10" stroke-width="2" />
          <line x1="12" y1="8" x2="12" y2="12" stroke-width="2" stroke-linecap="round" />
          <line x1="12" y1="16" x2="12.01" y2="16" stroke-width="2" stroke-linecap="round" />
        </svg>
      </div>
      <div class="error-content">
        <p class="error-title">Unable to Load Profile</p>
        <p class="error-desc">{{ errorMessage }}</p>
      </div>
      <button type="button" class="retry-btn" @click="loadProfile">Try Again</button>
    </div>

    <!-- Profile Content -->
    <div v-else-if="profile" class="profile-content-stack">
      <!-- Profile Hero Card -->
      <section class="card profile-hero-card" aria-label="Student Identity Card">
        <div class="hero-bg-accent" aria-hidden="true" />
        
        <div class="hero-body-content">
          <div class="avatar-wrap">
            <img
              v-if="profile.photo_path"
              :src="studentService.getPhotoUrl(profile.id, profile.photo_path) || ''"
              :alt="profile.full_name"
              class="avatar-photo-img"
              @error="profile.photo_path = null"
            />
            <div v-else class="avatar-initials">
              {{ profile.first_name?.[0] }}{{ profile.last_name?.[0] }}
            </div>
            <div class="online-indicator-pip" title="Active Account" />
          </div>

          <div class="hero-info">
            <div class="hero-header-row">
              <h2 class="student-name">{{ profile.full_name }}</h2>
              <span class="status-badge" :class="profile.status.toLowerCase()">
                <span class="status-dot" />
                {{ profile.status }}
              </span>
            </div>

            <div class="hero-meta-row">
              <div class="meta-pill">
                <span class="lbl">Admission:</span>
                <strong>{{ profile.admission_number }}</strong>
              </div>
              <span class="meta-dot">&bull;</span>
              <div class="meta-pill">
                <span class="lbl">Class:</span>
                <strong>{{ profile.current_class_name || 'Unassigned' }}</strong>
              </div>
              <span class="meta-dot">&bull;</span>
              <div class="meta-pill">
                <span class="lbl">Academic Year:</span>
                <strong>{{ profile.academic_year || 'Current' }}</strong>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Detail Cards Grid -->
      <div class="details-two-column">
        <!-- 1. Personal Information Card -->
        <section class="card info-card">
          <div class="card-header">
            <div class="card-icon-wrap bg-blue-tint">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div>
              <h3 class="section-title">Personal Information</h3>
              <p class="section-sub">Primary student identification records</p>
            </div>
          </div>

          <div class="info-list">
            <div class="info-row">
              <span class="info-label">Full Name</span>
              <span class="info-val font-semibold text-slate-900">{{ profile.full_name }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Admission Number</span>
              <span class="info-val font-mono font-bold text-emerald-700">{{ profile.admission_number }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Gender</span>
              <span class="info-val">{{ profile.gender || 'Not specified' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Date of Birth</span>
              <span class="info-val">{{ formatDate(profile.date_of_birth) }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Contact Phone</span>
              <span class="info-val">{{ profile.phone || 'Not registered' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Email Address</span>
              <span class="info-val">{{ profile.email || 'Not registered' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Residential Address</span>
              <span class="info-val">{{ profile.address || 'Mogadishu, Somalia' }}</span>
            </div>
          </div>
        </section>

        <!-- 2. Guardian & Emergency Contacts Card -->
        <section class="card info-card">
          <div class="card-header">
            <div class="card-icon-wrap bg-emerald-tint">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <div>
              <h3 class="section-title">Guardian & Emergency Contacts</h3>
              <p class="section-sub">Parent / guardian communication channels</p>
            </div>
          </div>

          <div class="info-list">
            <div class="info-row">
              <span class="info-label">Guardian Name</span>
              <span class="info-val font-semibold text-slate-900">{{ profile.guardian_name || '—' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Relationship</span>
              <span class="info-val">{{ profile.guardian_relationship || 'Parent / Guardian' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Guardian Phone</span>
              <span class="info-val font-mono font-bold text-slate-800">{{ profile.guardian_phone || '—' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Guardian Email</span>
              <span class="info-val">{{ profile.guardian_email || '—' }}</span>
            </div>
          </div>
        </section>

        <!-- 3. Academic Enrollment Details Card -->
        <section class="card info-card full-width">
          <div class="card-header">
            <div class="card-icon-wrap bg-purple-tint">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <div>
              <h3 class="section-title">Enrollment & Institutional Status</h3>
              <p class="section-sub">Current registration and class placement details</p>
            </div>
          </div>

          <div class="academic-stats-grid">
            <div class="stat-box">
              <span class="stat-lbl">CURRENT GRADE</span>
              <span class="stat-val">{{ profile.current_class_name || 'Unassigned' }}</span>
              <span class="stat-sub">Code: {{ profile.current_class_code || 'N/A' }}</span>
            </div>

            <div class="stat-box">
              <span class="stat-lbl">ACADEMIC YEAR</span>
              <span class="stat-val">{{ profile.academic_year || '2026/2027' }}</span>
              <span class="stat-sub">Active Term Session</span>
            </div>

            <div class="stat-box">
              <span class="stat-lbl">ENROLLMENT STATUS</span>
              <span class="stat-val text-emerald-600">{{ profile.status }}</span>
              <span class="stat-sub">Official Student Portal</span>
            </div>

            <div class="stat-box">
              <span class="stat-lbl">ADMISSION DATE</span>
              <span class="stat-val">{{ formatDate(profile.admission_date) }}</span>
              <span class="stat-sub">First Matriculation</span>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.portal-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
}

.page-header {
  margin-bottom: 0.25rem;
}

.page-title {
  font-size: 1.45rem;
  font-weight: 800;
  color: #0F172A;
  margin: 0;
}

.page-subtitle {
  font-size: 0.85rem;
  color: #64748B;
  margin: 0.25rem 0 0 0;
}

/* Card Style */
.card {
  background-color: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
}

/* Read-only Notice Banner */
.readonly-banner {
  background: #FFFBEB;
  border: 1px solid #FDE68A;
  border-left: 4px solid #F59E0B;
  border-radius: 12px;
  padding: 1rem 1.25rem;
  display: flex;
  align-items: flex-start;
  gap: 0.85rem;
}

.banner-icon-wrap {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #FEF3C7;
  color: #D97706;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.banner-icon {
  width: 18px;
  height: 18px;
}

.banner-text {
  flex: 1;
}

.banner-title {
  font-size: 0.76rem;
  font-weight: 800;
  color: #92400E;
  letter-spacing: 0.04em;
  display: block;
}

.banner-desc {
  font-size: 0.78rem;
  color: #B45309;
  margin: 0.25rem 0 0 0;
  line-height: 1.4;
}

/* Loading & Error States */
.loading-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 3.5rem 1.5rem;
  color: #64748B;
  font-size: 0.88rem;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #E2E8F0;
  border-top-color: #10B981;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  background-color: #FEF2F2;
  border-color: #FECACA;
  color: #991B1B;
}

.error-icon-box {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #FEE2E2;
  color: #DC2626;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.error-icon-box svg {
  width: 22px;
  height: 22px;
}

.error-content {
  flex: 1;
}

.error-title {
  font-size: 0.95rem;
  font-weight: 700;
  margin: 0;
}

.error-desc {
  font-size: 0.82rem;
  margin: 0.2rem 0 0 0;
  color: #B91C1C;
}

.retry-btn {
  padding: 0.5rem 1rem;
  background-color: #DC2626;
  color: #FFFFFF;
  border: none;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
}

/* Profile Content Stack */
.profile-content-stack {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Profile Hero Card */
.profile-hero-card {
  position: relative;
  overflow: hidden;
  padding: 1.75rem;
  background: #FFFFFF;
}

.hero-bg-accent {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 6px;
  background: linear-gradient(90deg, #0A192F 0%, #1E3A8A 40%, #0284C7 75%, #FF5722 100%);
}

.hero-body-content {
  display: flex;
  align-items: center;
  gap: 1.75rem;
  flex-wrap: wrap;
}

.avatar-wrap {
  position: relative;
  width: 90px;
  height: 90px;
  flex-shrink: 0;
}

.avatar-photo-img {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #FFFFFF;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.avatar-initials {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0A192F 0%, #1E3A8A 100%);
  color: #FFFFFF;
  font-weight: 800;
  font-size: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid #FFFFFF;
  box-shadow: 0 4px 12px rgba(10, 25, 47, 0.2);
}

.online-indicator-pip {
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background-color: #10B981;
  border: 2px solid #FFFFFF;
  box-shadow: 0 0 6px rgba(16, 185, 129, 0.6);
}

.hero-info {
  flex: 1;
  min-width: 250px;
}

.hero-header-row {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  flex-wrap: wrap;
  margin-bottom: 0.5rem;
}

.student-name {
  font-size: 1.5rem;
  font-weight: 800;
  color: #0F172A;
  margin: 0;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
}

.status-badge.active {
  background-color: #ECFDF5;
  color: #065F46;
  border: 1px solid #A7F3D0;
}

.status-badge.inactive {
  background-color: #FEF2F2;
  color: #991B1B;
  border: 1px solid #FECACA;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: currentColor;
}

.hero-meta-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.84rem;
  color: #64748B;
  flex-wrap: wrap;
}

.meta-pill {
  display: inline-flex;
  gap: 0.3rem;
}

.meta-pill strong {
  color: #0F172A;
}

.meta-dot {
  color: #CBD5E1;
}

/* Two Column Details Grid */
.details-two-column {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.full-width {
  grid-column: 1 / -1;
}

.info-card {
  padding: 1.5rem;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
  padding-bottom: 0.85rem;
  border-bottom: 1px solid #F1F5F9;
}

.card-icon-wrap {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-icon-wrap svg {
  width: 19px;
  height: 19px;
}

.bg-blue-tint { background: #EFF6FF; color: #2563EB; }
.bg-emerald-tint { background: #ECFDF5; color: #059669; }
.bg-purple-tint { background: #FAF5FF; color: #7C3AED; }

.section-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #0F172A;
  margin: 0;
}

.section-sub {
  font-size: 0.75rem;
  color: #64748B;
  margin: 0.15rem 0 0 0;
}

.info-list {
  display: flex;
  flex-direction: column;
}

.info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.7rem 0;
  border-bottom: 1px solid #F8FAFC;
  font-size: 0.84rem;
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  color: #64748B;
  font-weight: 500;
}

.info-val {
  color: #1E293B;
  text-align: right;
}

/* Academic Stats Grid */
.academic-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.stat-box {
  background-color: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 1rem 1.15rem;
  display: flex;
  flex-direction: column;
}

.stat-lbl {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #64748B;
}

.stat-val {
  font-size: 1.15rem;
  font-weight: 800;
  color: #0F172A;
  margin: 0.25rem 0;
}

.stat-sub {
  font-size: 0.72rem;
  color: #94A3B8;
}

/* Responsive Media Queries */
@media (max-width: 900px) {
  .details-two-column {
    grid-template-columns: 1fr;
  }
  .academic-stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .hero-body-content {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  .hero-header-row {
    justify-content: center;
  }
  .hero-meta-row {
    justify-content: center;
  }
  .info-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.2rem;
  }
  .info-val {
    text-align: left;
  }
  .academic-stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
