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
    academicYears.value = ['2025-2026'];
    selectedYear.value = '2025-2026';
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
  <div class="portal-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content-row">
        <div>
          <h1 class="page-title">My Class & Curriculum Subjects</h1>
          <p class="page-subtitle">Your grade level enrollment, class faculty, syllabus subjects, and academic year history.</p>
        </div>

        <!-- Academic Year Selector -->
        <div v-if="academicYears.length > 0" class="year-selector-wrap">
          <label for="class-year-select" class="selector-lbl">Academic Year:</label>
          <select
            id="class-year-select"
            v-model="selectedYear"
            class="year-select"
            @change="handleYearChange"
          >
            <option v-for="y in academicYears" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="card loading-card">
      <div class="spinner" />
      <span>Loading class enrollment records from PostgreSQL...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage" class="card error-card">
      <p class="error-title">Unable to Load Class Details</p>
      <p class="error-desc">{{ errorMessage }}</p>
      <button class="retry-btn" @click="loadData">Try Again</button>
    </div>

    <div v-else-if="classData" class="content-stack">
      <!-- 1. Enrolled Class Hero Card -->
      <div v-if="classData.school_class" class="card class-hero-card">
        <div class="hero-top-row">
          <span class="grade-badge">{{ classData.school_class.name }}</span>
          <span class="year-badge">{{ classData.academic_year }}</span>
        </div>
        <div class="hero-body">
          <h2 class="class-title">{{ classData.school_class.name }} ({{ classData.school_class.code }})</h2>
          <div class="class-meta-row">
            <span class="meta-item">Section: <strong>{{ classData.section || classData.school_class.section || 'General Stream' }}</strong></span>
            <span class="meta-sep">&bull;</span>
            <span class="meta-item">Class Teacher: <strong>{{ classData.class_teacher_name || 'Assigned by Administration' }}</strong></span>
            <span class="meta-sep">&bull;</span>
            <span class="meta-item">Class Capacity: <strong>{{ classData.capacity }} Students</strong></span>
          </div>
          <p v-if="classData.school_class.description" class="class-desc">{{ classData.school_class.description }}</p>
        </div>
      </div>

      <div v-else class="card empty-card">
        <p class="empty-title">No Active Class Enrollment</p>
        <p class="empty-desc">You are not currently enrolled in a class for the selected academic year ({{ selectedYear }}).</p>
      </div>

      <!-- 2. Enrolled Subjects Grid -->
      <div class="section-container">
        <div class="section-title-row">
          <h3 class="section-title">Enrolled Academic Subjects</h3>
          <span class="badge-count">{{ classData.subjects.length }} Subjects</span>
        </div>

        <div v-if="classData.subjects.length === 0" class="card empty-card">
          <p class="empty-title">No Subjects Assigned</p>
          <p class="empty-desc">There are no syllabus subjects assigned to this grade level yet.</p>
        </div>

        <div v-else class="subjects-grid">
          <div v-for="s in classData.subjects" :key="s.id" class="card subject-card">
            <div class="subject-top">
              <span class="dept-badge">{{ s.department || 'General' }}</span>
              <span class="code-badge">{{ s.code }}</span>
            </div>
            <h4 class="subject-name">{{ s.name }}</h4>
            <div class="subject-faculty">
              <span class="faculty-lbl">Teacher:</span>
              <strong class="faculty-val">{{ s.teacher_name || 'Faculty Member' }}</strong>
            </div>
            <div class="subject-status">
              <span class="status-pill active">{{ s.status }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. Academic Year History -->
      <div class="section-container">
        <div class="section-title-row">
          <h3 class="section-title">Academic Year Enrollment History</h3>
          <span class="badge-count">{{ classData.enrollment_history.length }} Years</span>
        </div>

        <div v-if="classData.enrollment_history.length === 0" class="card empty-card">
          <p class="empty-desc">No previous academic enrollment history found.</p>
        </div>

        <div v-else class="history-timeline">
          <div
            v-for="(hist, idx) in classData.enrollment_history"
            :key="idx"
            class="card timeline-card"
            :class="{ current: hist.academic_year === selectedYear }"
          >
            <div class="timeline-year-box">
              <span class="year-val">{{ hist.academic_year }}</span>
              <span v-if="hist.academic_year === selectedYear" class="current-tag">Selected</span>
            </div>
            <div class="timeline-details">
              <h4 class="timeline-class">{{ hist.class_name }} ({{ hist.class_code }})</h4>
              <p class="timeline-meta">
                Section: {{ hist.section || 'General' }} &bull; Roll Number: {{ hist.roll_number || '—' }} &bull; Status:
                <strong class="text-emerald">{{ hist.status }}</strong>
              </p>
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

.header-content-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1rem;
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

/* Year Selector */
.year-selector-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  padding: 0.4rem 0.75rem;
  border-radius: 8px;
}

