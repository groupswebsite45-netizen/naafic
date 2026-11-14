<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import {
  formMasterService,
  type FormMasterClassSummary,
  type FormMasterDashboardData,
} from '../../../services/formMasterService';

const router = useRouter();

const loading = ref(false);
const errorMsg = ref('');
const myClasses = ref<FormMasterClassSummary[]>([]);
const selectedClassId = ref<number | null>(null);
const dashboardData = ref<FormMasterDashboardData | null>(null);

onMounted(async () => {
  await loadClasses();
});

watch(selectedClassId, async (newId) => {
  if (newId) {
    await loadDashboard(newId);
  }
});

async function loadClasses() {
  loading.value = true;
  errorMsg.value = '';
  try {
    const classes = await formMasterService.getMyClasses();
    myClasses.value = classes;
    if (classes.length > 0) {
      selectedClassId.value = classes[0].id;
    } else {
      errorMsg.value = 'You are not currently appointed as a Form Master for any active class.';
    }
  } catch (err: any) {
    if (err?.response?.status === 403) {
      errorMsg.value = 'Access denied: You are not appointed as a Form Master.';
    } else {
      errorMsg.value = err?.response?.data?.detail || 'Failed to load assigned Form Master classes.';
    }
  } finally {
    loading.value = false;
  }
}

