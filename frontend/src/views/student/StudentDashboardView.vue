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
      <span class="loading-text">Loading student records and academic performance...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage" class="alert-box error card">
      <div class="error-icon-box">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="10" stroke-width="2" />
          <line x1="12" y1="8" x2="12" y2="12" stroke-width="2" stroke-linecap="round" />
          <line x1="12" y1="16" x2="12.01" y2="16" stroke-width="2" stroke-linecap="round" />
        </svg>
      </div>
      <div class="error-content">
        <strong class="error-title">Unable to Load Dashboard</strong>
        <p class="error-msg">{{ errorMessage }}</p>
      </div>
      <button type="button" class="retry-btn" @click="loadDashboard">Try Again</button>
    </div>

    <!-- Dashboard Content -->
    <div v-else-if="dashboardData" class="dashboard-content-stack">
      <!-- 1. Hero Welcome Banner -->
      <section class="welcome-banner" aria-label="Student Welcome Banner">
        <div class="banner-decor-shapes" aria-hidden="true">
          <div class="decor-circle circle-1" />
          <div class="decor-circle circle-2" />
        </div>

        <div class="welcome-left">
          <div class="badge-row">
            <span class="portal-badge">
              <span class="pulsing-emerald-dot" />
              SOMROYAL STUDENT PORTAL
            </span>
            <span class="status-chip">Academic Year {{ dashboardData.academic_year || '2026/2027' }}</span>
          </div>

          <h2 class="welcome-heading">
            Welcome back, <span class="student-name-highlight">{{ dashboardData.student.first_name }} {{ dashboardData.student.last_name }}</span> 👋
          </h2>

          <div class="welcome-meta-chips">
            <div class="meta-chip">
              <svg class="meta-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2" />
              </svg>
              <span>Adm: <strong>{{ dashboardData.student.admission_number }}</strong></span>
            </div>

            <div class="meta-chip">
              <svg class="meta-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              <span>Class: <strong>{{ dashboardData.current_class ? dashboardData.current_class.name : 'Not enrolled' }}</strong></span>
            </div>

            <div v-if="dashboardData.current_class?.section" class="meta-chip">
              <svg class="meta-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              <span>Section: <strong>{{ dashboardData.current_class.section }}</strong></span>
            </div>
          </div>
        </div>

        <div class="welcome-right">
          <button type="button" class="quick-profile-btn" @click="navigateTo('/student/profile')">
            <span>View Full Profile</span>
            <svg class="arrow-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </button>
        </div>
      </section>

      <!-- 2. 6 Summary Cards Responsive Grid -->
      <section class="summary-cards-grid" aria-label="Student Academic Metrics">
        <!-- Card 1: Current Class -->
        <div class="kpi-card card variant-blue" tabindex="0" role="button" @click="navigateTo('/student/class')" @keydown.enter="navigateTo('/student/class')">
          <div class="kpi-top">
            <span class="kpi-label">CURRENT CLASS</span>
            <div class="kpi-icon-wrap bg-blue-tint">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
          </div>
          <div class="kpi-val">{{ dashboardData.current_class ? dashboardData.current_class.name : 'Unassigned' }}</div>
          <div class="kpi-sub">
            Section: <strong>{{ dashboardData.current_class?.section || 'Section A' }}</strong>
          </div>
        </div>

        <!-- Card 2: Enrolled Subjects -->
        <div class="kpi-card card variant-emerald" tabindex="0" role="button" @click="navigateTo('/student/class')" @keydown.enter="navigateTo('/student/class')">
          <div class="kpi-top">
            <span class="kpi-label">ENROLLED SUBJECTS</span>
            <div class="kpi-icon-wrap bg-emerald-tint">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
          </div>
          <div class="kpi-val">{{ dashboardData.enrolled_subjects_count }}</div>
          <div class="kpi-sub">Active Curriculum Syllabus</div>
        </div>

        <!-- Card 3: Attendance Summary -->
        <div class="kpi-card card variant-amber" tabindex="0" role="button" @click="navigateTo('/student/attendance')" @keydown.enter="navigateTo('/student/attendance')">
          <div class="kpi-top">
            <span class="kpi-label">ATTENDANCE RATE</span>
            <div class="kpi-icon-wrap bg-amber-tint">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
          </div>
          <div class="kpi-val text-emerald-600">
            {{ dashboardData.attendance_summary ? `${dashboardData.attendance_summary.attendance_percentage}%` : '—' }}
          </div>
          <div class="kpi-sub">
            Present: <strong>{{ dashboardData.attendance_summary?.present_count || 0 }}</strong> &bull; Absent: <strong>{{ dashboardData.attendance_summary?.absent_count || 0 }}</strong>
          </div>
        </div>

        <!-- Card 4: Fees Summary -->
        <div class="kpi-card card" :class="dashboardData.outstanding_balance > 0 ? 'variant-rose' : 'variant-emerald'" tabindex="0" role="button" @click="navigateTo('/student/fees')" @keydown.enter="navigateTo('/student/fees')">
          <div class="kpi-top">
            <span class="kpi-label">OUTSTANDING FEES</span>
            <div class="kpi-icon-wrap" :class="dashboardData.outstanding_balance > 0 ? 'bg-rose-tint' : 'bg-emerald-tint'">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <div class="kpi-val" :class="dashboardData.outstanding_balance > 0 ? 'text-rose-600' : 'text-emerald-600'">
            ${{ Number(dashboardData.outstanding_balance).toFixed(2) }}
          </div>
          <div class="kpi-sub">
            <span v-if="dashboardData.outstanding_balance > 0">Due to Finance Office</span>
            <span v-else class="text-emerald-600 font-semibold">✓ Account fully settled</span>
          </div>
        </div>

        <!-- Card 5: Latest Released Exam Result -->
        <div class="kpi-card card variant-purple" tabindex="0" role="button" @click="navigateTo('/student/exams')" @keydown.enter="navigateTo('/student/exams')">
          <div class="kpi-top">
            <span class="kpi-label">LATEST EXAM RESULT</span>
            <div class="kpi-icon-wrap bg-purple-tint">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <div v-if="dashboardData.latest_exam_result" class="kpi-exam-content">
            <div class="kpi-exam-name">{{ dashboardData.latest_exam_result.exam_name }}</div>
            <div class="kpi-sub">
              Grade: <span class="badge-mini-grade">{{ dashboardData.latest_exam_result.grade || 'PASS' }}</span> &bull; {{ dashboardData.latest_exam_result.percentage }}%
            </div>
          </div>
          <div v-else class="kpi-empty-text">
            No released results yet.
          </div>
        </div>

        <!-- Card 6: Next / Today's Class Period -->
        <div class="kpi-card card variant-indigo" tabindex="0" role="button" @click="navigateTo('/student/timetable')" @keydown.enter="navigateTo('/student/timetable')">
          <div class="kpi-top">
            <span class="kpi-label">NEXT CLASS PERIOD</span>
            <div class="kpi-icon-wrap bg-indigo-tint">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <div v-if="dashboardData.next_class_period" class="kpi-period-content">
            <div class="kpi-period-name">{{ dashboardData.next_class_period.subject?.name || dashboardData.next_class_period.subject_name || 'Scheduled Subject' }}</div>
            <div class="kpi-sub">
              {{ dashboardData.next_class_period.start_time }} – {{ dashboardData.next_class_period.end_time }} &bull; <span class="badge-room">{{ dashboardData.next_class_period.room || dashboardData.next_class_period.room_number || 'Room TBD' }}</span>
            </div>
          </div>
          <div v-else class="kpi-empty-text">
            No active periods scheduled.
          </div>
        </div>
      </section>

      <!-- 3. Quick Actions Shortcuts -->
      <section class="quick-nav-grid" aria-label="Student Navigation Shortcuts">
        <div class="quick-nav-card" @click="navigateTo('/student/timetable')">
          <div class="quick-nav-icon bg-blue-tint">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <div class="quick-nav-text">
            <h4>Weekly Timetable</h4>
            <p>Class periods & rooms</p>
          </div>
          <span class="quick-nav-arrow">&rarr;</span>
        </div>

        <div class="quick-nav-card" @click="navigateTo('/student/attendance')">
          <div class="quick-nav-icon bg-emerald-tint">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
          </div>
          <div class="quick-nav-text">
            <h4>Attendance History</h4>
            <p>Subject period audits</p>
          </div>
          <span class="quick-nav-arrow">&rarr;</span>
        </div>

        <div class="quick-nav-card" @click="navigateTo('/student/fees')">
          <div class="quick-nav-icon bg-amber-tint">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="quick-nav-text">
            <h4>Fees & Invoices</h4>
            <p>Billing receipts & balance</p>
          </div>
          <span class="quick-nav-arrow">&rarr;</span>
        </div>

        <div class="quick-nav-card" @click="navigateTo('/student/exams')">
          <div class="quick-nav-icon bg-purple-tint">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="quick-nav-text">
            <h4>Exams & Results</h4>
            <p>Approved report cards</p>
          </div>
          <span class="quick-nav-arrow">&rarr;</span>
        </div>
      </section>

      <!-- 4. Today's Class Schedule Table Card -->
      <section class="card section-panel">
        <div class="panel-header">
          <div class="panel-title-wrap">
            <div class="panel-icon-circle bg-blue-tint">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h3 class="panel-title">Today's Class Schedule</h3>
              <p class="panel-sub">Official period lectures scheduled for today.</p>
            </div>
          </div>
          <button type="button" class="panel-action-link" @click="navigateTo('/student/timetable')">
            <span>Weekly Timetable</span>
            <span class="action-arrow">&rarr;</span>
          </button>
        </div>

        <div v-if="dashboardData.today_schedule.length === 0" class="empty-state-wrap">
          <div class="empty-icon-circle">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <h4 class="empty-state-title">No class periods scheduled for today</h4>
          <p class="empty-state-desc">You are free today or classes are not in session. Check your full weekly timetable for upcoming lectures.</p>
        </div>

        <div v-else class="table-responsive-wrapper">
          <table class="somroyal-table">
            <thead>
              <tr>
                <th>Period Time</th>
                <th>Subject</th>
                <th>Instructor</th>
                <th>Location / Room</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in dashboardData.today_schedule" :key="s.id">
                <td class="font-bold text-emerald-700">
                  <span class="time-badge">{{ s.start_time }} – {{ s.end_time }}</span>
                </td>
                <td class="font-semibold text-slate-900">
                  {{ s.subject?.name || s.subject_name || 'Subject' }}
                </td>
                <td class="text-slate-700">
                  <div class="teacher-inline-pill">
                    <svg class="w-3.5 h-3.5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    <span>{{ s.teacher?.full_name || s.teacher_name || 'Assigned Faculty' }}</span>
                  </div>
                </td>
                <td>
                  <span class="room-pill">{{ s.room || s.room_number || 'Room TBD' }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- 5. Recent Released Exam Results Table Card -->
      <section class="card section-panel">
        <div class="panel-header">
          <div class="panel-title-wrap">
            <div class="panel-icon-circle bg-purple-tint">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h3 class="panel-title">Official Released Examination Results</h3>
              <p class="panel-sub">Recently published assessment scores approved by School Administration.</p>
            </div>
          </div>
          <button type="button" class="panel-action-link" @click="navigateTo('/student/exams')">
            <span>View All Results</span>
            <span class="action-arrow">&rarr;</span>
          </button>
        </div>

        <div v-if="dashboardData.recent_exam_results.length === 0" class="empty-state-wrap">
          <div class="empty-icon-circle">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h4 class="empty-state-title">No released examination results yet</h4>
          <p class="empty-state-desc">Exam scores are currently being verified and will appear here once officially published.</p>
        </div>

        <div v-else class="table-responsive-wrapper">
          <table class="somroyal-table">
            <thead>
              <tr>
                <th>Assessment Exam</th>
                <th>Subject</th>
                <th>Marks Obtained</th>
                <th>Percentage</th>
                <th>Grade</th>
                <th>Verification</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="res in dashboardData.recent_exam_results" :key="res.id">
                <td class="font-bold text-slate-900">{{ res.exam_name }}</td>
                <td class="text-slate-800 font-medium">{{ res.subject_name }}</td>
                <td class="font-semibold text-slate-900">
                  <span v-if="res.marks_obtained !== null">{{ res.marks_obtained }} / {{ res.total_marks }}</span>
                  <span v-else class="text-slate-400">—</span>
                </td>
                <td class="font-bold">
                  <span v-if="res.percentage !== null" :class="(res.percentage || 0) >= 50 ? 'text-emerald-600' : 'text-rose-600'">
                    {{ res.percentage }}%
                  </span>
                  <span v-else class="text-slate-400">—</span>
                </td>
                <td>
                  <span class="grade-pill" :class="res.grade === 'F' ? 'grade-fail' : 'grade-pass'">
                    {{ res.grade || 'PASS' }}
                  </span>
                </td>
                <td>
                  <span class="verified-tag">
                    <svg class="w-3 h-3 text-emerald-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                    </svg>
                    Released
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.student-dashboard {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
}

.dashboard-content-stack {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
}

/* Base Card Style */
.card {
  background-color: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
}

/* Loading & Error States */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.85rem;
  padding: 3.5rem 1.5rem;
  color: #64748B;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #E2E8F0;
  border-top-color: #2563EB;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 0.88rem;
  font-weight: 500;
}