.selector-lbl {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
}

.year-select {
  background: var(--bg-surface-secondary);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
  padding: 0.35rem 0.65rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  outline: none;
  cursor: pointer;
}

.content-stack {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}

/* Class Hero Card */
.class-hero-card {
  padding: 1.5rem 2rem;
  border-left: 4px solid #10b981;
  background: linear-gradient(135deg, var(--bg-surface) 0%, rgba(16, 185, 129, 0.08) 100%);
  border: 1px solid var(--border-subtle);
  border-left-width: 4px;
}

.hero-top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.grade-badge {
  background-color: rgba(16, 185, 129, 0.15);
  color: #10b981;
  font-size: 0.82rem;
  font-weight: 800;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  text-transform: uppercase;
}

.year-badge {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-muted);
}

.class-title {
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0.25rem 0;
}

.class-meta-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.85rem;
  color: var(--text-secondary);
  flex-wrap: wrap;
  margin: 0.35rem 0;
}

.meta-item strong {
  color: var(--text-primary);
}

.meta-sep {
  color: var(--border-subtle);
}

.class-desc {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin: 0.5rem 0 0 0;
  line-height: 1.45;
}

/* Subjects Grid */
.section-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.section-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-size: 1.2rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}

.badge-count {
  font-size: 0.75rem;
  font-weight: 700;
  background-color: var(--bg-surface-secondary);
  color: var(--text-muted);
  padding: 0.2rem 0.55rem;
  border-radius: 12px;
}

.subjects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1rem;
}

.subject-card {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-top: 3px solid #10b981;
}

.subject-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dept-badge {
  font-size: 0.72rem;
  background-color: var(--bg-surface-secondary);
  color: var(--text-secondary);
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.code-badge {
  font-size: 0.75rem;
  font-family: monospace;
  font-weight: 700;
  color: #10b981;
}

.subject-name {
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}

.subject-faculty {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.82rem;
}

.faculty-lbl {
  color: var(--text-muted);
}

.faculty-val {
  color: var(--text-primary);
}

.subject-status {
  margin-top: auto;
  padding-top: 0.5rem;
  border-top: 1px dashed var(--border-subtle);
}

.status-pill {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.status-pill.active {
  background-color: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

/* Timeline */
.history-timeline {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.timeline-card {
  padding: 1rem 1.25rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
}

.timeline-card.current {
  border-left: 4px solid #10b981;
  background: linear-gradient(135deg, var(--bg-surface) 0%, rgba(16, 185, 129, 0.05) 100%);
}

.timeline-year-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
  min-width: 100px;
}

.year-val {
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--text-primary);
}

.current-tag {
  font-size: 0.68rem;
  font-weight: 700;
  background-color: rgba(16, 185, 129, 0.15);
  color: #10b981;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}

.timeline-details {
  flex: 1;
}

.timeline-class {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.timeline-meta {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin: 0.2rem 0 0 0;
}

.text-emerald {
  color: #10b981;
}

/* Common states */
.loading-card, .error-card, .empty-card {
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

@keyframes spin { to { transform: rotate(360deg); } }

.empty-title, .error-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.empty-desc, .error-desc {
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

@media (max-width: 640px) {
  .header-content-row {
    flex-direction: column;
  }
  .timeline-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  .timeline-year-box {
    flex-direction: row;
    align-items: center;
    gap: 0.5rem;
  }
}
</style>
