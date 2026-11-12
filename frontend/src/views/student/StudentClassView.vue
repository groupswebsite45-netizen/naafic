<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { studentPortalService } from '../../services/studentPortalService';
import { StudentClassDetails } from '../../types/studentPortal';

const classData = ref<StudentClassDetails | null>(null);
const academicYears = ref<string[]>([]);
const selectedYear = ref<string>('');
const isLoading = ref(true);
const errorMessage = ref('');

async function loadData() {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    classData.value = await studentPortalService.getMyClass(selectedYear.value || undefined);
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to load class and subject information.';
  } finally {
    isLoading.value = false;
  }
}

async function initPage() {
  try {
    academicYears.value = await studentPortalService.getAcademicYears();
    if (academicYears.value.length > 0) {
      selectedYear.value = academicYears.value[0];
    }
  } catch {
    academicYears.value = ['2026/2027', '2025/2026'];
    selectedYear.value = '2026/2027';
  }
  await loadData();
}

function handleYearChange() {
  loadData();
}

onMounted(() => {
  initPage();
});
</script>

<template>
  <div class="class-portal">
    <!-- Header -->
    <div class="page-header">
      <div class="header-main">
        <div>
          <div class="somroyal-tag">
            <svg class="crown-icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M5 16L3 5l5.5 5L12 4l3.5 6L21 5l-2 11H5m14 3c0 .6-.4 1-1 1H6c-.6 0-1-.4-1-1v-1h14v1z"/>
            </svg>
            <span>ACADEMIC ENROLLMENT &amp; CURRICULUM</span>
          </div>
          <h1 class="page-title">My Class &amp; Subjects</h1>
          <p class="page-subtitle">Your grade level cohort, assigned classroom faculty, curriculum subjects, and academic year history.</p>
        </div>

        <!-- Academic Year Selector & Refresh -->
        <div class="header-controls">
          <div v-if="academicYears.length > 0" class="year-selector-box">
            <label for="class-year-select" class="selector-lbl">Academic Year</label>
            <select
              id="class-year-select"
              v-model="selectedYear"
              class="year-select"
              @change="handleYearChange"
            >
              <option v-for="y in academicYears" :key="y" :value="y">{{ y }}</option>
            </select>
          </div>

          <button
            type="button"
            class="btn-refresh"
            title="Refresh class details"
            :disabled="isLoading"
            @click="loadData"
          >
            <svg class="refresh-icon" :class="{ spinning: isLoading }" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
            </svg>
            <span>Sync</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="state-card loading">
      <div class="spinner-ring" />
      <p class="loading-label">Retrieving class enrollment records from Somroyal database...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage" class="error-banner">
      <div class="error-icon-box">
        <svg viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
      </div>
      <div class="error-details">
        <h3 class="error-title">Unable to Load Class Details</h3>
        <p class="error-desc">{{ errorMessage }}</p>
      </div>
      <button class="btn-retry" @click="loadData">Try Again</button>
    </div>

    <div v-else-if="classData" class="content-stack">
      <!-- 1. Enrolled Class Hero Card -->
      <div v-if="classData.school_class" class="class-hero-card">
        <div class="hero-top-row">
          <div class="hero-badges">
            <span class="badge-grade">{{ classData.school_class.name }}</span>
            <span class="badge-year">{{ classData.academic_year }}</span>
          </div>
          <div class="hero-status">
            <span class="pulse-dot" />
            <span>ENROLLED &amp; ACTIVE</span>
          </div>
        </div>

        <div class="hero-body">
          <h2 class="class-title">{{ classData.school_class.name }} <span class="class-code">({{ classData.school_class.code }})</span></h2>
          <div class="meta-badges-row">
            <div class="meta-pill">
              <span class="meta-lbl">Section</span>
              <strong class="meta-val">{{ classData.section || classData.school_class.section || 'General Stream' }}</strong>
            </div>
            <div class="meta-pill">
              <span class="meta-lbl">Class Teacher</span>
              <strong class="meta-val">{{ classData.class_teacher_name || 'Assigned by Administration' }}</strong>
            </div>
            <div class="meta-pill">
              <span class="meta-lbl">Capacity</span>
              <strong class="meta-val">{{ classData.capacity }} Students</strong>
            </div>
          </div>
          <p v-if="classData.school_class.description" class="class-description">
            {{ classData.school_class.description }}
          </p>
        </div>
      </div>

      <div v-else class="state-card empty">
        <div class="empty-icon-circle">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        </div>
        <h3 class="state-title">No Active Class Enrollment</h3>
        <p class="state-desc">You are not currently enrolled in a class cohort for the selected academic year ({{ selectedYear }}).</p>
      </div>

      <!-- 2. Enrolled Subjects Grid -->
      <div class="section-block">
        <div class="section-head">
          <div class="section-title-box">
            <h3 class="section-title">Enrolled Academic Subjects</h3>
            <span class="counter-badge">{{ classData.subjects.length }} Subjects</span>
          </div>
          <span class="section-subtext">Approved syllabus courses for your current curriculum</span>
        </div>

        <div v-if="classData.subjects.length === 0" class="state-card empty-sub">
          <p class="empty-text">No syllabus subjects have been registered for this grade level yet.</p>
        </div>

        <div v-else class="subjects-grid">
          <div
            v-for="s in classData.subjects"
            :key="s.id"
            class="subject-card"
          >
            <div class="subj-top">
              <span class="dept-pill">{{ s.department || 'General Academic' }}</span>
              <span class="code-pill">{{ s.code }}</span>
            </div>

            <h4 class="subj-name">{{ s.name }}</h4>

            <div class="subj-faculty">
              <div class="faculty-avatar">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="faculty-info">
                <span class="faculty-lbl">Instructor</span>
                <strong class="faculty-val">{{ s.teacher_name || 'Faculty Member' }}</strong>
              </div>
            </div>

            <div class="subj-foot">
              <span class="status-pill active">
                <span class="dot" />
                <span>{{ s.status || 'Active' }}</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. Academic Year Enrollment History -->
      <div class="section-block">
        <div class="section-head">
          <div class="section-title-box">
            <h3 class="section-title">Academic Year Enrollment History</h3>
            <span class="counter-badge">{{ classData.enrollment_history.length }} Years</span>
          </div>
          <span class="section-subtext">Historical grade progress and past institutional records</span>
        </div>

        <div v-if="classData.enrollment_history.length === 0" class="state-card empty-sub">
          <p class="empty-text">No previous academic enrollment history found for your student profile.</p>
        </div>

        <div v-else class="history-list">
          <div
            v-for="(hist, idx) in classData.enrollment_history"
            :key="idx"
            class="history-card"
            :class="{ current: hist.academic_year === selectedYear }"
          >
            <div class="history-year-col">
              <span class="history-year-num">{{ hist.academic_year }}</span>
              <span v-if="hist.academic_year === selectedYear" class="current-badge">Active Cohort</span>
            </div>

            <div class="history-divider" />

            <div class="history-details-col">
              <div class="history-class-row">
                <h4 class="history-class-name">{{ hist.class_name }}</h4>
                <span class="history-class-code">({{ hist.class_code }})</span>
              </div>
              <div class="history-meta-row">
                <span class="meta-chunk">Section: <strong>{{ hist.section || 'General' }}</strong></span>
                <span class="bullet">&bull;</span>
                <span class="meta-chunk">Roll No: <strong>{{ hist.roll_number || '—' }}</strong></span>
                <span class="bullet">&bull;</span>
                <span class="meta-chunk">Enrollment Status: <strong class="text-emerald">{{ hist.status }}</strong></span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.class-portal {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

/* Header */
.page-header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.header-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1.25rem;
}