.alert-box.error {
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
  display: block;
}

.error-msg {
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
  transition: background-color 0.15s ease;
}

.retry-btn:hover {
  background-color: #B91C1C;
}

/* 1. Hero Welcome Banner (Admin Brand Gradient) */
.welcome-banner {
  background: linear-gradient(135deg, #071E46 0%, #0D47A1 45%, #0284C7 100%);
  border-radius: 20px;
  padding: 1.75rem 2rem;
  color: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  position: relative;
  overflow: hidden;
  box-shadow: 0 12px 30px -6px rgba(7, 30, 70, 0.35);
}

.banner-decor-shapes {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.decor-circle {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(2, 132, 199, 0.25) 0%, transparent 70%);
}

.circle-1 {
  width: 320px;
  height: 320px;
  top: -120px;
  right: -60px;
}

.circle-2 {
  width: 200px;
  height: 200px;
  bottom: -80px;
  left: 20%;
}

.welcome-left {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  z-index: 2;
}

.badge-row {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-wrap: wrap;
}

.portal-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #FFFFFF;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.25);
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
}

.pulsing-emerald-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #38BDF8;
  box-shadow: 0 0 8px #38BDF8;
}

.status-chip {
  font-size: 0.72rem;
  color: #CBD5E1;
  background: rgba(255, 255, 255, 0.1);
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.welcome-heading {
  font-size: 1.6rem;
  font-weight: 800;
  color: #FFFFFF;
  margin: 0;
  line-height: 1.25;
}

.student-name-highlight {
  color: #FDE68A;
}

.welcome-meta-chips {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.meta-chip {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.8rem;
  color: #CBD5E1;
  background: rgba(255, 255, 255, 0.08);
  padding: 0.35rem 0.75rem;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.meta-chip strong {
  color: #FFFFFF;
}

.meta-icon {
  width: 14px;
  height: 14px;
  color: #38BDF8;
}

.welcome-right {
  z-index: 2;
  flex-shrink: 0;
}

.quick-profile-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  background: #FFFFFF;
  color: #0A192F;
  font-size: 0.86rem;
  font-weight: 700;
  padding: 0.75rem 1.35rem;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.2s ease;
}

.quick-profile-btn:hover {
  background: #F1F5F9;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.arrow-icon {
  width: 16px;
  height: 16px;
  color: #2563EB;
  transition: transform 0.2s ease;
}

.quick-profile-btn:hover .arrow-icon {
  transform: translateX(4px);
}

/* 2. 6 Summary Cards Grid */
.summary-cards-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 1rem;
}

.kpi-card {
  padding: 1.15rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 120px;
}

.kpi-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
}

