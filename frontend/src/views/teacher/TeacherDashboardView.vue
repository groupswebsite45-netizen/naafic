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
    <div v-if="isLoading" class="loading-state card">
      <div class="spinner" />
      <span>Loading teacher portal dashboard metrics...</span>
    </div>

    <div v-else-if="errorMessage" class="alert-box error">
      {{ errorMessage }}
    </div>

    <div v-else-if="dashboardData" class="dashboard-grid-layout">
      <!-- Welcome Card -->
      <div class="welcome-card card">
        <div class="welcome-left">
          <span class="badge-role">Education Management System Faculty Portal</span>
          <h2 class="welcome-name">
            Welcome, {{ dashboardData.teacher.first_name }} {{ dashboardData.teacher.last_name }}
          </h2>
          <p class="welcome-sub">
            Faculty ID: <code>{{ dashboardData.teacher.teacher_number }}</code>
            <span class="sub-sep">•</span>
            <span>Qualification: {{ dashboardData.teacher.qualification || 'Educator' }}</span>
            <span class="sub-sep">•</span>
            <span>Email: {{ dashboardData.teacher.email }}</span>
          </p>
        </div>
        <div class="welcome-quick-actions">
          <button class="btn btn-primary btn-touch" @click="navigateTo('/teacher/attendance')">
            <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Take Today's Attendance
          </button>
          <button class="btn btn-outline btn-touch" @click="navigateTo('/teacher/exams')">
            <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            Enter Exam Marks
          </button>
        </div>
      </div>

      <!-- Quick Metrics Grid -->
      <div class="metrics-grid">
        <div class="metric-card card blue" @click="navigateTo('/teacher/classes')">
          <span class="metric-label">Assigned Classes</span>
          <span class="metric-val">{{ dashboardData.total_classes }}</span>
          <span class="metric-sub">Class Grade Sections</span>
        </div>
        <div class="metric-card card green" @click="navigateTo('/teacher/classes')">
          <span class="metric-label">Assigned Subjects</span>
          <span class="metric-val">{{ dashboardData.total_subjects }}</span>
          <span class="metric-sub">Curriculum Areas</span>
        </div>
        <div class="metric-card card purple" @click="navigateTo('/teacher/students')">
          <span class="metric-label">Assigned Students</span>
          <span class="metric-val">{{ dashboardData.total_students }}</span>
          <span class="metric-sub">Enrolled in Your Classes</span>
        </div>
        <div class="metric-card card amber" @click="navigateTo('/teacher/exams')">
          <span class="metric-label">Pending Result Sets</span>
          <span class="metric-val">{{ dashboardData.pending_results_count ?? 0 }}</span>
          <span class="metric-sub">Drafts / Awaiting Submission</span>
        </div>
      </div>

      <!-- Two Column Widgets: Today's Attendance & Pending Submissions -->
      <div class="widgets-split-grid">
        <!-- Widget 1: Today's Attendance -->
        <div class="section-card card">
          <div class="section-header">
            <div>
              <h3 class="section-title">Today's Class Attendance</h3>
              <p class="section-sub-text">Daily attendance logs for assigned classes today.</p>
            </div>
            <button class="btn btn-sm btn-outline" @click="navigateTo('/teacher/attendance')">
              Open Module &rarr;
            </button>
          </div>

          <div v-if="!dashboardData.today_attendance_summary || dashboardData.today_attendance_summary.length === 0" class="empty-inline">
            No active class assignments found.
          </div>
          <div v-else class="attendance-widget-list">
            <div
              v-for="item in dashboardData.today_attendance_summary"
              :key="`${item.class_id}_${item.subject_id}`"
              class="att-item-row"
              :class="{ 'is-recorded': item.is_recorded }"
            >
              <div class="att-item-main">
                <span class="att-class-name">{{ item.class_name }}</span>
                <span class="att-sub-name">{{ item.subject_name }}</span>
              </div>

              <div class="att-item-status">
                <span v-if="item.is_recorded" class="status-chip recorded">
                  ✓ Recorded ({{ item.present_count }}/{{ item.total_students }} Present)
                </span>
                <span v-else class="status-chip pending">
                  ● Pending ({{ item.total_students }} Students)
                </span>
              </div>

              <button
                class="btn btn-xs btn-touch"
                :class="item.is_recorded ? 'btn-outline' : 'btn-primary'"
                @click="navigateTo('/teacher/attendance')"
              >
                {{ item.is_recorded ? 'View/Edit' : 'Take Attendance' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Widget 2: Pending Result Submissions -->
        <div class="section-card card">
          <div class="section-header">
            <div>
              <h3 class="section-title">Pending Result Submissions</h3>
              <p class="section-sub-text">Active exam mark entry workloads requiring teacher review.</p>
            </div>
            <button class="btn btn-sm btn-outline" @click="navigateTo('/teacher/exams')">
              Open Exams &rarr;
            </button>
          </div>

          <div v-if="!dashboardData.pending_submissions || dashboardData.pending_submissions.length === 0" class="empty-inline">
            No pending exam results requiring submission.
          </div>
          <div v-else class="pending-sub-list">
            <div
              v-for="sub in dashboardData.pending_submissions.slice(0, 4)"
              :key="`${sub.exam_id}_${sub.class_id}_${sub.subject_id}`"
              class="pending-sub-row"
            >
              <div class="pending-sub-main">
                <div class="pending-title-wrap">
                  <span class="pending-exam-name">{{ sub.exam_name }}</span>
                  <ResultStatusBadge :status="sub.status" />
                </div>
                <span class="pending-scope">{{ sub.class_name }} • {{ sub.subject_name }}</span>
              </div>

              <div class="pending-progress-wrap">
                <span class="progress-count">{{ sub.completed_students }} / {{ sub.total_students }} Completed</span>
                <div class="progress-bar-bg">
                  <div
                    class="progress-bar-fill"
                    :style="{ width: `${sub.total_students > 0 ? (sub.completed_students / sub.total_students) * 100 : 0}%` }"
                  />
                </div>
              </div>

              <button class="btn btn-xs btn-outline btn-touch" @click="navigateTo('/teacher/exams')">
                Enter Marks
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Upcoming Teaching Schedule -->
      <div class="section-card card">
        <div class="section-header">
          <div>
            <h3 class="section-title">Weekly Teaching Schedule</h3>
            <p class="section-sub-text">Scheduled class periods and lecture times.</p>
          </div>
          <button class="btn btn-sm btn-outline" @click="navigateTo('/teacher/timetable')">
            Full Timetable &rarr;
          </button>
        </div>
        <div v-if="dashboardData.upcoming_timetables.length === 0" class="empty-inline">
          No class periods scheduled.
        </div>
        <div v-else class="table-responsive" tabindex="0" role="region" aria-label="Teacher portal table">
          <table class="portal-table">
            <thead>
              <tr>
                <th>Day & Time</th>
                <th>Class</th>
                <th>Subject</th>
                <th>Room</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in dashboardData.upcoming_timetables" :key="s.id">
                <td class="font-bold text-primary">{{ s.day_of_week }} {{ s.start_time }} - {{ s.end_time }}</td>
                <td>{{ s.class_name }}</td>
                <td>{{ s.subject_name }}</td>
                <td><span class="room-badge">{{ s.room_number || 'Room TBD' }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Upcoming Scheduled Examinations -->
      <div class="section-card card">
        <div class="section-header">
          <div>
            <h3 class="section-title">Upcoming / Scheduled Examinations</h3>
            <p class="section-sub-text">Active exam schedules across your assigned streams.</p>
          </div>
        </div>
        <div v-if="dashboardData.active_exams.length === 0" class="empty-inline">
          No upcoming exams scheduled for your assigned classes.
        </div>
        <div v-else class="table-responsive" tabindex="0" role="region" aria-label="Teacher portal table">
          <table class="portal-table">
            <thead>
              <tr>
                <th>Exam Name</th>
                <th>Class</th>
                <th>Subject</th>
                <th>Max Marks</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="ex in dashboardData.active_exams" :key="ex.id">
                <td class="font-bold">{{ ex.name }}</td>
                <td>{{ ex.class_name }}</td>
                <td>{{ ex.subject_name }}</td>
                <td>{{ ex.max_marks }} Marks</td>
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
  box-sizing: border-box;
}

.dashboard-grid-layout {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.welcome-card {
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
  border-left: 4px solid #0284c7;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1.25rem;
  width: 100%;
  box-sizing: border-box;
}

.welcome-left {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 0;
}

.badge-role {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #0284c7;
  letter-spacing: 0.05em;
}

.welcome-name {
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--text-primary, #0f172a);
  margin: 0;
  word-break: break-word;
}

.welcome-sub {
  font-size: 0.85rem;
  color: var(--text-muted, #64748b);
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  min-width: 0;
  max-width: 100%;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.sub-sep {
  color: var(--border-medium, #cbd5e1);
}

.welcome-quick-actions {
  display: flex;
  gap: 0.65rem;
  flex-wrap: wrap;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  width: 100%;
}

.metric-card {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  border-left: 4px solid var(--brand-primary, #0284c7);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  width: 100%;
  box-sizing: border-box;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.metric-card.green { border-left-color: #10b981; }
.metric-card.purple { border-left-color: #8b5cf6; }
.metric-card.amber { border-left-color: #f59e0b; }

.metric-label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted, #64748b);
}

.metric-val {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--text-primary, #0f172a);
}

.metric-sub {
  font-size: 0.75rem;
  color: var(--text-secondary, #475569);
}

.widgets-split-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
  width: 100%;
}

.section-card {
  padding: 1.25rem;
  width: 100%;
  box-sizing: border-box;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary, #0f172a);
}

.section-sub-text {
  font-size: 0.8rem;
  color: var(--text-muted, #64748b);
  margin: 0.15rem 0 0 0;
}

.attendance-widget-list, .pending-sub-list {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.att-item-row, .pending-sub-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0.85rem;
  background: var(--bg-surface-secondary, #f8fafc);
  border-radius: 8px;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.att-item-row.is-recorded {
  border-left: 3px solid #10b981;
}

.att-item-main {
  display: flex;
  flex-direction: column;
  min-width: 140px;
}

.att-class-name {
  font-weight: 700;
  font-size: 0.9rem;
  color: var(--text-primary, #0f172a);
}

.att-sub-name {
  font-size: 0.78rem;
  color: var(--text-muted, #64748b);
}

.status-chip {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
}

.status-chip.recorded { background: #dcfce7; color: #166534; }
.status-chip.pending { background: #fef3c7; color: #92400e; }

.pending-sub-main {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  flex: 1;
  min-width: 140px;
}

.pending-title-wrap {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.pending-exam-name {
  font-weight: 700;
  font-size: 0.88rem;
  color: var(--text-primary, #0f172a);
}

.pending-scope {
  font-size: 0.78rem;
  color: var(--text-muted, #64748b);
}

.pending-progress-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 120px;
}

.progress-count {
  font-size: 0.72rem;
  color: var(--text-muted, #64748b);
  text-align: right;
}

.progress-bar-bg {
  width: 100%;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: #0284c7;
  border-radius: 3px;
}

.table-responsive {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.portal-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.88rem;
  min-width: 480px;
}

.portal-table th {
  background: var(--bg-surface-secondary, #f8fafc);
  padding: 0.75rem 1rem;
  font-weight: 700;
  color: var(--text-secondary, #475569);
  border-bottom: 1px solid var(--border-subtle, #e2e8f0);
}

.portal-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-subtle, #e2e8f0);
  color: var(--text-primary, #0f172a);
}

.room-badge {
  background: #f1f5f9;
  color: #475569;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  font-size: 0.75rem;
}

.font-bold { font-weight: 700; }
.text-primary { color: #0284c7; }
.empty-inline { font-size: 0.85rem; color: var(--text-muted, #64748b); font-style: italic; padding: 1rem 0; }

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.55rem 0.9rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s;
}

.btn-touch {
  min-height: 44px;
}

.btn-primary { background: #0284c7; color: #ffffff; }
.btn-primary:hover { background: #0369a1; }
.btn-outline { background: #ffffff; border-color: var(--border-medium, #cbd5e1); color: var(--text-primary, #0f172a); }
.btn-outline:hover { background: #f8fafc; }
.btn-sm { padding: 0.35rem 0.65rem; font-size: 0.78rem; min-height: 36px; }
.btn-xs { padding: 0.25rem 0.5rem; font-size: 0.72rem; }
.btn-icon { width: 1rem; height: 1rem; flex-shrink: 0; }

.loading-state {
  padding: 3rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-subtle, #e2e8f0);
  border-top-color: #0284c7;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }
.alert-box.error { background: #fef2f2; color: #991b1b; padding: 1rem; border-radius: 6px; }

/* Responsive Breakpoints */
@media (max-width: 1024px) {
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .widgets-split-grid {
    grid-template-columns: 1fr;
  }
  .welcome-card {
    padding: 1.25rem;
    flex-direction: column;
    align-items: stretch;
  }
  .welcome-quick-actions {
    flex-direction: column;
  }
  .welcome-quick-actions .btn {
    width: 100%;
  }
}

@media (max-width: 640px) {
  .metrics-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.75rem;
  }
  .metric-card {
    padding: 0.85rem;
    gap: 0.5rem;
    flex-direction: column;
    align-items: flex-start;
  }
  .att-item-row, .pending-sub-row {
    flex-direction: column;
    align-items: stretch;
  }
  .att-item-row .btn, .pending-sub-row .btn {
    width: 100%;
  }
  .pending-progress-wrap {
    min-width: 100%;
  }
}
</style>
