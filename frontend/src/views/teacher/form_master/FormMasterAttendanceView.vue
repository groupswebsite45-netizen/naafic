<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import {
  formMasterService,
  type FormMasterClassSummary,
  type FormMasterAttendanceData,
} from '../../../services/formMasterService';

const loading = ref(false);
const errorMsg = ref('');
const myClasses = ref<FormMasterClassSummary[]>([]);
const selectedClassId = ref<number | null>(null);
const attendanceData = ref<FormMasterAttendanceData | null>(null);

// Filters
const activeTab = ref<'STUDENTS' | 'HISTORY' | 'TRENDS'>('STUDENTS');
const startDate = ref('');
const endDate = ref('');

onMounted(async () => {
  await loadClasses();
});

watch(selectedClassId, async (newId) => {
  if (newId) {
    await loadAttendance(newId);
  }
});

watch([startDate, endDate], async () => {
  if (selectedClassId.value) {
    await loadAttendance(selectedClassId.value);
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
    }
  } catch (err: any) {
    errorMsg.value = err?.response?.data?.detail || 'Failed to load assigned classes.';
  } finally {
    loading.value = false;
  }
}

async function loadAttendance(classId: number) {
  loading.value = true;
  errorMsg.value = '';
  try {
    const params: any = {};
    if (startDate.value) params.start_date = startDate.value;
    if (endDate.value) params.end_date = endDate.value;
    const data = await formMasterService.getAttendance(classId, params);
    attendanceData.value = data;
  } catch (err: any) {
    errorMsg.value = err?.response?.data?.detail || 'Failed to load attendance records.';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="attendance-monitoring-view">
    <!-- Header -->
    <header class="page-header">
      <div class="header-main">
        <div class="title-wrap">
          <div class="icon-wrap bg-green-subtle text-green">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h1 class="page-title">Class Attendance Monitoring</h1>
              <span class="badge badge-supervisory">CROSS-SUBJECT SUPERVISION</span>
            </div>
            <p class="page-subtitle">
              Monitor present, absent and late students across all periods and subjects in your assigned class.
            </p>
          </div>
        </div>

        <!-- Class Picker (if >1 class assigned) -->
        <div v-if="myClasses.length > 1" class="class-picker">
          <span class="picker-label">Class:</span>
          <select v-model="selectedClassId" class="picker-select">
            <option v-for="c in myClasses" :key="c.id" :value="c.id">
              {{ c.name }} ({{ c.division }})
            </option>
          </select>
        </div>
      </div>
    </header>

    <!-- Error State -->
    <div v-if="errorMsg" class="alert alert-error">
      <span>{{ errorMsg }}</span>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner" />
      <p>Loading attendance telemetry and chronic absence patterns...</p>
    </div>

    <!-- Main Content -->
    <div v-else-if="attendanceData" class="attendance-body">
      <!-- Attendance Statistics Cards -->
      <div class="stat-grid">
        <div class="card">
          <span class="card-label">Overall Attendance Rate</span>
          <span class="card-val" :class="attendanceData.overall_stats.attendance_rate >= 80 ? 'text-green' : 'text-amber'">
            {{ attendanceData.overall_stats.attendance_rate }}%
          </span>
          <span class="card-sub">{{ attendanceData.overall_stats.total_records }} total periods tracked</span>
        </div>

        <div class="card">
          <span class="card-label">Present Periods</span>
          <span class="card-val text-green">{{ attendanceData.overall_stats.present_count }}</span>
          <span class="card-sub">Recorded on time</span>
        </div>

        <div class="card">
          <span class="card-label">Absences</span>
          <span class="card-val text-red">{{ attendanceData.overall_stats.absent_count }}</span>
          <span class="card-sub">Unexcused missed periods</span>
        </div>

        <div class="card">
          <span class="card-label">Late Arrivals</span>
          <span class="card-val text-amber">{{ attendanceData.overall_stats.late_count }}</span>
          <span class="card-sub">Arrived after period bell</span>
        </div>
      </div>

      <!-- Tab Switcher -->
      <div class="tab-bar">
        <button
          type="button"
          class="tab-btn"
          :class="{ active: activeTab === 'STUDENTS' }"
          @click="activeTab = 'STUDENTS'"
        >
          Student Attendance Standings
        </button>
        <button
          type="button"
          class="tab-btn"
          :class="{ active: activeTab === 'TRENDS' }"
          @click="activeTab = 'TRENDS'"
        >
          Monthly Trends
        </button>
        <button
          type="button"
          class="tab-btn"
          :class="{ active: activeTab === 'HISTORY' }"
          @click="activeTab = 'HISTORY'"
        >
          Recent Period Logs
        </button>
      </div>

      <!-- TAB 1: Student Attendance Standings -->
      <div v-if="activeTab === 'STUDENTS'" class="table-card">
        <table class="data-table">
          <thead>
            <tr>
              <th>Student</th>
              <th>Admission #</th>
              <th>Present</th>
              <th>Absent</th>
              <th>Late</th>
              <th>Excused</th>
              <th>Attendance Rate</th>
              <th>Standing</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="s in attendanceData.students"
              :key="s.student_id"
              :class="{ 'row-warning': s.is_frequent_absentee }"
            >
              <td class="font-medium">
                {{ s.name }}
                <span v-if="s.is_frequent_absentee" class="badge-alert ml-1">Chronic Absence</span>
              </td>
              <td class="text-xs text-muted">{{ s.admission_number }}</td>
              <td><span class="count-tag text-green">{{ s.present_count }}</span></td>
              <td>
                <span class="count-tag" :class="s.absent_count >= 3 ? 'text-red font-bold' : 'text-slate-700'">
                  {{ s.absent_count }}
                </span>
              </td>
              <td><span class="count-tag text-amber">{{ s.late_count }}</span></td>
              <td><span class="count-tag text-slate-500">{{ s.excused_count }}</span></td>
              <td>
                <div class="rate-bar-wrap">
                  <div class="rate-bar">
                    <div
                      class="rate-fill"
                      :class="s.attendance_rate >= 80 ? 'fill-green' : 'fill-amber'"
                      :style="{ width: `${s.attendance_rate}%` }"
                    />
                  </div>
                  <span class="rate-text">{{ s.attendance_rate }}%</span>
                </div>
              </td>
              <td>
                <span v-if="s.is_frequent_absentee" class="status-alert">Intervention Needed</span>
                <span v-else class="status-ok">Regular</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- TAB 2: Monthly Trends -->
      <div v-if="activeTab === 'TRENDS'" class="table-card">
        <table class="data-table">
          <thead>
            <tr>
              <th>Month</th>
              <th>Total Periods</th>
              <th>Present Count</th>
              <th>Absent Count</th>
              <th>Monthly Attendance Rate</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in attendanceData.monthly_trend" :key="t.month">
              <td class="font-bold">{{ t.month }}</td>
              <td>{{ t.total }}</td>
              <td class="text-green font-medium">{{ t.present }}</td>
              <td class="text-red font-medium">{{ t.absent }}</td>
              <td>
                <span class="rate-badge font-bold" :class="t.rate >= 80 ? 'text-green' : 'text-amber'">
                  {{ t.rate }}%
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- TAB 3: Recent Period Logs -->
      <div v-if="activeTab === 'HISTORY'" class="table-card">
        <table class="data-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Period</th>
              <th>Subject</th>
              <th>Student</th>
              <th>Status</th>
              <th>Remarks</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in attendanceData.recent_records" :key="log.id">
              <td>{{ log.date }}</td>
              <td>{{ log.period || '—' }}</td>
              <td class="font-medium">{{ log.subject_name }}</td>
              <td>{{ log.student_name }}</td>
              <td>
                <span
                  class="status-pill"
                  :class="{
                    'status-present': log.status === 'PRESENT',
                    'status-absent': log.status === 'ABSENT',
                    'status-late': log.status === 'LATE',
                    'status-excused': log.status === 'EXCUSED',
                  }"
                >
                  {{ log.status }}
                </span>
              </td>
              <td class="text-xs text-muted">{{ log.remarks || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.attendance-monitoring-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-header {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.25rem 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.header-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.title-wrap {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bg-green-subtle { background: #f0fdf4; }
.text-green { color: #16a34a; }
.text-amber { color: #d97706; }
.text-red { color: #dc2626; }

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

.badge-supervisory {
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  background: #f0fdf4;
  color: #16a34a;
  border: 1px solid #bbf7d0;
}

.class-picker {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.picker-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
}

.picker-select {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  background: #ffffff;
}

/* Stat Grid */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.card {
  padding: 1.25rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
}

.card-label {
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
}

.card-val {
  font-size: 1.75rem;
  font-weight: 800;
  margin: 0.25rem 0 0.125rem;
}

.card-sub {
  font-size: 0.6875rem;
  color: #94a3b8;
}

/* Tab Bar */
.tab-bar {
  display: flex;
  background: #f1f5f9;
  padding: 0.25rem;
  border-radius: 10px;
  gap: 0.25rem;
  width: fit-content;
}

.tab-btn {
  padding: 0.5rem 1rem;
  font-size: 0.8125rem;
  font-weight: 600;
  border: none;
  background: transparent;
  color: #64748b;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.tab-btn.active {
  background: #ffffff;
  color: #0f172a;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

/* Table Card */
.table-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8125rem;
}

.data-table th {
  padding: 0.875rem 1rem;
  background: #f8fafc;
  font-weight: 700;
  font-size: 0.6875rem;
  text-transform: uppercase;
  color: #64748b;
  border-bottom: 1px solid #e2e8f0;
}

.data-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f1f5f9;
}

.data-table tr.row-warning td {
  background: #fffdf5;
}

.count-tag {
  font-weight: 700;
}

.badge-alert {
  font-size: 0.625rem;
  font-weight: 700;
  padding: 0.1rem 0.375rem;
  border-radius: 4px;
  background: #fee2e2;
  color: #b91c1c;
}

.rate-bar-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.rate-bar {
  width: 80px;
  height: 6px;
  background: #e2e8f0;
  border-radius: 9999px;
  overflow: hidden;
}

.rate-fill {
  height: 100%;
  border-radius: 9999px;
}

.fill-green { background: #16a34a; }
.fill-amber { background: #d97706; }

.rate-text {
  font-size: 0.75rem;
  font-weight: 700;
  color: #334155;
}

.status-alert {
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border-radius: 9999px;
  background: #fee2e2;
  color: #991b1b;
}

.status-ok {
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border-radius: 9999px;
  background: #dcfce7;
  color: #166534;
}

.status-pill {
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
}

.status-present { background: #dcfce7; color: #166534; }
.status-absent { background: #fee2e2; color: #991b1b; }
.status-late { background: #fef3c7; color: #92400e; }
.status-excused { background: #f1f5f9; color: #475569; }

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
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