async function loadDashboard(classId: number) {
  loading.value = true;
  errorMsg.value = '';
  try {
    const data = await formMasterService.getDashboard(classId);
    dashboardData.value = data;
  } catch (err: any) {
    errorMsg.value = err?.response?.data?.detail || 'Failed to load Form Master dashboard data.';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="form-master-dashboard">
    <!-- Header with Class Tabs -->
    <header class="dashboard-header">
      <div class="header-content">
        <div class="title-with-badge">
          <div class="fm-shield-icon">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h1 class="page-title">Form Master Dashboard</h1>
              <span class="supervisory-pill">SUPERVISORY ACCESS</span>
            </div>
            <p class="page-subtitle">
              Comprehensive supervisory oversight of student academics, attendance, and fee status.
            </p>
          </div>
        </div>
      </div>

      <!-- Class Selector Switcher (if teacher has 1 or 2 classes) -->
      <div v-if="myClasses.length > 0" class="class-switcher-bar">
        <span class="switcher-label">Supervising Class:</span>
        <div class="class-pills">
          <button
            v-for="c in myClasses"
            :key="c.id"
            type="button"
            class="class-pill-btn"
            :class="{ active: selectedClassId === c.id }"
            @click="selectedClassId = c.id"
          >
            <span class="pill-title">{{ c.name }}</span>
            <span class="pill-meta">{{ c.division }} &bull; {{ c.student_count }} Students</span>
          </button>
        </div>
      </div>
    </header>

    <!-- Error State -->
    <div v-if="errorMsg" class="alert-box alert-error">
      <svg class="h-5 w-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
      </svg>
      <span>{{ errorMsg }}</span>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner" />
      <p>Loading class supervisory metrics...</p>
    </div>

    <!-- Main Content -->
    <div v-else-if="dashboardData" class="dashboard-body">
      <!-- Top Metrics Banner -->
      <div class="metrics-grid">
        <!-- 1. Total Students -->
        <div class="stat-card" @click="router.push(`/teacher/form-classes/students`)">
          <div class="stat-content">
            <span class="stat-label">Total Enrolled</span>
            <div class="stat-num">{{ dashboardData.total_students }}</div>
            <span class="stat-hint">In {{ dashboardData.selected_class.name }}</span>
          </div>
          <div class="stat-icon-wrap bg-blue">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
        </div>

        <!-- 2. Attendance Rate -->
        <div class="stat-card" @click="router.push(`/teacher/form-classes/attendance`)">
          <div class="stat-content">
            <span class="stat-label">Attendance Rate</span>
            <div class="stat-num" :class="dashboardData.attendance_rate >= 80 ? 'text-green' : 'text-amber'">
              {{ dashboardData.attendance_rate }}%
            </div>
            <span class="stat-hint">Present &amp; Late combined</span>
          </div>
          <div class="stat-icon-wrap bg-green">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>

        <!-- 3. Poor Academic Performance -->
        <div class="stat-card" @click="router.push(`/teacher/form-classes/results`)">
          <div class="stat-content">
            <span class="stat-label">Poor Academic Progress</span>
            <div class="stat-num" :class="dashboardData.students_with_poor_performance_count > 0 ? 'text-red' : 'text-green'">
              {{ dashboardData.students_with_poor_performance_count }}
            </div>
            <span class="stat-hint">Average &lt; 50% or failing subjects</span>
          </div>
          <div class="stat-icon-wrap bg-red">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>

        <!-- 4. Chronic Absences -->
        <div class="stat-card" @click="router.push(`/teacher/form-classes/attendance`)">
          <div class="stat-content">
            <span class="stat-label">Frequent Absences</span>
            <div class="stat-num" :class="dashboardData.students_with_frequent_absences_count > 0 ? 'text-amber' : 'text-green'">
              {{ dashboardData.students_with_frequent_absences_count }}
            </div>
            <span class="stat-hint">Recorded &ge; 3 absences</span>
          </div>
          <div class="stat-icon-wrap bg-amber">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>

        <!-- 5. Outstanding Fees -->
        <div class="stat-card" @click="router.push(`/teacher/form-classes/fees`)">
          <div class="stat-content">
            <span class="stat-label">Outstanding Fees</span>
            <div class="stat-num text-orange">
              ${{ dashboardData.total_outstanding_fees }}
            </div>
            <span class="stat-hint">{{ dashboardData.students_with_outstanding_fees_count }} student(s) with balance</span>
          </div>
          <div class="stat-icon-wrap bg-orange">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Critical Attention Alerts -->
      <section v-if="dashboardData.alerts.length > 0" class="alerts-section">
        <h2 class="section-title flex items-center gap-2">
          <svg class="h-5 w-5 text-amber" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
          Important Supervisory Alerts Requiring Attention
        </h2>
        <div class="alerts-stack">
          <div
            v-for="(alert, idx) in dashboardData.alerts"
            :key="idx"
            class="alert-card"
            :class="alert.level === 'WARNING' ? 'alert-card-warning' : 'alert-card-info'"
          >
            <div class="alert-header">
              <span class="alert-category">{{ alert.category }}</span>
              <h3 class="alert-title">{{ alert.title }}</h3>
            </div>
            <p class="alert-desc">{{ alert.description }}</p>
          </div>
        </div>
      </section>

      <!-- Two-Column Grid: Poor Academic Performers & Chronic Absences -->
      <div class="two-col-grid">
        <!-- Poor Academic Performers -->
        <div class="dashboard-panel">
          <div class="panel-header">
            <div>
              <h2 class="panel-title">Students Requiring Academic Support</h2>
              <p class="panel-subtitle">Students with average score below 50% or failing subjects</p>
            </div>
            <button
              type="button"
              class="btn-text"
              @click="router.push(`/teacher/form-classes/results`)"
            >
              View Results Sheet &rarr;
            </button>
          </div>

          <div v-if="dashboardData.poor_performance_students.length === 0" class="panel-empty">
            <svg class="h-10 w-10 text-green" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="font-medium text-slate-800 mt-2">All students currently meet passing criteria</p>
            <span class="text-xs text-muted">No failing subjects or low averages identified.</span>
          </div>

          <table v-else class="simple-table">
            <thead>
              <tr>
                <th>Student</th>
                <th>Admission #</th>
                <th>Average</th>
                <th>Failing</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in dashboardData.poor_performance_students" :key="s.student_id">
                <td class="font-medium">{{ s.name }}</td>
                <td class="text-muted text-xs">{{ s.admission_number }}</td>
                <td>
                  <span class="score-badge text-red font-semibold">
                    {{ s.average_score !== null ? `${s.average_score}%` : 'N/A' }}
                  </span>
                </td>
                <td>
                  <span class="fail-pill">{{ s.failing_subjects_count }} subject(s)</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Chronic Absences -->
        <div class="dashboard-panel">
          <div class="panel-header">
            <div>
              <h2 class="panel-title">Chronic Attendance Alerts</h2>
              <p class="panel-subtitle">Students with 3 or more recorded absences</p>
            </div>
            <button
              type="button"
              class="btn-text"
              @click="router.push(`/teacher/form-classes/attendance`)"
            >
              View Attendance &rarr;
            </button>
          </div>

          <div v-if="dashboardData.frequent_absences_students.length === 0" class="panel-empty">
            <svg class="h-10 w-10 text-green" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="font-medium text-slate-800 mt-2">Satisfactory attendance across the class</p>
            <span class="text-xs text-muted">No students with chronic absences detected.</span>
          </div>

          <table v-else class="simple-table">
            <thead>
              <tr>
                <th>Student</th>
                <th>Admission #</th>
                <th>Absences</th>
                <th>Guardian Contact</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in dashboardData.frequent_absences_students" :key="s.student_id">
                <td class="font-medium">{{ s.name }}</td>
                <td class="text-muted text-xs">{{ s.admission_number }}</td>
                <td>
                  <span class="absent-pill">{{ s.absent_count }} days</span>
                </td>
                <td class="text-xs text-muted">
                  {{ s.guardian_name || 'Guardian' }} &bull; {{ s.phone || 'No phone' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Quick Navigation Shortcuts -->
      <section class="shortcuts-section">
        <h2 class="section-title">Form Master Supervision Suites</h2>
        <div class="suite-cards-grid">
          <div class="suite-card" @click="router.push(`/teacher/form-classes/results`)">
            <div class="suite-icon bg-blue-subtle text-blue">
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
              </svg>
            </div>
            <div>
              <h3 class="suite-title">Academic Results Monitoring</h3>
              <p class="suite-desc">Cross-subject grades, exam performance, class averages and published rankings.</p>
            </div>
          </div>

          <div class="suite-card" @click="router.push(`/teacher/form-classes/attendance`)">
            <div class="suite-icon bg-green-subtle text-green">
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h3 class="suite-title">Attendance Monitoring</h3>
              <p class="suite-desc">Cross-period attendance, monthly attendance trends and chronic absence alerts.</p>
            </div>
          </div>

          <div class="suite-card" @click="router.push(`/teacher/form-classes/fees`)">
            <div class="suite-icon bg-orange-subtle text-orange">
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h3 class="suite-title">Student Fees Monitoring</h3>
              <p class="suite-desc">Read-only student fee status, outstanding balances, and payment records.</p>
            </div>
          </div>

          <div class="suite-card" @click="router.push(`/teacher/form-classes/students`)">
            <div class="suite-icon bg-purple-subtle text-purple">
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <div>
              <h3 class="suite-title">Class Students Roster</h3>
              <p class="suite-desc">Student profile information, guardian contacts, and individual progress records.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.form-master-dashboard {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.dashboard-header {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.25rem 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.title-with-badge {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.fm-shield-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #ff6500 0%, #ff8a00 100%);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(255, 101, 0, 0.25);
}

.page-title {
  font-size: 1.375rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.page-subtitle {
  font-size: 0.8125rem;
  color: #64748b;
  margin: 0.25rem 0 0;
}

.supervisory-pill {
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  padding: 0.2rem 0.5rem;
  border-radius: 9999px;
  background: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
}

/* Class Switcher */
.class-switcher-bar {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #f1f5f9;
}

.switcher-label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
}

.class-pills {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.class-pill-btn {
  display: flex;
  flex-direction: column;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
  background: #f8fafc;
  cursor: pointer;
  text-align: left;
  transition: all 0.15s ease;
}

.class-pill-btn:hover {
  border-color: #ff6500;
  background: #ffffff;
}

.class-pill-btn.active {
  background: #fff7ed;
  border-color: #ff6500;
  box-shadow: 0 0 0 2px rgba(255, 101, 0, 0.2);
}

.pill-title {
  font-size: 0.875rem;
  font-weight: 700;
  color: #0f172a;
}

.pill-meta {
  font-size: 0.6875rem;
  color: #64748b;
}

/* Stat Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.stat-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.15s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  border-color: #ff6500;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
}

.stat-num {
  font-size: 1.625rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0.25rem 0 0.125rem;
}

.stat-hint {
  font-size: 0.6875rem;
  color: #94a3b8;
}

.stat-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bg-blue { background: #eff6ff; color: #2563eb; }
.bg-green { background: #f0fdf4; color: #16a34a; }
.bg-red { background: #fef2f2; color: #dc2626; }
.bg-amber { background: #fffbeb; color: #d97706; }
.bg-orange { background: #fff7ed; color: #ff6500; }
.bg-purple-subtle { background: #faf5ff; }
.text-purple { color: #9333ea; }

.text-green { color: #16a34a; }
.text-amber { color: #d97706; }
.text-red { color: #dc2626; }
.text-orange { color: #ff6500; }

/* Alerts */
.alerts-section {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.25rem;
}

.section-title {
  font-size: 0.9375rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 1rem;
}

.alerts-stack {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.alert-card {
  padding: 0.875rem 1.125rem;
  border-radius: 8px;
  border-left: 4px solid;
}

.alert-card-warning {
  background: #fffbeb;
  border-color: #f59e0b;
}

.alert-card-info {
  background: #eff6ff;
  border-color: #3b82f6;
}

.alert-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.alert-category {
  font-size: 0.625rem;
  font-weight: 800;
  text-transform: uppercase;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.08);
}

.alert-title {
  font-size: 0.875rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.alert-desc {
  font-size: 0.8125rem;
  color: #475569;
  margin: 0;
}

/* Two Column Grid */
.two-col-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: 1.25rem;
}

.dashboard-panel {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.panel-title {
  font-size: 0.9375rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.panel-subtitle {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0.125rem 0 0;
}

.btn-text {
  background: transparent;
  border: none;
  font-size: 0.75rem;
  font-weight: 600;
  color: #ff6500;
  cursor: pointer;
}

.btn-text:hover {
  text-decoration: underline;
}

.panel-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
  text-align: center;
}

.simple-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8125rem;
}

.simple-table th {
  padding: 0.5rem 0.75rem;
  text-align: left;
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
  border-bottom: 1px solid #e2e8f0;
}

.simple-table td {
  padding: 0.625rem 0.75rem;
  border-bottom: 1px solid #f1f5f9;
}

.fail-pill {
  font-size: 0.6875rem;
  font-weight: 600;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  background: #fee2e2;
  color: #991b1b;
}

.absent-pill {
  font-size: 0.6875rem;
  font-weight: 600;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  background: #fef3c7;
  color: #92400e;
}

/* Suites Shortcuts */
.suite-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}

.suite-card {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.125rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.suite-card:hover {
  border-color: #ff6500;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

.suite-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.suite-title {
  font-size: 0.875rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.suite-desc {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0.25rem 0 0;
  line-height: 1.4;
}

/* Alerts and Loading */
.alert-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-radius: 8px;
  font-size: 0.875rem;
}

.alert-error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 1.5rem;
  color: #64748b;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e2e8f0;
  border-top-color: #ff6500;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 0.75rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>

