<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { studentPortalService } from '../../services/studentPortalService';
import { StudentAttendanceData } from '../../types/studentPortal';

const attendanceData = ref<StudentAttendanceData | null>(null);
const academicYears = ref<string[]>([]);
const selectedYear = ref<string>('');
const selectedMonth = ref<string>('');
const selectedSubjectId = ref<string>('');
const selectedStatus = ref<string>('');
const isLoading = ref(true);
const errorMessage = ref('');

const monthsList = [
  { value: '1', label: 'January' },
  { value: '2', label: 'February' },
  { value: '3', label: 'March' },
  { value: '4', label: 'April' },
  { value: '5', label: 'May' },
  { value: '6', label: 'June' },
  { value: '7', label: 'July' },
  { value: '8', label: 'August' },
  { value: '9', label: 'September' },
  { value: '10', label: 'October' },
  { value: '11', label: 'November' },
  { value: '12', label: 'December' },
];

async function fetchAttendance() {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    const filters: {
      academic_year?: string;
      month?: number;
      subject_id?: number;
      status?: string;
    } = {};

    if (selectedYear.value) filters.academic_year = selectedYear.value;
    if (selectedMonth.value) filters.month = parseInt(selectedMonth.value);
    if (selectedSubjectId.value) filters.subject_id = parseInt(selectedSubjectId.value);
    if (selectedStatus.value) filters.status = selectedStatus.value;

    attendanceData.value = await studentPortalService.getMyAttendance(filters);
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to retrieve attendance logs.';
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
    academicYears.value = ['2026/2027'];
    selectedYear.value = '2026/2027';
  }
  await fetchAttendance();
}

function formatDate(dateStr: string) {
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' });
  } catch {
    return dateStr;
  }
}

function resetFilters() {
  selectedMonth.value = '';
  selectedSubjectId.value = '';
  selectedStatus.value = '';
  fetchAttendance();
}

onMounted(() => {
  initPage();
});
</script>

