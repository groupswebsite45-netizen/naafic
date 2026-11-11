<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { studentPortalService } from '../../services/studentPortalService';
import { StudentDashboardData } from '../../types/studentPortal';

const router = useRouter();
const dashboardData = ref<StudentDashboardData | null>(null);
const isLoading = ref(true);
const errorMessage = ref('');

async function loadDashboard() {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    dashboardData.value = await studentPortalService.getDashboard();
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to load student dashboard.';
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
  <div class="student-dashboard">
    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state card">
      <div class="spinner" />
      <span>Querying real student records from PostgreSQL...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage" class="alert-box error card">
      <div class="error-content">
        <strong class="error-title">Unable to Load Dashboard</strong>
        <p class="error-msg">{{ errorMessage }}</p>
      </div>
      <button class="retry-btn" @click="loadDashboard">Try Again</button>
    </div>

    <!-- Dashboard Content -->
    <div v-else-if="dashboardData" class="dashboard-content-stack">
      <!-- 1. Hero Welcome Banner -->
      <div class="welcome-banner card">
        <div class="welcome-left">
          <span class="portal-badge">STUDENT PORTAL &bull; EDUCATION MANAGEMENT SYSTEM</span>
          <h2 class="welcome-heading">
            Welcome back, {{ dashboardData.student.first_name }} {{ dashboardData.student.last_name }}
          </h2>
          <div class="welcome-meta">
            <span class="meta-pill">
              Admission: <strong>{{ dashboardData.student.admission_number }}</strong>
            </span>
            <span class="meta-sep">&bull;</span>
            <span class="meta-pill">
              Class: <strong>{{ dashboardData.current_class ? dashboardData.current_class.name : 'Not enrolled' }}</strong>
            </span>
            <span class="meta-sep">&bull;</span>
            <span class="meta-pill">
              Academic Year: <strong>{{ dashboardData.academic_year || '2025-2026' }}</strong>
            </span>
          </div>
        </div>
        <div class="welcome-right">
          <button class="quick-profile-btn" @click="navigateTo('/student/profile')">
            My Profile &rarr;
          </button>
        </div>
      </div>

      <!-- 2. 6 Summary Cards Grid -->
      <div class="summary-cards-grid">
        <!-- Card 1: Current Class -->
        <div class="kpi-card card blue" @click="navigateTo('/student/class')">
          <div class="kpi-top">
            <span class="kpi-label">CURRENT CLASS</span>
            <svg class="kpi-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <div class="kpi-val">{{ dashboardData.current_class ? dashboardData.current_class.name : 'Unassigned' }}</div>
          <div class="kpi-sub">
            Section: {{ dashboardData.current_class?.section || 'Section A' }}
          </div>
        </div>

        <!-- Card 2: Enrolled Subjects -->
        <div class="kpi-card card green" @click="navigateTo('/student/class')">
          <div class="kpi-top">
            <span class="kpi-label">ENROLLED SUBJECTS</span>
            <svg class="kpi-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <div class="kpi-val">{{ dashboardData.enrolled_subjects_count }}</div>
          <div class="kpi-sub">Active Curriculum Syllabus</div>
        </div>

        <!-- Card 3: Attendance Summary -->
        <div class="kpi-card card amber" @click="navigateTo('/student/attendance')">
          <div class="kpi-top">
            <span class="kpi-label">ATTENDANCE RATE</span>
            <svg class="kpi-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
          </div>
          <div class="kpi-val text-emerald">
            {{ dashboardData.attendance_summary ? `${dashboardData.attendance_summary.attendance_percentage}%` : '—' }}
          </div>
          <div class="kpi-sub">
            Present: {{ dashboardData.attendance_summary?.present_count || 0 }} &bull; Absent: {{ dashboardData.attendance_summary?.absent_count || 0 }}
          </div>
        </div>

        <!-- Card 4: Fees Summary -->
        <div class="kpi-card card red" @click="navigateTo('/student/fees')">
          <div class="kpi-top">
            <span class="kpi-label">OUTSTANDING FEES</span>
            <svg class="kpi-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="kpi-val" :class="dashboardData.outstanding_balance > 0 ? 'text-rose' : 'text-emerald'">
            ${{ Number(dashboardData.outstanding_balance).toFixed(2) }}
          </div>
          <div class="kpi-sub">
            ${{ Number(dashboardData.total_fees_paid).toFixed(2) }} Paid to date
          </div>
        </div>

        <!-- Card 5: Latest Released Exam Result -->
        <div class="kpi-card card purple" @click="navigateTo('/student/exams')">
          <div class="kpi-top">
            <span class="kpi-label">LATEST EXAM RESULT</span>
            <svg class="kpi-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div v-if="dashboardData.latest_exam_result" class="kpi-exam-content">
            <div class="kpi-val-text">{{ dashboardData.latest_exam_result.exam_name }}</div>
            <div class="kpi-sub">
              Grade: <strong>{{ dashboardData.latest_exam_result.grade || 'PASS' }}</strong> &bull; {{ dashboardData.latest_exam_result.percentage }}%
            </div>
          </div>
          <div v-else class="kpi-empty-text">
            No released results yet.
          </div>
        </div>

        <!-- Card 6: Next / Today's Class Period -->
        <div class="kpi-card card teal" @click="navigateTo('/student/timetable')">
          <div class="kpi-top">
            <span class="kpi-label">NEXT CLASS PERIOD</span>
            <svg class="kpi-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div v-if="dashboardData.next_class_period" class="kpi-period-content">
            <div class="kpi-val-text text-emerald">{{ dashboardData.next_class_period.subject?.name || dashboardData.next_class_period.subject_name || 'Scheduled Subject' }}</div>
            <div class="kpi-sub">
              {{ dashboardData.next_class_period.start_time }} - {{ dashboardData.next_class_period.end_time }} &bull; {{ dashboardData.next_class_period.room || dashboardData.next_class_period.room_number || 'Room TBD' }}
            </div>
          </div>
          <div v-else class="kpi-empty-text">
            No active periods scheduled.
          </div>
        </div>
      </div>

      <!-- 3. Today's Class Schedule -->
      <div class="card section-card">
        <div class="section-header">
          <div>
            <h3 class="section-title">Today's Class Schedule</h3>
            <p class="section-sub">Lectures scheduled for today according to the official timetable.</p>
          </div>
          <button class="view-all-link" @click="navigateTo('/student/timetable')">
            Full Weekly Timetable &rarr;
          </button>
        </div>

        <div v-if="dashboardData.today_schedule.length === 0" class="empty-schedule-box">
          <svg class="empty-clock-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p class="empty-msg">No class periods scheduled for today.</p>
          <span class="empty-sub">Enjoy your study time or check the weekly schedule for upcoming days.</span>
        </div>

        <div v-else class="table-responsive" tabindex="0" role="region" aria-label="Student portal table">
          <table class="portal-table">
            <thead>
              <tr>
                <th>Time</th>
                <th>Subject</th>
                <th>Teacher</th>
                <th>Room</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in dashboardData.today_schedule" :key="s.id">
                <td class="font-bold text-emerald">{{ s.start_time }} - {{ s.end_time }}</td>
                <td class="font-semibold">{{ s.subject?.name || s.subject_name || 'Subject' }}</td>
                <td>{{ s.teacher?.full_name || s.teacher_name || 'Assigned Faculty' }}</td>
                <td><span class="room-pill">{{ s.room || s.room_number || 'Classroom' }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 4. Recent Released Exam Results -->
      <div class="card section-card">
        <div class="section-header">
          <div>
            <h3 class="section-title">Official Released Examination Results</h3>
            <p class="section-sub">Recently published assessment scores approved and released by School Administration.</p>
          </div>
          <button class="view-all-link" @click="navigateTo('/student/exams')">
            View All Results &rarr;
          </button>
        </div>

        <div v-if="dashboardData.recent_exam_results.length === 0" class="empty-schedule-box">
          <svg class="empty-clock-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="empty-msg">No released examination results yet.</p>
          <span class="empty-sub">Exam marks are being processed and verified by School Administration.</span>
        </div>

        <div v-else class="table-responsive" tabindex="0" role="region" aria-label="Student portal table">
          <table class="portal-table">
            <thead>
              <tr>
                <th>Assessment</th>
                <th>Subject</th>
                <th>Marks</th>
                <th>Percentage</th>
                <th>Grade</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="res in dashboardData.recent_exam_results" :key="res.id">
                <td class="font-bold">{{ res.exam_name }}</td>
                <td>{{ res.subject_name }}</td>
                <td class="font-semibold">
                  <span v-if="res.marks_obtained !== null">{{ res.marks_obtained }} / {{ res.total_marks }}</span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td class="font-bold">
                  <span v-if="res.percentage !== null">{{ res.percentage }}%</span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td>
                  <span class="grade-pill" :class="res.grade === 'F' ? 'fail' : 'pass'">
                    {{ res.grade || 'PASS' }}
                  </span>
                </td>
                <td>
                  <span class="released-tag">Released</span>
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
.student-dashboard {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.dashboard-content-stack {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Welcome Banner */
.welcome-banner {
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, var(--bg-surface) 0%, rgba(16, 185, 129, 0.08) 100%);
  border-left: 4px solid #10b981;
  border: 1px solid var(--border-subtle);
  border-left-width: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.portal-badge {
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #10b981;
}

.welcome-heading {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0.25rem 0;
}

.welcome-meta {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.85rem;
  color: var(--text-muted);
  flex-wrap: wrap;
}

.meta-pill strong {
  color: var(--text-primary);
}

.meta-sep {
  color: var(--border-subtle);
}

.quick-profile-btn {
  background-color: var(--bg-surface-secondary);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
  font-size: 0.85rem;
  font-weight: 600;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-profile-btn:hover {
  background-color: #10b981;
  color: #fff;
  border-color: #10b981;
}

/* 6 KPI Cards Grid */
.summary-cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.kpi-card {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  border-left: 4px solid var(--brand-primary);
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-left-width: 4px;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

.kpi-card.blue { border-left-color: #0284c7; }
.kpi-card.green { border-left-color: #10b981; }
.kpi-card.amber { border-left-color: #f59e0b; }
.kpi-card.red { border-left-color: #ef4444; }
.kpi-card.purple { border-left-color: #8b5cf6; }
.kpi-card.teal { border-left-color: #14b8a6; }

.kpi-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.35rem;
}

.kpi-label {
  font-size: clamp(0.62rem, 2.2vw, 0.72rem);
  font-weight: 700;
  letter-spacing: 0.03em;
  line-height: 1.25;
  color: var(--text-muted);
}

.kpi-icon {
  width: 1.1rem;
  height: 1.1rem;
  flex-shrink: 0;
  color: var(--text-muted);
}

.kpi-val {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--text-primary);
}

.kpi-val-text {
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.kpi-sub {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.kpi-empty-text {
  font-size: 0.88rem;
  font-style: italic;
  color: var(--text-muted);
  margin: 0.2rem 0;
}

.text-emerald { color: #10b981; }
.text-rose { color: #ef4444; }

/* Sections */
.section-card {
  padding: 1.5rem;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.section-title {
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}

.section-sub {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin: 0.2rem 0 0 0;
}

.view-all-link {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  background: none;
  border: none;
  color: #10b981;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  padding: 0 0.25rem;
}

.view-all-link:hover {
  text-decoration: underline;
}

/* Empty Schedule */
.empty-schedule-box {
  padding: 2.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.empty-clock-icon {
  width: 2.5rem;
  height: 2.5rem;
  color: var(--text-muted);
}

.empty-msg {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.empty-sub {
  font-size: 0.8rem;
  color: var(--text-muted);
}

/* Tables */
.table-responsive {
  overflow-x: auto;
}

.portal-table {
  width: 100%;
  min-width: 640px;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.88rem;
}

.portal-table th,
.portal-table td {
  white-space: nowrap;
}

.portal-table th {
  background: var(--bg-surface-secondary);
  padding: 0.75rem 1rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border-subtle);
}

.portal-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-subtle);
  color: var(--text-primary);
}

.room-pill {
  background-color: var(--bg-surface-secondary);
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  font-size: 0.78rem;
  color: var(--text-secondary);
}

.grade-pill {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}

.grade-pill.pass {
  background-color: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.grade-pill.fail {
  background-color: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.released-tag {
  font-size: 0.72rem;
  font-weight: 700;
  background-color: rgba(2, 132, 199, 0.12);
  color: #0284c7;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

/* Loading & Error */
.loading-state {
  padding: 3.5rem;
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

.alert-box.error {
  background-color: rgba(239, 68, 68, 0.1);
  border-left: 4px solid #ef4444;
  padding: 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.error-title {
  color: #ef4444;
  font-weight: 700;
  display: block;
}

.error-msg {
  color: var(--text-secondary);
  font-size: 0.85rem;
  margin: 0.2rem 0 0 0;
}

.retry-btn {
  background-color: #ef4444;
  color: #fff;
  border: none;
  padding: 0.45rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

@media (max-width: 1024px) {
  .summary-cards-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .summary-cards-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.75rem;
  }
  .summary-card {
    padding: 0.85rem;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  .welcome-banner {
    padding: 1.25rem;
  }
}
</style>
