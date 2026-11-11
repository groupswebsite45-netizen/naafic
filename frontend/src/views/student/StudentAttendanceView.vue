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
    academicYears.value = ['2025-2026'];
    selectedYear.value = '2025-2026';
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
  <div class="portal-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">My Class Attendance</h1>
        <p class="page-subtitle">Your subject period attendance logs, attendance rate, and unexcused absence audits.</p>
      </div>
    </div>

    <!-- Summary KPI Cards -->
    <div v-if="attendanceData" class="summary-grid">
      <div class="summary-card card blue">
        <span class="sum-label">TOTAL CLASSES</span>
        <span class="sum-val">{{ attendanceData.summary.total_classes }}</span>
        <span class="sum-sub">Scheduled Periods</span>
      </div>
      <div class="summary-card card green">
        <span class="sum-label">CLASSES PRESENT</span>
        <span class="sum-val text-emerald">{{ attendanceData.summary.present_count }}</span>
        <span class="sum-sub">Attended Lectures</span>
      </div>
      <div class="summary-card card red">
        <span class="sum-label">ABSENT</span>
        <span class="sum-val text-rose">{{ attendanceData.summary.absent_count }}</span>
        <span class="sum-sub">{{ attendanceData.summary.absent_count === 0 ? 'Perfect Record' : 'Missed Sessions' }}</span>
      </div>
      <div class="summary-card card purple">
        <span class="sum-label">ATTENDANCE RATE</span>
        <span class="sum-val" :class="attendanceData.summary.attendance_percentage >= 80 ? 'text-emerald' : 'text-amber'">
          {{ attendanceData.summary.attendance_percentage }}%
        </span>
        <span class="sum-sub">Minimum 75% Required</span>
      </div>
    </div>

    <!-- Attendance by Subject -->
    <div v-if="attendanceData && attendanceData.by_subject.length > 0" class="section-block">
      <h3 class="section-title">Attendance by Subject</h3>
      <div class="subject-att-grid">
        <div v-for="sub in attendanceData.by_subject" :key="sub.subject_id" class="card subject-att-card">
          <div class="subj-header">
            <h4 class="subj-name">{{ sub.subject_name }}</h4>
            <span class="subj-pct" :class="sub.attendance_percentage >= 80 ? 'good' : 'warn'">
              {{ sub.attendance_percentage }}%
            </span>
          </div>
          <div class="subj-stats-row">
            <div class="subj-stat">
              <span class="lbl">Present</span>
              <strong class="val text-emerald">{{ sub.present_count }}</strong>
            </div>
            <div class="subj-stat">
              <span class="lbl">Absent</span>
              <strong class="val" :class="sub.absent_count > 0 ? 'text-rose' : ''">{{ sub.absent_count }}</strong>
            </div>
            <div class="subj-stat">
              <span class="lbl">Total</span>
              <strong class="val">{{ sub.total_classes }}</strong>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="card filter-card">
      <div class="filter-group">
        <label for="year-select" class="filter-label">Academic Year</label>
        <select id="year-select" v-model="selectedYear" class="form-select" @change="fetchAttendance">
          <option v-for="y in academicYears" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>

      <div class="filter-group">
        <label for="month-select" class="filter-label">Month</label>
        <select id="month-select" v-model="selectedMonth" class="form-select" @change="fetchAttendance">
          <option value="">All Months</option>
          <option v-for="m in monthsList" :key="m.value" :value="m.value">{{ m.label }}</option>
        </select>
      </div>

      <div class="filter-group">
        <label for="subject-select" class="filter-label">Subject</label>
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

      <div class="filter-group">
        <label for="status-select" class="filter-label">Status</label>
        <select id="status-select" v-model="selectedStatus" class="form-select" @change="fetchAttendance">
          <option value="">All Statuses</option>
          <option value="PRESENT">Present Only</option>
          <option value="ABSENT">Absent Only</option>
          <option value="EXCUSED">Excused Only</option>
        </select>
      </div>

      <div class="filter-actions">
        <button class="reset-btn" @click="resetFilters">Reset</button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="card loading-card">
      <div class="spinner" />
      <span>Querying real attendance records from PostgreSQL...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage" class="card error-card">
      <p class="error-title">Unable to Load Attendance</p>
      <p class="error-desc">{{ errorMessage }}</p>
      <button class="retry-btn" @click="fetchAttendance">Try Again</button>
    </div>

    <!-- Attendance History List -->
    <div v-else-if="attendanceData">
      <div v-if="attendanceData.history.length === 0" class="card empty-card">
        <div class="empty-icon-wrap">
          <svg class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
        <h4 class="empty-title">No Attendance Records Found</h4>
        <p class="empty-desc">No attendance entries match your selected criteria.</p>
      </div>

      <div v-else class="history-list">
        <!-- Desktop Table View -->
        <div class="desktop-table-wrap card">
          <table class="att-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Subject</th>
                <th>Period</th>
                <th>Teacher</th>
                <th>Status</th>
                <th>Remarks</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in attendanceData.history" :key="item.id">
                <td class="font-bold">{{ formatDate(item.date) }}</td>
                <td>
                  <strong>{{ item.subject_name }}</strong>
                  <span v-if="item.subject_code" class="sub-code">{{ item.subject_code }}</span>
                </td>
                <td class="font-mono">{{ item.period || 'Scheduled Period' }}</td>
                <td>{{ item.teacher_name || 'Assigned Faculty' }}</td>
                <td>
                  <span class="status-pill" :class="item.status.toLowerCase()">
                    {{ item.status }}
                  </span>
                </td>
                <td class="remarks-cell">{{ item.remarks || '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile Stacked Card View -->
        <div class="mobile-cards-wrap">
          <div v-for="item in attendanceData.history" :key="item.id" class="card mobile-att-card">
            <div class="card-top-row">
              <span class="card-date">{{ formatDate(item.date) }}</span>
              <span class="status-pill" :class="item.status.toLowerCase()">
                {{ item.status }}
              </span>
            </div>
            <h4 class="card-subj">{{ item.subject_name }}</h4>
            <div class="card-meta">
              <span class="meta-item font-mono">{{ item.period || '08:00 - 09:00' }}</span>
              <span v-if="item.teacher_name" class="meta-item">&bull; {{ item.teacher_name }}</span>
            </div>
            <p v-if="item.remarks" class="card-remarks">Note: {{ item.remarks }}</p>
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

/* Summary Grid */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.summary-card {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  border-left: 4px solid var(--brand-primary);
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
}

.summary-card.blue { border-left-color: #0284c7; }
.summary-card.green { border-left-color: #10b981; }
.summary-card.red { border-left-color: #ef4444; }
.summary-card.purple { border-left-color: #8b5cf6; }

.sum-label {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--text-muted);
}

.sum-val {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--text-primary);
}

.sum-sub {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.text-emerald { color: #10b981; }
.text-rose { color: #ef4444; }
.text-amber { color: #f59e0b; }

/* Subject Breakdown */
.section-block {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.section-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.subject-att-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
}

.subject-att-card {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
}

.subj-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-subtle);
  padding-bottom: 0.4rem;
}

.subj-name {
  font-size: 0.95rem;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}

.subj-pct {
  font-size: 0.78rem;
  font-weight: 800;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.subj-pct.good {
  background-color: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.subj-pct.warn {
  background-color: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.subj-stats-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
}

.subj-stat {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.subj-stat .lbl {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.subj-stat .val {
  font-size: 0.95rem;
}

/* Filter Card */
.filter-card {
  padding: 1rem 1.25rem;
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 1rem;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  flex: 1;
  min-width: 140px;
}

.filter-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
}

.form-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-subtle);
  background-color: var(--bg-surface-secondary);
  color: var(--text-primary);
  border-radius: 6px;
  font-size: 0.85rem;
  outline: none;
}

.filter-actions {
  display: flex;
  align-items: flex-end;
}

.reset-btn {
  padding: 0.5rem 0.85rem;
  background: none;
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
}

.reset-btn:hover {
  background-color: var(--bg-surface-secondary);
  color: var(--text-primary);
}

/* Table View */
.desktop-table-wrap {
  overflow-x: auto;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
}

.att-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.88rem;
}

.att-table th {
  background: var(--bg-surface-secondary);
  padding: 0.75rem 1rem;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border-subtle);
}

.att-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-subtle);
  color: var(--text-primary);
}

.sub-code {
  display: block;
  font-size: 0.72rem;
  color: var(--text-muted);
}

.status-pill {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 4px;
}

.status-pill.present {
  background-color: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.status-pill.absent {
  background-color: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.status-pill.excused {
  background-color: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.font-bold { font-weight: 700; }
.font-mono { font-family: monospace; font-size: 0.8rem; }
.remarks-cell { font-size: 0.8rem; color: var(--text-muted); }

/* Mobile Cards View */
.mobile-cards-wrap {
  display: none;
  flex-direction: column;
  gap: 0.75rem;
}

.mobile-att-card {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
}

.card-top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-date {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-primary);
}

.card-subj {
  font-size: 1rem;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}

.card-meta {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.card-remarks {
  font-size: 0.78rem;
  color: var(--text-secondary);
  font-style: italic;
  margin: 0;
}

/* Empty & Loading */
.loading-card, .empty-card, .error-card {
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

.empty-icon-wrap {
  width: 48px;
  height: 48px;
  background-color: var(--bg-surface-secondary);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-icon {
  width: 1.5rem;
  height: 1.5rem;
  color: var(--text-muted);
}

.empty-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.empty-desc {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin: 0;
}

@media (max-width: 768px) {
  .desktop-table-wrap {
    display: none;
  }
  .mobile-cards-wrap {
    display: flex;
  }
}
</style>