<template>
  <div class="portal-page student-attendance-view">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">My Class Attendance</h1>
        <p class="page-subtitle">Your subject period attendance logs, overall attendance rate, and verified absence records.</p>
      </div>
    </div>

    <!-- Summary KPI Cards -->
    <section v-if="attendanceData" class="summary-grid" aria-label="Attendance Overview Metrics">
      <!-- Total Classes -->
      <div class="card summary-card variant-blue">
        <div class="sum-top">
          <span class="sum-label">TOTAL CLASSES</span>
          <div class="sum-icon-box bg-blue-tint">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
        </div>
        <span class="sum-val">{{ attendanceData.summary.total_classes }}</span>
        <span class="sum-sub">Conducted Periods</span>
      </div>

      <!-- Classes Present -->
      <div class="card summary-card variant-emerald">
        <div class="sum-top">
          <span class="sum-label">CLASSES PRESENT</span>
          <div class="sum-icon-box bg-emerald-tint">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
        <span class="sum-val text-emerald-600">{{ attendanceData.summary.present_count }}</span>
        <span class="sum-sub">Attended Lectures</span>
      </div>

      <!-- Absent -->
      <div class="card summary-card variant-rose">
        <div class="sum-top">
          <span class="sum-label">ABSENT PERIODS</span>
          <div class="sum-icon-box bg-rose-tint">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
        <span class="sum-val text-rose-600">{{ attendanceData.summary.absent_count }}</span>
        <span class="sum-sub">{{ attendanceData.summary.absent_count === 0 ? '✓ Perfect Attendance' : 'Missed Periods' }}</span>
      </div>

      <!-- Attendance Rate -->
      <div class="card summary-card variant-purple">
        <div class="sum-top">
          <span class="sum-label">ATTENDANCE RATE</span>
          <div class="sum-icon-box bg-purple-tint">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
        </div>
        <span class="sum-val" :class="attendanceData.summary.attendance_percentage >= 80 ? 'text-emerald-600' : 'text-amber-600'">
          {{ attendanceData.summary.attendance_percentage }}%
        </span>
        <span class="sum-sub">Minimum 75% Requirement</span>
      </div>
    </section>

    <!-- Attendance by Subject Breakdown -->
    <section v-if="attendanceData && attendanceData.by_subject.length > 0" class="card section-panel">
      <div class="panel-header-simple">
        <h3 class="panel-title">Subject-Wise Attendance Breakdown</h3>
        <p class="panel-sub">Performance metrics calculated across your enrolled subjects.</p>
      </div>

      <div class="subject-att-grid">
        <div v-for="sub in attendanceData.by_subject" :key="sub.subject_id" class="subject-att-card">
          <div class="subj-header">
            <h4 class="subj-name" :title="sub.subject_name">{{ sub.subject_name }}</h4>
            <span class="subj-pct" :class="sub.attendance_percentage >= 80 ? 'pct-good' : 'pct-warn'">
              {{ sub.attendance_percentage }}%
            </span>
          </div>

          <!-- Progress Bar -->
          <div class="progress-track">
            <div
              class="progress-fill"
              :class="sub.attendance_percentage >= 80 ? 'fill-good' : 'fill-warn'"
              :style="{ width: `${Math.min(sub.attendance_percentage, 100)}%` }"
            />
          </div>

          <div class="subj-stats-row">
            <div class="subj-stat">
              <span class="lbl">Present</span>
              <strong class="val text-emerald-600">{{ sub.present_count }}</strong>
            </div>
            <div class="subj-stat">
              <span class="lbl">Absent</span>
              <strong class="val" :class="sub.absent_count > 0 ? 'text-rose-600' : 'text-slate-600'">{{ sub.absent_count }}</strong>
            </div>
            <div class="subj-stat">
              <span class="lbl">Total</span>
              <strong class="val text-slate-800">{{ sub.total_classes }}</strong>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Filter Bar Card -->
    <section class="card filter-card" aria-label="Filter Attendance Records">
      <div class="filter-controls-grid">
        <div class="filter-group">
          <label for="year-select" class="filter-label">Academic Year</label>
          <div class="select-box">
            <select id="year-select" v-model="selectedYear" class="form-select" @change="fetchAttendance">
              <option v-for="y in academicYears" :key="y" :value="y">{{ y }}</option>
            </select>
          </div>
        </div>

        <div class="filter-group">
          <label for="month-select" class="filter-label">Month</label>
          <div class="select-box">
            <select id="month-select" v-model="selectedMonth" class="form-select" @change="fetchAttendance">
              <option value="">All Months</option>
              <option v-for="m in monthsList" :key="m.value" :value="m.value">{{ m.label }}</option>
            </select>
          </div>
        </div>

        <div class="filter-group">
          <label for="subject-select" class="filter-label">Subject</label>
          <div class="select-box">
            <select id="subject-select" v-model="selectedSubjectId" class="form-select" @change="fetchAttendance">
              <option value="">All Subjects</option>
              <option
                v-for="sub in (attendanceData?.by_subject || [])"
                :key="sub.subject_id"
                :value="sub.subject_id.toString()"
              >
                {{ sub.subject_name }}
              </option>
            </select>
          </div>
        </div>

        <div class="filter-group">
          <label for="status-select" class="filter-label">Status</label>
          <div class="select-box">
            <select id="status-select" v-model="selectedStatus" class="form-select" @change="fetchAttendance">
              <option value="">All Statuses</option>
              <option value="PRESENT">Present Only</option>
              <option value="ABSENT">Absent Only</option>
              <option value="EXCUSED">Excused Only</option>
            </select>
          </div>
        </div>

        <div class="filter-actions">
          <button type="button" class="reset-btn" @click="resetFilters">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>Reset</span>
          </button>
        </div>
      </div>
    </section>

    <!-- Loading State -->
    <div v-if="isLoading" class="card loading-card">
      <div class="spinner" />
      <span>Filtering student attendance records from PostgreSQL...</span>
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
        <p class="error-title">Unable to Load Attendance</p>
        <p class="error-desc">{{ errorMessage }}</p>
      </div>
      <button type="button" class="retry-btn" @click="fetchAttendance">Try Again</button>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="!attendanceData || attendanceData.history.length === 0"
      class="card empty-card"
    >
      <div class="empty-icon-wrap">
        <svg class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
        </svg>
      </div>
      <h3 class="empty-title">No Attendance Records Found</h3>
      <p class="empty-desc">No attendance entries matched the selected academic filters or no logs have been recorded for this period.</p>
    </div>

    <!-- Attendance Records Table Card -->
    <section v-else class="card section-panel">
      <div class="panel-header-simple">
        <div class="flex-between">
          <div>
            <h3 class="panel-title">Detailed Period Attendance Logs</h3>
            <p class="panel-sub">Showing {{ attendanceData.history.length }} recorded period entries.</p>
          </div>
          <span class="count-pill">{{ attendanceData.history.length }} Records</span>
        </div>
      </div>

      <div class="table-responsive-wrapper">
        <table class="somroyal-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Subject</th>
              <th>Period Time</th>
              <th>Teacher</th>
              <th>Status</th>
              <th>Remarks</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="rec in attendanceData.history" :key="rec.id">
              <td class="font-bold text-slate-900">{{ formatDate(rec.date) }}</td>
              <td class="font-semibold text-slate-800">{{ rec.subject_name || 'Subject' }}</td>
              <td>
                <span class="time-badge">
                  {{ rec.period || 'Standard Period' }}
                </span>
              </td>
              <td class="text-slate-600">{{ rec.teacher_name || 'Faculty Member' }}</td>
              <td>
                <span
                  class="status-pill"
                  :class="{
                    'status-present': rec.status === 'PRESENT',
                    'status-absent': rec.status === 'ABSENT',
                    'status-excused': rec.status === 'EXCUSED' || rec.status === 'LATE',
                  }"
                >
                  <span class="status-dot" />
                  {{ rec.status }}
                </span>
              </td>
              <td class="text-slate-500 font-normal">
                {{ rec.remarks || '—' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
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

/* Base Card Style */
.card {
  background-color: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
}

/* Summary KPI Cards Grid (4 columns) */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.15rem;
}

.summary-card {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.sum-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.sum-label {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: #64748B;
}

.sum-icon-box {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sum-icon-box svg {
  width: 17px;
  height: 17px;
}

.bg-blue-tint { background: #EFF6FF; color: #2563EB; }
.bg-emerald-tint { background: #ECFDF5; color: #059669; }
.bg-rose-tint { background: #FEF2F2; color: #DC2626; }
.bg-purple-tint { background: #FAF5FF; color: #7C3AED; }

.sum-val {
  font-size: 1.6rem;
  font-weight: 800;
  color: #0F172A;
  line-height: 1.15;
  margin-bottom: 0.35rem;
}

.sum-sub {
  font-size: 0.74rem;
  color: #64748B;
}

/* Subject Breakdown */
.section-panel {
  padding: 1.5rem;
}

.panel-header-simple {
  margin-bottom: 1.25rem;
}

.flex-between {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
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

.count-pill {
  font-size: 0.75rem;
  font-weight: 700;
  background: #F1F5F9;
  color: #475569;
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  border: 1px solid #E2E8F0;
}

.subject-att-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1rem;
}

.subject-att-card {
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  transition: all 0.15s ease;
}

.subject-att-card:hover {
  background: #FFFFFF;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

.subj-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.subj-name {
  font-size: 0.88rem;
  font-weight: 700;
  color: #0F172A;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.subj-pct {
  font-size: 0.78rem;
  font-weight: 800;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
}

.pct-good {
  background: #ECFDF5;
  color: #059669;
  border: 1px solid #A7F3D0;
}

.pct-warn {
  background: #FFFBEB;
  color: #D97706;
  border: 1px solid #FDE68A;
}

.progress-track {
  height: 6px;
  border-radius: 9999px;
  background: #E2E8F0;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.4s ease;
}

.fill-good {
  background: linear-gradient(90deg, #10B981, #059669);
}

.fill-warn {
  background: linear-gradient(90deg, #F59E0B, #D97706);
}

.subj-stats-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid #E2E8F0;
  padding-top: 0.5rem;
}

.subj-stat {
  display: flex;
  flex-direction: column;
  line-height: 1.15;
}

.subj-stat .lbl {
  font-size: 0.68rem;
  color: #64748B;
}

.subj-stat .val {
  font-size: 0.86rem;
  font-weight: 700;
}

/* Filter Card */
.filter-card {
  padding: 1.25rem 1.5rem;
}

.filter-controls-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr) auto;
  gap: 1rem;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.filter-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #475569;
  letter-spacing: 0.02em;
}

.select-box {
  position: relative;
}

.form-select {
  width: 100%;
  background-color: #F8FAFC;
  border: 1px solid #CBD5E1;
  border-radius: 8px;
  padding: 0.45rem 0.75rem;
  font-size: 0.82rem;
  color: #1E293B;
  outline: none;
  cursor: pointer;
  transition: all 0.15s ease;
}

.form-select:focus {
  background-color: #FFFFFF;
  border-color: #10B981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15);
}

.reset-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.48rem 1rem;
  background-color: #F1F5F9;
  border: 1px solid #CBD5E1;
  border-radius: 8px;
  color: #475569;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.reset-btn:hover {
  background-color: #E2E8F0;
  color: #0F172A;
}

/* Loading, Error, Empty */
.loading-card,
.empty-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1.5rem;
  text-align: center;
  color: #64748B;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #E2E8F0;
  border-top-color: #10B981;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 0.65rem;
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

.empty-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: #F1F5F9;
  color: #94A3B8;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.75rem;
}

.empty-icon {
  width: 26px;
  height: 26px;
}

.empty-title {
  font-size: 1rem;
  font-weight: 700;
  color: #0F172A;
  margin: 0 0 0.25rem 0;
}

.empty-desc {
  font-size: 0.82rem;
  color: #64748B;
  max-width: 420px;
  margin: 0;
}

/* Table Style */
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
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  color: #475569;
  padding: 0.15rem 0.45rem;
  border-radius: 6px;
  font-size: 0.74rem;
  font-weight: 600;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.65rem;
  border-radius: 9999px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: currentColor;
}

.status-present {
  background-color: #ECFDF5;
  color: #065F46;
  border: 1px solid #A7F3D0;
}

.status-absent {
  background-color: #FEF2F2;
  color: #991B1B;
  border: 1px solid #FECACA;
}

.status-excused {
  background-color: #FFFBEB;
  color: #92400E;
  border: 1px solid #FDE68A;
}

/* Responsive Media Queries */
@media (max-width: 1024px) {
  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .filter-controls-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
  }
  .summary-card {
    padding: 0.95rem;
  }
  .sum-val {
    font-size: 1.35rem;
  }
  .filter-controls-grid {
    grid-template-columns: 1fr;
  }
  .reset-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
