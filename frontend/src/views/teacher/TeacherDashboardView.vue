<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { teacherPortalService } from '../../services/teacherPortalService';
import { TeacherDashboardData } from '../../types/portal';
import StatusBadge from '../../components/common/StatusBadge.vue';
import ResultStatusBadge from '../../components/results/ResultStatusBadge.vue';

const router = useRouter();
const dashboardData = ref<TeacherDashboardData | null>(null);
const isLoading = ref(true);
const errorMessage = ref('');

async function loadDashboard() {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    const data = await teacherPortalService.getDashboard();
    dashboardData.value = data;
  } catch (err: any) {
    errorMessage.value = err.response?.data?.error?.message || err.response?.data?.detail || 'Failed to load teacher dashboard data.';
  } finally {
    isLoading.value = false;
  }
}

function navigateTo(path: string) {
  router.push(path);
}

onMounted(() => {
  loadDashboard();
});
</script>

<template>
  <div class="teacher-dashboard">
    <!-- Loading State -->
    <div v-if="isLoading" class="state-card loading">
      <div class="spinner-ring" />
      <span class="loading-label">Loading teacher portal dashboard metrics...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage" class="error-banner">
      <div class="error-icon-box">
        <svg viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
      </div>
      <div class="error-details">
        <h3 class="error-title">Unable to Load Dashboard</h3>
        <p class="error-desc">{{ errorMessage }}</p>
      </div>
      <button class="btn-retry" @click="loadDashboard">Try Again</button>
    </div>

    <div v-else-if="dashboardData" class="dashboard-content">
      <!-- 1. Somroyal Welcome Hero Card -->
      <div class="welcome-hero-card">
        <div class="welcome-main">
          <div class="somroyal-tag">
            <svg class="crown-icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M5 16L3 5l5.5 5L12 4l3.5 6L21 5l-2 11H5m14 3c0 .6-.4 1-1 1H6c-.6 0-1-.4-1-1v-1h14v1z"/>
            </svg>
            <span>FACULTY WORKSPACE &bull; INSTRUCTOR OVERVIEW</span>
          </div>

          <h1 class="welcome-name">
            Welcome back, {{ dashboardData.teacher.first_name }} {{ dashboardData.teacher.last_name }}
          </h1>

          <div class="faculty-meta-row">
            <div class="meta-item">
              <span class="meta-label">ID:</span>
              <code class="meta-code">{{ dashboardData.teacher.teacher_number }}</code>
            </div>
            <span class="meta-sep">&bull;</span>
            <div class="meta-item">
              <span class="meta-label">Qualification:</span>
              <span class="meta-val">{{ dashboardData.teacher.qualification || 'Educator' }}</span>
            </div>
            <span class="meta-sep">&bull;</span>
            <div class="meta-item">
              <span class="meta-label">Email:</span>
              <span class="meta-val">{{ dashboardData.teacher.email }}</span>
            </div>
          </div>
        </div>

        <div class="welcome-actions">
          <button class="btn-action primary" @click="navigateTo('/teacher/attendance')">
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
            <span>Take Today's Attendance</span>
          </button>

          <button class="btn-action secondary" @click="navigateTo('/teacher/exams')">
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z" />
              <path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clip-rule="evenodd" />
            </svg>
            <span>Enter Exam Marks</span>
          </button>
        </div>
      </div>

      <!-- 2. Responsive 4-KPI Grid (2x2 on mobile, 4 columns on desktop) -->
      <div class="kpi-grid">
        <div class="kpi-card blue" @click="navigateTo('/teacher/classes')">
          <div class="kpi-icon-wrap blue">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <div class="kpi-details">
            <span class="kpi-label">ASSIGNED CLASSES</span>
            <span class="kpi-value">{{ dashboardData.total_classes }}</span>
            <span class="kpi-hint">Class Grade Sections &rarr;</span>
          </div>
        </div>

        <div class="kpi-card emerald" @click="navigateTo('/teacher/classes')">
          <div class="kpi-icon-wrap emerald">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <div class="kpi-details">
            <span class="kpi-label">ASSIGNED SUBJECTS</span>
            <span class="kpi-value text-emerald">{{ dashboardData.total_subjects }}</span>
            <span class="kpi-hint">Curriculum Disciplines &rarr;</span>
          </div>
        </div>

        <div class="kpi-card purple" @click="navigateTo('/teacher/students')">
          <div class="kpi-icon-wrap purple">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
          <div class="kpi-details">
            <span class="kpi-label">ASSIGNED STUDENTS</span>
            <span class="kpi-value">{{ dashboardData.total_students }}</span>
            <span class="kpi-hint">Enrolled Under You &rarr;</span>
          </div>
        </div>

        <div class="kpi-card amber" @click="navigateTo('/teacher/exams')">
          <div class="kpi-icon-wrap amber">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
          </div>
          <div class="kpi-details">
            <span class="kpi-label">PENDING RESULTS</span>
            <span class="kpi-value text-amber">{{ dashboardData.pending_results_count ?? 0 }}</span>
            <span class="kpi-hint">Requires Submission &rarr;</span>
          </div>
        </div>
      </div>

      <!-- 3. Two-Column Workload Widgets -->
      <div class="widgets-split-grid">
        <!-- Widget 1: Today's Class Attendance -->
        <div class="panel-card">
          <div class="panel-header">
            <div>
              <h3 class="panel-title">Today's Class Attendance</h3>
              <p class="panel-subtitle">Daily attendance status for assigned classes today.</p>
            </div>
            <button class="btn-link" @click="navigateTo('/teacher/attendance')">
              <span>Open Module</span>
              <svg viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>

          <div v-if="!dashboardData.today_attendance_summary || dashboardData.today_attendance_summary.length === 0" class="empty-inline">
            No active class assignments scheduled for attendance today.
          </div>
          <div v-else class="attendance-items-list">
            <div
              v-for="item in dashboardData.today_attendance_summary"
              :key="`${item.class_id}_${item.subject_id}`"
              class="attendance-item-card"
              :class="{ recorded: item.is_recorded }"
            >
              <div class="att-info">
                <h4 class="att-class-name">{{ item.class_name }}</h4>
                <span class="att-subject-name">{{ item.subject_name }}</span>
              </div>

              <div class="att-status-col">
                <span v-if="item.is_recorded" class="status-pill-att recorded">
                  <span class="dot green" />
                  <span>Recorded ({{ item.present_count }}/{{ item.total_students }})</span>
                </span>
                <span v-else class="status-pill-att pending">
                  <span class="dot amber" />
                  <span>Pending ({{ item.total_students }} Students)</span>
                </span>
              </div>

              <button
                class="btn-att-action"
                :class="item.is_recorded ? 'outline' : 'primary'"
                @click="navigateTo('/teacher/attendance')"
              >
                {{ item.is_recorded ? 'View/Edit' : 'Take Attendance' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Widget 2: Pending Result Submissions -->
        <div class="panel-card">
          <div class="panel-header">
            <div>
              <h3 class="panel-title">Pending Result Submissions</h3>
              <p class="panel-subtitle">Active exam mark entry workloads requiring review.</p>
            </div>
            <button class="btn-link" @click="navigateTo('/teacher/exams')">
              <span>Open Exams</span>
              <svg viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>

          <div v-if="!dashboardData.pending_submissions || dashboardData.pending_submissions.length === 0" class="empty-inline">
            No pending exam results requiring submission. All marks up to date!
          </div>
          <div v-else class="pending-sub-list">
            <div
              v-for="sub in dashboardData.pending_submissions.slice(0, 4)"
              :key="`${sub.exam_id}_${sub.class_id}_${sub.subject_id}`"
              class="pending-sub-item"
            >
              <div class="pending-head">
                <div class="pending-title-row">
                  <h4 class="pending-exam-name">{{ sub.exam_name }}</h4>
                  <ResultStatusBadge :status="sub.status" />
                </div>
                <span class="pending-scope">{{ sub.class_name }} &bull; {{ sub.subject_name }}</span>
              </div>

              <div class="pending-progress-section">
                <div class="progress-labels">
                  <span class="progress-txt">Mark Entry</span>
                  <strong class="progress-nums">{{ sub.completed_students }} / {{ sub.total_students }}</strong>
                </div>
                <div class="progress-bar-track">
                  <div
                    class="progress-bar-fill"
                    :style="{ width: `${sub.total_students > 0 ? (sub.completed_students / sub.total_students) * 100 : 0}%` }"
                  />
                </div>
              </div>

              <button class="btn-sub-enter" @click="navigateTo('/teacher/exams')">
                Enter Marks &rarr;
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 4. Weekly Teaching Schedule -->
      <div class="panel-card">
        <div class="panel-header">
          <div>
            <h3 class="panel-title">Weekly Teaching Schedule</h3>
            <p class="panel-subtitle">Scheduled lecture periods across your assigned grade streams.</p>
          </div>
          <button class="btn-link" @click="navigateTo('/teacher/timetable')">
            <span>Full Timetable</span>
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>

        <div v-if="dashboardData.upcoming_timetables.length === 0" class="empty-inline">
          No class periods scheduled for your profile.
        </div>
        <div v-else class="table-responsive-wrapper">
          <table class="somroyal-table">
            <thead>
              <tr>
                <th>Day &amp; Time</th>
                <th>Class / Stream</th>
                <th>Subject</th>
                <th>Assigned Room</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in dashboardData.upcoming_timetables" :key="s.id">
                <td class="font-bold text-navy">
                  <span class="day-tag">{{ s.day_of_week }}</span>
                  <span class="time-range">{{ s.start_time }} &ndash; {{ s.end_time }}</span>
                </td>
                <td class="font-semibold text-slate-800">{{ s.class_name }}</td>
                <td>
                  <span class="subj-pill">{{ s.subject_name }}</span>
                </td>
                <td>
                  <span class="room-pill">{{ s.room_number || 'Room TBD' }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 5. Upcoming Scheduled Examinations -->
      <div class="panel-card">
        <div class="panel-header">
          <div>
            <h3 class="panel-title">Upcoming / Scheduled Examinations</h3>
            <p class="panel-subtitle">Active examination schedules across your teaching curriculum.</p>
          </div>
          <button class="btn-link" @click="navigateTo('/teacher/exams')">
            <span>All Exams</span>
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>

        <div v-if="dashboardData.active_exams.length === 0" class="empty-inline">
          No upcoming examinations currently scheduled for your classes.
        </div>
        <div v-else class="table-responsive-wrapper">
          <table class="somroyal-table">
            <thead>
              <tr>
                <th>Examination Name</th>
                <th>Class</th>
                <th>Subject</th>
                <th>Max Marks</th>
                <th>Exam Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="ex in dashboardData.active_exams" :key="ex.id">
                <td class="font-bold text-navy">{{ ex.name }}</td>
                <td class="font-semibold text-slate-800">{{ ex.class_name }}</td>
                <td>
                  <span class="subj-pill">{{ ex.subject_name }}</span>
                </td>
                <td class="font-semibold text-slate-700">{{ ex.max_marks }} Marks</td>
                <td>
                  <StatusBadge :status="ex.status" :variant="ex.status === 'ONGOING' ? 'warning' : 'info'" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.teacher-dashboard {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 1300px;
  margin: 0 auto;
  width: 100%;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 1. Welcome Hero Card (Admin Brand Gradient) */
.welcome-hero-card {
  background: linear-gradient(135deg, #071E46 0%, #0D47A1 45%, #0284C7 100%);
  border-radius: 16px;
  padding: 1.75rem 2rem;
  color: #FFFFFF;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 12px 30px -6px rgba(7, 30, 70, 0.35);
  position: relative;
  overflow: hidden;
}

.welcome-hero-card::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 320px;
  background: radial-gradient(circle at right, rgba(2, 132, 199, 0.25) 0%, transparent 70%);
  pointer-events: none;
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
  margin-bottom: 0.4rem;
}

.crown-icon {
  width: 14px;
  height: 14px;
  color: #F59E0B;
}

.welcome-name {
  font-size: 1.65rem;
  font-weight: 800;
  color: #FFFFFF;
  letter-spacing: -0.02em;
  margin: 0;
}

.faculty-meta-row {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  font-size: 0.84rem;
  color: #94A3B8;
  margin-top: 0.5rem;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.meta-label {
  color: #64748B;
  font-size: 0.78rem;
}

.meta-code {
  font-family: monospace;
  font-weight: 700;
  color: #F59E0B;
  background: rgba(245, 158, 11, 0.15);
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}

.meta-val {
  color: #E2E8F0;
  font-weight: 600;
}

.meta-sep {
  color: #475569;
}

.welcome-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  z-index: 1;
}

.btn-action {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1.15rem;
  border-radius: 10px;
  font-size: 0.84rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-action svg {
  width: 16px;
  height: 16px;
}

.btn-action.primary {
  background: #1E3A8A;
  color: #FFFFFF;
  border: none;
  box-shadow: 0 4px 12px rgba(30, 58, 138, 0.3);
}

.btn-action.primary:hover {
  background: #1E40AF;
  transform: translateY(-1px);
}

.btn-action.secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #FFFFFF;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(8px);
}

.btn-action.secondary:hover {
  background: rgba(255, 255, 255, 0.18);
  transform: translateY(-1px);
}

/* 2. KPI Cards Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.15rem;
}

.kpi-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 14px;
  padding: 1.25rem;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 6px rgba(10, 25, 47, 0.03);
}

.kpi-card:hover {
  border-color: #CBD5E1;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(10, 25, 47, 0.06);
}

.kpi-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kpi-icon-wrap svg {
  width: 22px;
  height: 22px;
}

.kpi-icon-wrap.blue {
  background: #EFF6FF;
  color: #2563EB;
}

.kpi-icon-wrap.emerald {
  background: #ECFDF5;
  color: #059669;
}

.kpi-icon-wrap.purple {
  background: #F5F3FF;
  color: #7C3AED;
}

.kpi-icon-wrap.amber {
  background: #FEF3C7;
  color: #D97706;
}

.kpi-details {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.kpi-label {
  font-size: 0.68rem;
  font-weight: 800;
  color: #64748B;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.kpi-value {
  font-size: 1.65rem;
  font-weight: 900;
  color: #0A192F;
  line-height: 1.2;
}

.kpi-hint {
  font-size: 0.72rem;
  color: #94A3B8;
  font-weight: 600;
  margin-top: 0.2rem;
}

.text-emerald {
  color: #059669 !important;
}

.text-amber {
  color: #D97706 !important;
}

/* 3. Workload Widgets Split Grid */
.widgets-split-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}

.panel-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
  box-shadow: 0 2px 6px rgba(10, 25, 47, 0.03);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.panel-title {
  font-size: 1.15rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
}

.panel-subtitle {
  font-size: 0.8rem;
  color: #64748B;
  margin: 0.2rem 0 0 0;
}

.btn-link {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  background: none;
  border: none;
  color: #2563EB;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.btn-link:hover {
  background: #EFF6FF;
  color: #1D4ED8;
}

.btn-link svg {
  width: 14px;
  height: 14px;
}

.empty-inline {
  padding: 2rem 1rem;
  text-align: center;
  font-size: 0.86rem;
  color: #64748B;
  background: #F8FAFC;
  border-radius: 10px;
  border: 1px dashed #CBD5E1;
}

/* Attendance list */
.attendance-items-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.attendance-item-card {
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 0.9rem 1.15rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  transition: all 0.2s ease;
}

.attendance-item-card.recorded {
  background: #F0FDF4;
  border-color: #BBF7D0;
}

.att-info {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.att-class-name {
  font-size: 0.95rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
}

.att-subject-name {
  font-size: 0.76rem;
  color: #64748B;
  font-weight: 600;
}

.status-pill-att {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.25rem 0.6rem;
  border-radius: 20px;
  white-space: nowrap;
}

.status-pill-att.recorded {
  background: #ECFDF5;
  color: #065F46;
  border: 1px solid #A7F3D0;
}

.status-pill-att.pending {
  background: #FEF3C7;
  color: #92400E;
  border: 1px solid #FDE68A;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.dot.green { background: #10B981; }
.dot.amber { background: #F59E0B; }

.btn-att-action {
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0.4rem 0.85rem;
  border-radius: 8px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.btn-att-action.primary {
  background: #1E3A8A;
  color: #FFFFFF;
  border: none;
}

.btn-att-action.primary:hover {
  background: #1E40AF;
}

.btn-att-action.outline {
  background: #FFFFFF;
  color: #0A192F;
  border: 1px solid #CBD5E1;
}

.btn-att-action.outline:hover {
  background: #F1F5F9;
  border-color: #94A3B8;
}

/* Pending submissions list */
.pending-sub-list {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.pending-sub-item {
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 1rem 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.pending-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.pending-exam-name {
  font-size: 0.95rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
}

.pending-scope {
  font-size: 0.76rem;
  color: #64748B;
  font-weight: 600;
}

.pending-progress-section {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.progress-labels {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.74rem;
}

.progress-txt {
  color: #64748B;
  font-weight: 600;
}

.progress-nums {
  color: #0A192F;
  font-weight: 700;
}

.progress-bar-track {
  width: 100%;
  height: 6px;
  background: #E2E8F0;
  border-radius: 10px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #10B981, #059669);
  border-radius: 10px;
  transition: width 0.3s ease;
}

.btn-sub-enter {
  align-self: flex-end;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  color: #0A192F;
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  font-size: 0.76rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-sub-enter:hover {
  background: #0A192F;
  color: #FFFFFF;
  border-color: #0A192F;
}

/* 4 & 5 Tables */
.table-responsive-wrapper {
  overflow-x: auto;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
}

.somroyal-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.86rem;
  text-align: left;
}

.somroyal-table thead {
  background: #0A192F;
  color: #FFFFFF;
}

.somroyal-table th {
  padding: 0.85rem 1rem;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #1E293B;
}

.somroyal-table td {
  padding: 0.9rem 1rem;
  border-bottom: 1px solid #F1F5F9;
  color: #1E293B;
  vertical-align: middle;
}

.somroyal-table tbody tr:hover {
  background: #F8FAFC;
}

.text-navy {
  color: #0A192F;
}

.day-tag {
  font-weight: 800;
  margin-right: 0.35rem;
}

.time-range {
  font-size: 0.78rem;
  color: #64748B;
  font-weight: 600;
}

.subj-pill {
  font-size: 0.76rem;
  font-weight: 700;
  background: #EFF6FF;
  color: #1E40AF;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
}

.room-pill {
  font-size: 0.74rem;
  font-weight: 700;
  background: #F1F5F9;
  color: #475569;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
}

/* Common States */
.state-card {
  background: #FFFFFF;
  border-radius: 16px;
  border: 1px solid #E2E8F0;
  padding: 4rem 1.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.85rem;
}

.spinner-ring {
  width: 36px;
  height: 36px;
  border: 3px solid #E2E8F0;
  border-top-color: #10B981;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-label {
  font-size: 0.88rem;
  color: #64748B;
  font-weight: 600;
}

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

/* Responsive Rules */
@media (max-width: 1024px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .widgets-split-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .welcome-hero-card {
    padding: 1.5rem;
  }
  .welcome-actions {
    width: 100%;
  }
  .btn-action {
    flex: 1;
    justify-content: center;
  }
  .kpi-grid {
    grid-template-columns: 1fr;
  }
  .attendance-item-card {
    flex-direction: column;
    align-items: flex-start;
  }
  .btn-att-action {
    width: 100%;
    text-align: center;
  }
}
</style>