.somroyal-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #38BDF8;
  text-transform: uppercase;
  margin-bottom: 0.35rem;
}

.crown-icon {
  width: 14px;
  height: 14px;
  color: #F59E0B;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #0A192F;
  letter-spacing: -0.02em;
  margin: 0;
}

.page-subtitle {
  font-size: 0.88rem;
  color: #64748B;
  margin-top: 0.25rem;
  line-height: 1.5;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.year-selector-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  padding: 0.35rem 0.75rem;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.selector-lbl {
  font-size: 0.72rem;
  font-weight: 700;
  color: #64748B;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.year-select {
  background: transparent;
  border: none;
  font-size: 0.85rem;
  font-weight: 700;
  color: #0A192F;
  cursor: pointer;
  outline: none;
}

.btn-refresh {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: #FFFFFF;
  color: #0A192F;
  border: 1px solid #E2E8F0;
  padding: 0.5rem 0.85rem;
  border-radius: 10px;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.btn-refresh:hover:not(:disabled) {
  border-color: #1E3A8A;
  color: #1E3A8A;
  background: #EFF6FF;
}

.refresh-icon {
  width: 15px;
  height: 15px;
}

.refresh-icon.spinning {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Error Banner */
.error-banner {
  background: #FEF2F2;
  border: 1px solid #FCA5A5;
  border-radius: 12px;
  padding: 1rem 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.error-icon-box {
  width: 36px;
  height: 36px;
  background: #EF4444;
  color: #FFFFFF;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.error-icon-box svg {
  width: 20px;
  height: 20px;
}

.error-details {
  flex: 1;
}

.error-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #991B1B;
  margin: 0;
}

.error-desc {
  font-size: 0.82rem;
  color: #B91C1C;
  margin: 0.15rem 0 0 0;
}

.btn-retry {
  background: #991B1B;
  color: #FFFFFF;
  border: none;
  padding: 0.45rem 0.9rem;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
}

/* Content Stack */
.content-stack {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}

/* Class Hero Card */
.class-hero-card {
  background: linear-gradient(135deg, #0A192F 0%, #0F2A4A 60%, #081528 100%);
  border-radius: 16px;
  padding: 1.75rem 2rem;
  color: #FFFFFF;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 10px 25px -5px rgba(10, 25, 47, 0.25);
  position: relative;
  overflow: hidden;
}

.class-hero-card::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 300px;
  background: radial-gradient(circle at right, rgba(16, 185, 129, 0.18) 0%, transparent 70%);
  pointer-events: none;
}

.hero-top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.hero-badges {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.badge-grade {
  background: #10B981;
  color: #FFFFFF;
  font-size: 0.75rem;
  font-weight: 800;
  padding: 0.25rem 0.65rem;
  border-radius: 6px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.badge-year {
  background: rgba(255, 255, 255, 0.15);
  color: #E2E8F0;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.65rem;
  border-radius: 6px;
}

.hero-status {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.7rem;
  font-weight: 800;
  color: #10B981;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
  padding: 0.25rem 0.65rem;
  border-radius: 20px;
  letter-spacing: 0.06em;
}

.pulse-dot {
  width: 6px;
  height: 6px;
  background: #10B981;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.85); }
}

.class-title {
  font-size: 1.6rem;
  font-weight: 900;
  color: #FFFFFF;
  letter-spacing: -0.01em;
  margin: 0;
}

.class-code {
  color: #94A3B8;
  font-weight: 600;
  font-size: 1.15rem;
}

.meta-badges-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-top: 1rem;
}

.meta-pill {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 0.4rem 0.85rem;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.82rem;
}

.meta-lbl {
  color: #94A3B8;
  font-size: 0.75rem;
}

.meta-val {
  color: #FFFFFF;
  font-weight: 700;
}

.class-description {
  font-size: 0.86rem;
  color: #CBD5E1;
  margin: 1rem 0 0 0;
  line-height: 1.5;
  background: rgba(0, 0, 0, 0.2);
  padding: 0.75rem 1rem;
  border-radius: 8px;
  border-left: 3px solid #10B981;
}

/* Sections */
.section-block {
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.section-title-box {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.section-title {
  font-size: 1.2rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
}

.counter-badge {
  font-size: 0.72rem;
  font-weight: 800;
  background: #ECFDF5;
  color: #059669;
  border: 1px solid #A7F3D0;
  padding: 0.15rem 0.55rem;
  border-radius: 20px;
}

.section-subtext {
  font-size: 0.82rem;
  color: #64748B;
}

/* Subjects Grid */
.subjects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.15rem;
}

.subject-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 14px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  box-shadow: 0 2px 6px rgba(10, 25, 47, 0.03);
  transition: all 0.2s ease;
  position: relative;
}

.subject-card:hover {
  border-color: #CBD5E1;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(10, 25, 47, 0.06);
}

.subj-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dept-pill {
  font-size: 0.7rem;
  font-weight: 700;
  background: #F1F5F9;
  color: #475569;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
}

.code-pill {
  font-size: 0.74rem;
  font-family: monospace;
  font-weight: 800;
  color: #2563EB;
  background: #EFF6FF;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
}

.subj-name {
  font-size: 1.1rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
  line-height: 1.35;
}

.subj-faculty {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  background: #F8FAFC;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
}

.faculty-avatar {
  width: 28px;
  height: 28px;
  background: #E2E8F0;
  color: #64748B;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.faculty-avatar svg {
  width: 16px;
  height: 16px;
}

.faculty-info {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.faculty-lbl {
  font-size: 0.65rem;
  color: #94A3B8;
  font-weight: 700;
  text-transform: uppercase;
}

.faculty-val {
  font-size: 0.82rem;
  color: #0A192F;
  font-weight: 700;
}

.subj-foot {
  margin-top: auto;
  padding-top: 0.6rem;
  border-top: 1px solid #F1F5F9;
  display: flex;
  justify-content: flex-end;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 20px;
}

.status-pill.active {
  background: #ECFDF5;
  color: #059669;
}

.status-pill.active .dot {
  width: 5px;
  height: 5px;
  background: #10B981;
  border-radius: 50%;
}

/* Timeline / History List */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.history-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 1.15rem 1.35rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  transition: all 0.2s ease;
}

.history-card.current {
  border-left: 4px solid #10B981;
  background: linear-gradient(135deg, #FFFFFF 0%, #F0FDF4 100%);
  border-color: #A7F3D0;
}

.history-year-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  min-width: 90px;
}

.history-year-num {
  font-size: 1.15rem;
  font-weight: 900;
  color: #0A192F;
}

.current-badge {
  font-size: 0.68rem;
  font-weight: 800;
  background: #10B981;
  color: #FFFFFF;
  padding: 0.15rem 0.5rem;
  border-radius: 10px;
}

.history-divider {
  width: 1px;
  height: 38px;
  background: #E2E8F0;
}

.history-details-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.history-class-row {
  display: flex;
  align-items: baseline;
  gap: 0.4rem;
}

.history-class-name {
  font-size: 1.05rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
}

.history-class-code {
  font-size: 0.82rem;
  color: #64748B;
  font-weight: 600;
}

.history-meta-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
  color: #64748B;
  flex-wrap: wrap;
}

.meta-chunk strong {
  color: #1E293B;
}

.bullet {
  color: #CBD5E1;
}

.text-emerald {
  color: #059669 !important;
}

/* States */
.state-card {
  background: #FFFFFF;
  border-radius: 16px;
  border: 1px solid #E2E8F0;
  padding: 3.5rem 1.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.state-card.empty-sub {
  padding: 2rem;
  background: #F8FAFC;
}

.empty-text {
  font-size: 0.86rem;
  color: #64748B;
  margin: 0;
}

.spinner-ring {
  width: 36px;
  height: 36px;
  border: 3px solid #E2E8F0;
  border-top-color: #1E3A8A;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.loading-label {
  font-size: 0.88rem;
  color: #64748B;
  font-weight: 600;
}

.empty-icon-circle {
  width: 56px;
  height: 56px;
  background: #F1F5F9;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94A3B8;
}

.empty-icon-circle svg {
  width: 28px;
  height: 28px;
}

.state-title {
  font-size: 1.15rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
}

.state-desc {
  font-size: 0.86rem;
  color: #64748B;
  max-width: 500px;
  line-height: 1.5;
  margin: 0;
}

@media (max-width: 640px) {
  .header-main {
    flex-direction: column;
    align-items: stretch;
  }

  .header-controls {
    justify-content: space-between;
  }

  .class-hero-card {
    padding: 1.25rem;
  }

  .history-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .history-divider {
    display: none;
  }

  .history-year-col {
    flex-direction: row;
    align-items: center;
    gap: 0.5rem;
    min-width: unset;
  }
}
</style>