.kpi-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.kpi-label {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: #64748B;
}

.kpi-icon-wrap {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.kpi-icon-wrap svg {
  width: 17px;
  height: 17px;
}

.bg-blue-tint { background: #EFF6FF; color: #2563EB; }
.bg-emerald-tint { background: #ECFDF5; color: #059669; }
.bg-amber-tint { background: #FFFBEB; color: #D97706; }
.bg-rose-tint { background: #FEF2F2; color: #DC2626; }
.bg-purple-tint { background: #FAF5FF; color: #7C3AED; }
.bg-indigo-tint { background: #EEF2FF; color: #4F46E5; }

.kpi-val {
  font-size: 1.45rem;
  font-weight: 800;
  color: #0F172A;
  line-height: 1.15;
  margin-bottom: 0.35rem;
}

.kpi-sub {
  font-size: 0.74rem;
  color: #64748B;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.kpi-exam-name,
.kpi-period-name {
  font-size: 0.95rem;
  font-weight: 700;
  color: #0F172A;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 0.25rem;
}

.kpi-empty-text {
  font-size: 0.78rem;
  color: #94A3B8;
  font-style: italic;
  padding: 0.35rem 0;
}

.badge-mini-grade {
  background: #ECFDF5;
  color: #059669;
  font-size: 0.7rem;
  font-weight: 800;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
}

.badge-room {
  background: #F1F5F9;
  color: #334155;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  font-weight: 600;
}

/* 3. Quick Navigation Grid */
.quick-nav-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.quick-nav-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 14px;
  padding: 0.9rem 1.15rem;
  display: flex;
  align-items: center;
  gap: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
}

.quick-nav-card:hover {
  transform: translateY(-2px);
  border-color: #CBD5E1;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.06);
}

.quick-nav-icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.quick-nav-icon svg {
  width: 20px;
  height: 20px;
}

.quick-nav-text {
  flex: 1;
  min-width: 0;
}

.quick-nav-text h4 {
  font-size: 0.85rem;
  font-weight: 700;
  color: #0F172A;
  margin: 0;
}

.quick-nav-text p {
  font-size: 0.72rem;
  color: #64748B;
  margin: 0.15rem 0 0 0;
}

.quick-nav-arrow {
  color: #94A3B8;
  font-size: 1rem;
  transition: transform 0.15s ease;
}

.quick-nav-card:hover .quick-nav-arrow {
  color: #2563EB;
  transform: translateX(3px);
}

/* 4 & 5. Section Panels (Tables) */
.section-panel {
  padding: 1.5rem;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.panel-title-wrap {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.panel-icon-circle {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.panel-icon-circle svg {
  width: 20px;
  height: 20px;
}

.panel-title {
  font-size: 1rem;
  font-weight: 700;
  color: #0F172A;
  margin: 0;
}

.panel-sub {
  font-size: 0.78rem;
  color: #64748B;
  margin: 0.2rem 0 0 0;
}

.panel-action-link {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: #2563EB;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.35rem 0.65rem;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.panel-action-link:hover {
  background: #EFF6FF;
  color: #1D4ED8;
}

.action-arrow {
  transition: transform 0.15s ease;
}

.panel-action-link:hover .action-arrow {
  transform: translateX(3px);
}

/* Empty State */
.empty-state-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2.75rem 1.5rem;
  text-align: center;
}

.empty-icon-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: #F1F5F9;
  color: #94A3B8;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.75rem;
}

.empty-icon-circle svg {
  width: 24px;
  height: 24px;
}

.empty-state-title {
  font-size: 0.92rem;
  font-weight: 700;
  color: #0F172A;
  margin: 0 0 0.35rem 0;
}

.empty-state-desc {
  font-size: 0.78rem;
  color: #64748B;
  max-width: 380px;
  margin: 0;
  line-height: 1.4;
}

/* Table Design */
.table-responsive-wrapper {
  overflow-x: auto;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
}

.somroyal-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.84rem;
}

.somroyal-table thead th {
  background-color: #F8FAFC;
  color: #475569;
  font-weight: 700;
  font-size: 0.72rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #E2E8F0;
}

.somroyal-table tbody tr {
  border-bottom: 1px solid #F1F5F9;
  transition: background-color 0.15s ease;
}

.somroyal-table tbody tr:hover {
  background-color: #F8FAFC;
}

.somroyal-table tbody td {
  padding: 0.85rem 1rem;
  color: #334155;
}

.time-badge {
  background: #ECFDF5;
  color: #065F46;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  font-size: 0.78rem;
  font-weight: 700;
  border: 1px solid #A7F3D0;
}

.teacher-inline-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.room-pill {
  background: #F1F5F9;
  border: 1px solid #E2E8F0;
  color: #334155;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
}

.grade-pill {
  display: inline-block;
  padding: 0.15rem 0.6rem;
  border-radius: 9999px;
  font-weight: 800;
  font-size: 0.72rem;
  text-align: center;
}

.grade-pass {
  background: #ECFDF5;
  color: #059669;
  border: 1px solid #A7F3D0;
}

.grade-fail {
  background: #FEF2F2;
  color: #DC2626;
  border: 1px solid #FECACA;
}

.verified-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  color: #059669;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
}

/* ========================================================================= */
/* RESPONSIVE BREAKPOINTS                                                    */
/* ========================================================================= */
@media (max-width: 1200px) {
  .summary-cards-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  .quick-nav-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .welcome-banner {
    padding: 1.35rem 1.25rem;
    flex-direction: column;
    align-items: flex-start;
  }
  .welcome-heading {
    font-size: 1.3rem;
  }
  .welcome-right {
    width: 100%;
  }
  .quick-profile-btn {
    width: 100%;
    justify-content: center;
  }
  .summary-cards-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 520px) {
  .summary-cards-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.65rem;
  }
  .kpi-card {
    padding: 0.85rem;
    min-height: 100px;
  }
  .kpi-val {
    font-size: 1.25rem;
  }
  .quick-nav-grid {
    grid-template-columns: 1fr;
    gap: 0.65rem;
  }
  .section-panel {
    padding: 1rem;
  }
}

@media (max-width: 360px) {
  .summary-cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>
