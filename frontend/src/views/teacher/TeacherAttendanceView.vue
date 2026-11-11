<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { attendanceService } from '../../services/attendanceService';
import {
  TeacherAttendanceOptionsResponse,
  TeacherAttendanceClassOption,
  TeacherAttendanceSubjectOption,
  TeacherAttendanceRosterResponse,
  StudentAttendanceRosterItem,
  TeacherAttendanceSessionItem,
  TeacherAttendanceSummaryResponse,
  TeacherStudentAttendanceSummaryItem,
} from '../../types/attendance';

const route = useRoute();

// Active Tab
const activeTab = ref<'take' | 'history' | 'summary'>('take');

// Options & Selection
const options = ref<TeacherAttendanceOptionsResponse | null>(null);
const selectedYear = ref<string>('');
const selectedClassId = ref<number | null>(null);
const selectedSubjectId = ref<number | null>(null);
const selectedDate = ref<string>(getTodayDateString());

// Loading & UI States
const isLoadingOptions = ref(true);
const isLoadingRoster = ref(false);
const isSaving = ref(false);
const isLoadingHistory = ref(false);
const isLoadingSummary = ref(false);
const notification = ref<{ type: 'success' | 'error'; message: string } | null>(null);
const isConfirmSaveModalOpen = ref(false);

// Roster Data
const rosterData = ref<TeacherAttendanceRosterResponse | null>(null);
const historySessions = ref<TeacherAttendanceSessionItem[]>([]);
const summaryData = ref<TeacherAttendanceSummaryResponse | null>(null);
const summarySearchQuery = ref('');

// Student History Modal
const selectedStudentDetail = ref<TeacherStudentAttendanceSummaryItem | null>(null);
const isStudentModalOpen = ref(false);

function getTodayDateString(): string {
  const d = new Date();
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function showNotification(type: 'success' | 'error', message: string) {
  notification.value = { type, message };
  setTimeout(() => {
    notification.value = null;
  }, 5000);
}

// Filtered dropdowns
const availableClasses = computed<TeacherAttendanceClassOption[]>(() => {
  if (!options.value) return [];
  if (!selectedYear.value) return options.value.classes;
  return options.value.classes.filter((c) => c.academic_year === selectedYear.value);
});

const availableSubjects = computed<TeacherAttendanceSubjectOption[]>(() => {
  if (!options.value || !selectedClassId.value) return [];
  return options.value.subjects.filter((s) => s.class_id === selectedClassId.value);
});

// Computed Counters
const presentCount = computed(() => {
  if (!rosterData.value) return 0;
  return rosterData.value.students.filter((s) => s.status === 'PRESENT' || s.status === 'LATE').length;
});

const absentCount = computed(() => {
  if (!rosterData.value) return 0;
  return rosterData.value.students.filter((s) => s.status === 'ABSENT' || s.status === 'EXCUSED').length;
});

const isFutureDate = computed(() => {
  if (!selectedDate.value) return false;
  return selectedDate.value > getTodayDateString();
});

const filteredStudentSummaries = computed(() => {
  if (!summaryData.value) return [];
  if (!summarySearchQuery.value.trim()) return summaryData.value.students;
  const q = summarySearchQuery.value.toLowerCase().trim();
  return summaryData.value.students.filter(
    (s) => s.student_name.toLowerCase().includes(q) || s.admission_number.toLowerCase().includes(q)
  );
});

// Load Filter Options
async function loadOptions() {
  isLoadingOptions.value = true;
  try {
    const data = await attendanceService.getOptions();
    options.value = data;

    const queryYear = route.query.academic_year as string;
    const queryClassId = route.query.class_id ? Number(route.query.class_id) : null;
    const querySubjectId = route.query.subject_id ? Number(route.query.subject_id) : null;

    if (queryYear && data.academic_years.includes(queryYear)) {
      selectedYear.value = queryYear;
    } else if (data.academic_years.length > 0) {
      selectedYear.value = data.academic_years[0];
    }

    if (queryClassId && data.classes.some((c) => c.id === queryClassId)) {
      selectedClassId.value = queryClassId;
      const subs = data.subjects.filter((s) => s.class_id === queryClassId);
      if (querySubjectId && subs.some((s) => s.id === querySubjectId)) {
        selectedSubjectId.value = querySubjectId;
      } else if (subs.length > 0) {
        selectedSubjectId.value = subs[0].id;
      }
    } else if (data.classes.length > 0) {
      selectedClassId.value = data.classes[0].id;
      const subs = data.subjects.filter((s) => s.class_id === data.classes[0].id);
      if (subs.length > 0) {
        selectedSubjectId.value = subs[0].id;
      }
    }

    if (selectedClassId.value && selectedSubjectId.value) {
      await fetchRoster();
    }
  } catch (err: any) {
    showNotification('error', err?.response?.data?.error?.message || 'Failed to load teacher class options.');
  } finally {
    isLoadingOptions.value = false;
  }
}

// Watchers for cascading dropdowns
watch(selectedClassId, (newClassId) => {
  if (options.value && newClassId) {
    const subs = options.value.subjects.filter((s) => s.class_id === newClassId);
    if (subs.length > 0) {
      selectedSubjectId.value = subs[0].id;
    } else {
      selectedSubjectId.value = null;
    }
    if (activeTab.value === 'take') {
      fetchRoster();
    } else if (activeTab.value === 'history') {
      fetchHistory();
    } else if (activeTab.value === 'summary') {
      fetchSummary();
    }
  }
});

watch(selectedSubjectId, (newSubId) => {
  if (newSubId && selectedClassId.value) {
    if (activeTab.value === 'take') {
      fetchRoster();
    } else if (activeTab.value === 'summary') {
      fetchSummary();
    }
  }
});

watch(selectedDate, (newDate) => {
  if (newDate && selectedClassId.value && selectedSubjectId.value && activeTab.value === 'take') {
    fetchRoster();
  }
});

// Fetch Roster
async function fetchRoster() {
  if (!selectedClassId.value || !selectedSubjectId.value || !selectedDate.value) return;

  if (isFutureDate.value) {
    showNotification('error', 'Future attendance dates are blocked. Please select today or a previous date.');
    return;
  }

  isLoadingRoster.value = true;
  try {
    const data = await attendanceService.getRoster({
      class_id: selectedClassId.value,
      subject_id: selectedSubjectId.value,
      date: selectedDate.value,
      academic_year: selectedYear.value,
    });
    rosterData.value = data;
  } catch (err: any) {
    showNotification('error', err?.response?.data?.error?.message || 'Failed to load class attendance roster.');
    rosterData.value = null;
  } finally {
    isLoadingRoster.value = false;
  }
}

// Toggle Student ON / OFF
function toggleStudentStatus(std: StudentAttendanceRosterItem) {
  if (std.status === 'PRESENT') {
    std.status = 'ABSENT';
  } else {
    std.status = 'PRESENT';
    std.remarks = null;
  }
}

// Save Attendance
async function handleSaveAttendance() {
  if (!rosterData.value || !selectedClassId.value || !selectedSubjectId.value) return;

  isSaving.value = true;
  try {
    const payload = {
      class_id: selectedClassId.value,
      subject_id: selectedSubjectId.value,
      academic_year: rosterData.value.academic_year || selectedYear.value || '2025-2026',
      date: selectedDate.value,
      entries: rosterData.value.students.map((s) => ({
        student_id: s.student_id,
        status: s.status,
        remarks: s.remarks || null,
      })),
    };

    const res = await attendanceService.saveAttendance(payload);
    showNotification('success', `Attendance saved: ${res.present_count} Present, ${res.absent_count} Absent in ${res.class_name}.`);
    isConfirmSaveModalOpen.value = false;
    await fetchRoster();
  } catch (err: any) {
    showNotification('error', err?.response?.data?.error?.message || 'Failed to save attendance records.');
  } finally {
    isSaving.value = false;
  }
}

// Mark All Present
function markAllPresent() {
  if (!rosterData.value) return;
  rosterData.value.students.forEach((s) => {
    s.status = 'PRESENT';
    s.remarks = null;
  });
}

// Fetch History
async function fetchHistory() {
  isLoadingHistory.value = true;
  try {
    const list = await attendanceService.getHistory({
      class_id: selectedClassId.value || undefined,
      academic_year: selectedYear.value || undefined,
    });
    historySessions.value = list;
  } catch (err: any) {
    showNotification('error', err?.response?.data?.error?.message || 'Failed to load attendance history.');
  } finally {
    isLoadingHistory.value = false;
  }
}

// Load Session from History
function loadSessionFromHistory(session: TeacherAttendanceSessionItem) {
  selectedClassId.value = session.class_id;
  selectedSubjectId.value = session.subject_id;
  selectedDate.value = session.date;
  selectedYear.value = session.academic_year;
  activeTab.value = 'take';
}

// Fetch Summary
async function fetchSummary() {
  if (!selectedClassId.value) return;
  isLoadingSummary.value = true;
  try {
    const data = await attendanceService.getSummary({
      class_id: selectedClassId.value,
      subject_id: selectedSubjectId.value || undefined,
    });
    summaryData.value = data;
  } catch (err: any) {
    showNotification('error', err?.response?.data?.error?.message || 'Failed to load attendance summary.');
  } finally {
    isLoadingSummary.value = false;
  }
}

function openStudentHistoryModal(std: TeacherStudentAttendanceSummaryItem) {
  selectedStudentDetail.value = std;
  isStudentModalOpen.value = true;
}

function handleTabChange(tab: 'take' | 'history' | 'summary') {
  activeTab.value = tab;
  if (tab === 'history') {
    fetchHistory();
  } else if (tab === 'summary') {
    fetchSummary();
  } else if (tab === 'take') {
    fetchRoster();
  }
}

onMounted(() => {
  loadOptions();
});
</script>

<template>
  <div class="attendance-page">
    <!-- Toast Notification -->
    <div v-if="notification" class="toast-banner" :class="notification.type">
      <div class="toast-content">
        <span>{{ notification.message }}</span>
        <button class="toast-close" aria-label="Dismiss alert" @click="notification = null">&times;</button>
      </div>
    </div>

    <!-- Header & Navigation -->
    <div class="page-header">
      <div class="header-main">
        <h1 class="page-title">Class Attendance Management</h1>
        <p class="page-subtitle">
          Record daily attendance, toggle absences with optional reasons, and monitor student attendance rates.
        </p>
      </div>

      <!-- Navigation Tabs -->
      <div class="tab-nav">
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'take' }"
          @click="handleTabChange('take')"
        >
          <svg class="tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>Take Attendance</span>
        </button>

        <button
          class="tab-btn"
          :class="{ active: activeTab === 'history' }"
          @click="handleTabChange('history')"
        >
          <svg class="tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>Session History</span>
        </button>

        <button
          class="tab-btn"
          :class="{ active: activeTab === 'summary' }"
          @click="handleTabChange('summary')"
        >
          <svg class="tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <span>Absence Analytics</span>
        </button>
      </div>
    </div>

    <!-- Filter Toolbar -->
    <div class="filters-card card">
      <div class="filters-grid">
        <div class="form-group">
          <label class="form-label">Academic Year</label>
          <select v-model="selectedYear" class="form-select" :disabled="isLoadingOptions">
            <option v-for="yr in options?.academic_years" :key="yr" :value="yr">{{ yr }}</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Select Class</label>
          <select v-model="selectedClassId" class="form-select" :disabled="isLoadingOptions || availableClasses.length === 0">
            <option v-if="availableClasses.length === 0" :value="null">No assigned classes</option>
            <option v-for="c in availableClasses" :key="c.id" :value="c.id">
              {{ c.name }} ({{ c.code }})
            </option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Select Subject</label>
          <select v-model="selectedSubjectId" class="form-select" :disabled="isLoadingOptions || availableSubjects.length === 0">
            <option v-if="availableSubjects.length === 0" :value="null">No assigned subjects</option>
            <option v-for="s in availableSubjects" :key="s.id" :value="s.id">
              {{ s.name }} ({{ s.code }})
            </option>
          </select>
        </div>

        <div v-if="activeTab === 'take'" class="form-group">
          <label class="form-label">Attendance Date</label>
          <input
            v-model="selectedDate"
            type="date"
            class="form-input"
            :max="getTodayDateString()"
            :disabled="isLoadingOptions"
          />
        </div>
      </div>

      <!-- Quick Preset Actions -->
      <div v-if="activeTab === 'take'" class="filter-actions">
        <div class="date-presets">
          <button
            class="preset-btn"
            :class="{ active: selectedDate === getTodayDateString() }"
            @click="selectedDate = getTodayDateString()"
          >
            Today's Date
          </button>
        </div>
      </div>
    </div>

    <!-- =================================================================== -->
    <!-- TAB 1: TAKE ATTENDANCE                                              -->
    <!-- =================================================================== -->
    <div v-if="activeTab === 'take'" class="tab-content">
      <!-- Loading State -->
      <div v-if="isLoadingRoster" class="card empty-loading">
        <div class="spinner" />
        <span>Loading class roster from PostgreSQL...</span>
      </div>

      <!-- Future Date Alert -->
      <div v-else-if="isFutureDate" class="alert-box error">
        <strong>Future Date Blocked:</strong> Attendance cannot be recorded for future dates. Please select today or a previous date.
      </div>

      <!-- Empty State -->
      <div v-else-if="!rosterData || rosterData.students.length === 0" class="card empty-box">
        <svg class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        <p class="empty-title">No Enrolled Students Found</p>
        <p class="empty-desc">No active students are currently enrolled in this class.</p>
      </div>

      <!-- Roster Active -->
      <div v-else class="roster-view">
        <!-- Live Summary Banner -->
        <div class="summary-banner card">
          <div class="summary-info">
            <span class="session-badge" :class="rosterData.is_recorded ? 'recorded' : 'new'">
              {{ rosterData.is_recorded ? 'Saved Session' : 'New Session (Unsaved)' }}
            </span>
            <div class="session-details">
              <strong>{{ rosterData.class_name }}</strong> • {{ rosterData.subject_name }} • {{ rosterData.date }}
            </div>
          </div>

          <div class="summary-pills">
            <div class="stat-pill total">
              <span class="pill-label">Total</span>
              <span class="pill-val">{{ rosterData.total_students }}</span>
            </div>
            <div class="stat-pill present">
              <span class="pill-label">Present</span>
              <span class="pill-val">{{ presentCount }}</span>
            </div>
            <div class="stat-pill absent">
              <span class="pill-label">Absent</span>
              <span class="pill-val">{{ absentCount }}</span>
            </div>
          </div>

          <div class="banner-actions">
            <button class="btn btn-outline btn-touch" @click="markAllPresent">
              Mark All Present
            </button>
            <button class="btn btn-primary btn-touch" :disabled="isSaving" @click="isConfirmSaveModalOpen = true">
              Save Attendance
            </button>
          </div>
        </div>

        <!-- Desktop Roster Table -->
        <div class="desktop-roster card">
          <div class="table-responsive" tabindex="0" role="region" aria-label="Attendance marking roster table">
            <table class="roster-table">
              <thead>
                <tr>
                  <th style="width: 50px;">#</th>
                  <th>Student Name</th>
                  <th>Admission #</th>
                  <th style="width: 140px; text-align: center;">Status (ON / OFF)</th>
                  <th>Absence Reason (Optional)</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(std, idx) in rosterData.students"
                  :key="std.student_id"
                  :class="{ 'row-absent': std.status === 'ABSENT' || std.status === 'EXCUSED' }"
                >
                  <td class="text-muted">{{ idx + 1 }}</td>
                  <td class="font-bold">
                    <span class="student-name">{{ std.student_name }}</span>
                    <span v-if="std.gender" class="gender-tag">{{ std.gender }}</span>
                  </td>
                  <td><code>{{ std.admission_number }}</code></td>
                  <td style="text-align: center;">
                    <!-- ON / OFF Toggle Switch -->
                    <button
                      type="button"
                      class="toggle-switch"
                      :class="{ 'is-on': std.status === 'PRESENT' || std.status === 'LATE', 'is-off': std.status === 'ABSENT' || std.status === 'EXCUSED' }"
                      :aria-label="`Toggle attendance for ${std.student_name}`"
                      @click="toggleStudentStatus(std)"
                    >
                      <span class="switch-handle" />
                      <span class="switch-text">{{ (std.status === 'PRESENT' || std.status === 'LATE') ? 'ON' : 'OFF' }}</span>
                    </button>
                  </td>
                  <td>
                    <div v-if="std.status === 'ABSENT' || std.status === 'EXCUSED'" class="reason-wrap">
                      <input
                        v-model="std.remarks"
                        type="text"
                        class="reason-input"
                        placeholder="e.g., Sick, Family matter, Unexcused"
                      />
                    </div>
                    <span v-else class="text-muted status-present-tag">Present in class</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Mobile Roster Cards (<= 768px) -->
        <div class="mobile-roster">
          <!-- Mobile Bulk Action Header -->
          <div class="mobile-bulk-actions">
            <button class="btn btn-outline btn-touch btn-block" @click="markAllPresent">
              Mark All Present
            </button>
          </div>

          <div
            v-for="(std, idx) in rosterData.students"
            :key="std.student_id"
            class="student-card card"
            :class="{ 'card-absent': std.status === 'ABSENT' || std.status === 'EXCUSED' }"
          >
            <div class="card-header">
              <div class="student-meta">
                <span class="index-num">#{{ idx + 1 }}</span>
                <div class="student-info-col">
                  <h4 class="student-title">{{ std.student_name }}</h4>
                  <span class="adm-code">{{ std.admission_number }}</span>
                </div>
              </div>

              <!-- Switch -->
              <button
                type="button"
                class="toggle-switch"
                :class="{ 'is-on': std.status === 'PRESENT' || std.status === 'LATE', 'is-off': std.status === 'ABSENT' || std.status === 'EXCUSED' }"
                :aria-label="`Toggle attendance for ${std.student_name}`"
                @click="toggleStudentStatus(std)"
              >
                <span class="switch-handle" />
                <span class="switch-text">{{ (std.status === 'PRESENT' || std.status === 'LATE') ? 'ON' : 'OFF' }}</span>
              </button>
            </div>

            <div v-if="std.status === 'ABSENT' || std.status === 'EXCUSED'" class="card-reason">
              <label class="reason-label">Reason for absence (optional):</label>
              <input
                v-model="std.remarks"
                type="text"
                class="reason-input"
                placeholder="e.g. Sick, Family emergency"
              />
            </div>
          </div>
        </div>

        <!-- Bottom Save Floating Bar on Mobile -->
        <div class="mobile-save-bar">
          <div class="mobile-save-counts">
            <span class="text-emerald font-bold">{{ presentCount }} Present</span>
            <span class="text-rose font-bold">{{ absentCount }} Absent</span>
          </div>
          <button class="btn btn-primary btn-touch btn-block" :disabled="isSaving" @click="isConfirmSaveModalOpen = true">
            Save Attendance
          </button>
        </div>
      </div>
    </div>

    <!-- =================================================================== -->
    <!-- TAB 2: SESSION HISTORY                                              -->
    <!-- =================================================================== -->
    <div v-else-if="activeTab === 'history'" class="tab-content">
      <div v-if="isLoadingHistory" class="card empty-loading">
        <div class="spinner" />
        <span>Loading attendance history from PostgreSQL...</span>
      </div>

      <div v-else-if="historySessions.length === 0" class="card empty-box">
        <p class="empty-title">No Previous Attendance Sessions Recorded</p>
        <p class="empty-desc">No attendance logs exist yet for this class selection.</p>
      </div>

      <div v-else class="history-grid">
        <div v-for="s in historySessions" :key="s.session_key" class="session-card card">
          <div class="session-top">
            <span class="session-date">{{ s.date }}</span>
            <span class="rate-badge" :class="s.attendance_percentage >= 80 ? 'green' : 'amber'">
              {{ s.attendance_percentage }}% Present
            </span>
          </div>
          <div class="session-body">
            <h4 class="session-class">{{ s.class_name }}</h4>
            <p class="session-sub">{{ s.subject_name }}</p>
            <div class="session-stats">
              <span>Total: <strong>{{ s.total_students }}</strong></span>
              <span class="text-emerald">Present: <strong>{{ s.present_count }}</strong></span>
              <span class="text-rose">Absent: <strong>{{ s.absent_count }}</strong></span>
            </div>
          </div>
          <div class="session-footer">
            <button class="btn btn-sm btn-outline btn-touch btn-block" @click="loadSessionFromHistory(s)">
              View / Edit Attendance
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- =================================================================== -->
    <!-- TAB 3: STUDENT ABSENCE ANALYTICS                                   -->
    <!-- =================================================================== -->
    <div v-else-if="activeTab === 'summary'" class="tab-content">
      <div v-if="isLoadingSummary" class="card empty-loading">
        <div class="spinner" />
        <span>Calculating student attendance rates from PostgreSQL...</span>
      </div>

      <div v-else-if="!summaryData || summaryData.students.length === 0" class="card empty-box">
        <p class="empty-title">No Summary Data Available</p>
        <p class="empty-desc">No attendance records found for this class.</p>
      </div>

      <div v-else class="summary-section">
        <!-- Search bar -->
        <div class="search-bar-wrap card">
          <input
            v-model="summarySearchQuery"
            type="text"
            class="form-input search-input"
            placeholder="Search student by name or admission number..."
          />
        </div>

        <!-- Desktop Summary Table -->
        <div class="card summary-table-card desktop-view">
          <div class="table-responsive" tabindex="0" role="region" aria-label="Student attendance summary table">
            <table class="roster-table">
              <thead>
                <tr>
                  <th>Student Name</th>
                  <th>Admission #</th>
                  <th class="text-center">Total Sessions</th>
                  <th class="text-center">Present</th>
                  <th class="text-center">Absent</th>
                  <th class="text-center">Attendance Rate</th>
                  <th style="text-align: right;">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="std in filteredStudentSummaries" :key="std.student_id">
                  <td class="font-bold">{{ std.student_name }}</td>
                  <td><code>{{ std.admission_number }}</code></td>
                  <td class="text-center">{{ std.total_sessions }}</td>
                  <td class="text-center text-emerald font-bold">{{ std.present_count }}</td>
                  <td class="text-center text-rose font-bold">{{ std.absent_count }}</td>
                  <td class="text-center">
                    <span
                      class="rate-pill"
                      :class="std.attendance_percentage >= 85 ? 'high' : (std.attendance_percentage >= 70 ? 'medium' : 'low')"
                    >
                      {{ std.attendance_percentage }}%
                    </span>
                  </td>
                  <td style="text-align: right;">
                    <button class="btn btn-sm btn-outline" @click="openStudentHistoryModal(std)">
                      View Absence History
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Mobile Summary Cards -->
        <div class="mobile-view summary-mobile-list">
          <div v-for="std in filteredStudentSummaries" :key="std.student_id" class="mobile-summary-card card">
            <div class="mobile-sum-header">
              <h4 class="std-name">{{ std.student_name }}</h4>
              <span
                class="rate-pill"
                :class="std.attendance_percentage >= 85 ? 'high' : (std.attendance_percentage >= 70 ? 'medium' : 'low')"
              >
                {{ std.attendance_percentage }}%
              </span>
            </div>
            <div class="adm-code">{{ std.admission_number }}</div>
            <div class="mobile-sum-metrics">
              <div class="sum-box">
                <span class="sum-lbl">Sessions</span>
                <span class="sum-v">{{ std.total_sessions }}</span>
              </div>
              <div class="sum-box">
                <span class="sum-lbl">Present</span>
                <span class="sum-v text-emerald">{{ std.present_count }}</span>
              </div>
              <div class="sum-box">
                <span class="sum-lbl">Absent</span>
                <span class="sum-v text-rose">{{ std.absent_count }}</span>
              </div>
            </div>
            <button class="btn btn-outline btn-touch btn-block" @click="openStudentHistoryModal(std)">
              View Absence History
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- =================================================================== -->
    <!-- CONFIRMATION MODAL                                                  -->
    <!-- =================================================================== -->
    <div v-if="isConfirmSaveModalOpen" class="modal-backdrop" @click="isConfirmSaveModalOpen = false">
      <div class="modal-card card" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">Save Attendance Confirmation</h3>
          <button class="modal-close" aria-label="Close dialog" @click="isConfirmSaveModalOpen = false">&times;</button>
        </div>
        <div class="modal-body">
          <p>You are about to save the attendance record to PostgreSQL for:</p>
          <div class="confirm-summary-box">
            <div class="confirm-row">
              <span>Class:</span>
              <strong>{{ rosterData?.class_name }}</strong>
            </div>
            <div class="confirm-row">
              <span>Subject:</span>
              <strong>{{ rosterData?.subject_name }}</strong>
            </div>
            <div class="confirm-row">
              <span>Date:</span>
              <strong>{{ selectedDate }}</strong>
            </div>
            <div class="confirm-row">
              <span>Present Students:</span>
              <strong class="text-emerald">{{ presentCount }}</strong>
            </div>
            <div class="confirm-row">
              <span>Absent Students:</span>
              <strong class="text-rose">{{ absentCount }}</strong>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline btn-touch" :disabled="isSaving" @click="isConfirmSaveModalOpen = false">
            Cancel
          </button>
          <button class="btn btn-primary btn-touch" :disabled="isSaving" @click="handleSaveAttendance">
            {{ isSaving ? 'Saving to Database...' : 'Confirm & Save' }}
          </button>
        </div>
      </div>
    </div>

    <!-- =================================================================== -->
    <!-- STUDENT ABSENCE HISTORY MODAL                                       -->
    <!-- =================================================================== -->
    <div v-if="isStudentModalOpen && selectedStudentDetail" class="modal-backdrop" @click="isStudentModalOpen = false">
      <div class="modal-card card large" @click.stop>
        <div class="modal-header">
          <div>
            <h3 class="modal-title">{{ selectedStudentDetail.student_name }}</h3>
            <span class="adm-code">{{ selectedStudentDetail.admission_number }} • {{ selectedStudentDetail.class_name }}</span>
          </div>
          <button class="modal-close" aria-label="Close dialog" @click="isStudentModalOpen = false">&times;</button>
        </div>

        <div class="modal-body">
          <!-- Quick stats -->
          <div class="modal-stats-grid">
            <div class="stat-box">
              <span class="stat-title">Total Sessions</span>
              <span class="stat-num">{{ selectedStudentDetail.total_sessions }}</span>
            </div>
            <div class="stat-box">
              <span class="stat-title">Present Count</span>
              <span class="stat-num text-emerald">{{ selectedStudentDetail.present_count }}</span>
            </div>
            <div class="stat-box">
              <span class="stat-title">Absent Count</span>
              <span class="stat-num text-rose">{{ selectedStudentDetail.absent_count }}</span>
            </div>
            <div class="stat-box">
              <span class="stat-title">Attendance Rate</span>
              <span class="stat-num text-primary">{{ selectedStudentDetail.attendance_percentage }}%</span>
            </div>
          </div>

          <h4 class="sub-heading">Recorded Absence History & Reasons</h4>
          <div v-if="selectedStudentDetail.absent_history.length === 0" class="empty-inline">
            No absences recorded. Student has a 100% attendance track record in this stream.
          </div>
          <div v-else class="table-responsive" tabindex="0" role="region" aria-label="Student absence history table">
            <table class="roster-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Subject</th>
                  <th>Status</th>
                  <th>Reason / Remarks</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(h, i) in selectedStudentDetail.absent_history" :key="i">
                  <td>{{ h.date }}</td>
                  <td>{{ h.subject_name || 'Class Period' }}</td>
                  <td>
                    <span class="status-pill absent">{{ h.status }}</span>
                  </td>
                  <td>{{ h.remarks || 'No reason specified' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-primary btn-touch btn-block-mobile" @click="isStudentModalOpen = false">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.attendance-page {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  max-width: 1300px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.toast-banner {
  padding: 0.85rem 1.25rem;
  border-radius: 8px;
  animation: fadeIn 0.3s ease;
}
.toast-banner.success { background: #ecfdf5; border: 1px solid #a7f3d0; color: #065f46; }
.toast-banner.error { background: #fef2f2; border: 1px solid #fecaca; color: #991b1b; }
.toast-content { display: flex; justify-content: space-between; align-items: center; font-size: 0.9rem; font-weight: 500; }
.toast-close { background: none; border: none; font-size: 1.4rem; cursor: pointer; color: inherit; line-height: 1; }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}
.page-title { font-size: 1.5rem; font-weight: 800; color: var(--text-primary, #0f172a); margin: 0; word-break: break-word; }
.page-subtitle { font-size: 0.85rem; color: var(--text-muted, #64748b); margin: 0.2rem 0 0 0; }

.tab-nav {
  display: flex;
  background: var(--bg-surface-secondary, #f8fafc);
  padding: 0.25rem;
  border-radius: 8px;
  gap: 0.25rem;
  flex-wrap: wrap;
}
.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 0.85rem;
  font-size: 0.82rem;
  font-weight: 600;
  border: none;
  border-radius: 6px;
  background: none;
  color: var(--text-muted, #64748b);
  cursor: pointer;
  min-height: 38px;
  transition: all 0.2s;
}
.tab-btn:hover { color: var(--text-primary, #0f172a); }
.tab-btn.active { background: #ffffff; color: #0284c7; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.tab-icon { width: 1.1rem; height: 1.1rem; flex-shrink: 0; }

.filters-card { padding: 1.25rem; width: 100%; box-sizing: border-box; }
.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}
.form-group { display: flex; flex-direction: column; gap: 0.35rem; }
.form-label { font-size: 0.78rem; font-weight: 700; text-transform: uppercase; color: var(--text-muted, #64748b); }
.form-select, .form-input {
  padding: 0.55rem 0.75rem;
  border: 1px solid var(--border-medium, #cbd5e1);
  border-radius: 6px;
  background: var(--bg-surface, #ffffff);
  font-size: 0.88rem;
  color: var(--text-primary, #0f172a);
  width: 100%;
  box-sizing: border-box;
}

.filter-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-subtle, #e2e8f0);
}
.preset-btn {
  background: #f1f5f9;
  border: 1px solid var(--border-subtle, #e2e8f0);
  padding: 0.4rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  color: #475569;
}
.preset-btn.active { background: #0284c7; color: #ffffff; border-color: #0284c7; }

.tab-content { display: flex; flex-direction: column; gap: 1.25rem; width: 100%; }

.summary-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  flex-wrap: wrap;
  gap: 1rem;
  background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
  border-left: 4px solid #0284c7;
  width: 100%;
  box-sizing: border-box;
}
.session-badge {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  margin-bottom: 0.25rem;
}
.session-badge.new { background: #fef3c7; color: #92400e; }
.session-badge.recorded { background: #dcfce7; color: #166534; }
.session-details { font-size: 0.95rem; color: var(--text-primary, #0f172a); word-break: break-word; }
.summary-pills { display: flex; gap: 0.75rem; flex-wrap: wrap; }
.stat-pill {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.4rem 0.85rem;
  border-radius: 6px;
  min-width: 75px;
}
.stat-pill.total { background: #f1f5f9; }
.stat-pill.present { background: #dcfce7; color: #15803d; }
.stat-pill.absent { background: #fee2e2; color: #b91c1c; }
.pill-label { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; }
.pill-val { font-size: 1.25rem; font-weight: 800; }
.banner-actions { display: flex; gap: 0.5rem; flex-wrap: wrap; }

/* Desktop Table */
.desktop-roster { padding: 0; overflow: hidden; width: 100%; }
.table-responsive { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; }
.roster-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; text-align: left; min-width: 580px; }
.roster-table th { background: var(--bg-surface-secondary, #f8fafc); padding: 0.85rem 1.25rem; font-weight: 700; color: var(--text-secondary, #475569); border-bottom: 1px solid var(--border-subtle, #e2e8f0); }
.roster-table td { padding: 0.85rem 1.25rem; border-bottom: 1px solid var(--border-subtle, #e2e8f0); vertical-align: middle; }
.roster-table tr:hover { background-color: #f8fafc; }
.row-absent { background-color: rgba(254, 242, 242, 0.4); }
.student-name { font-weight: 700; color: var(--text-primary, #0f172a); }
.gender-tag { font-size: 0.7rem; background: #f1f5f9; color: #64748b; padding: 0.1rem 0.35rem; border-radius: 3px; margin-left: 0.4rem; }
.status-present-tag { font-size: 0.8rem; color: #059669; }

/* ON / OFF Switch */
.toggle-switch {
  display: inline-flex;
  align-items: center;
  position: relative;
  width: 80px;
  height: 36px;
  border-radius: 18px;
  border: none;
  cursor: pointer;
  padding: 3px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.12);
  flex-shrink: 0;
}
.toggle-switch.is-on { background-color: #10b981; }
.toggle-switch.is-off { background-color: #ef4444; }
.switch-handle {
  width: 30px;
  height: 30px;
  background-color: #ffffff;
  border-radius: 50%;
  transition: transform 0.25s ease;
  box-shadow: 0 2px 5px rgba(0,0,0,0.25);
}
.toggle-switch.is-on .switch-handle { transform: translateX(44px); }
.toggle-switch.is-off .switch-handle { transform: translateX(0); }
.switch-text {
  position: absolute;
  font-size: 0.75rem;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: 0.05em;
}
.toggle-switch.is-on .switch-text { left: 12px; }
.toggle-switch.is-off .switch-text { right: 12px; }

.reason-input {
  width: 100%;
  max-width: 320px;
  padding: 0.55rem 0.75rem;
  font-size: 0.85rem;
  border: 1px solid #fca5a5;
  background: #ffffff;
  border-radius: 6px;
  color: var(--text-primary, #0f172a);
  box-sizing: border-box;
}

/* Mobile Roster Cards */
.mobile-roster { display: none; flex-direction: column; gap: 0.75rem; width: 100%; }
.mobile-bulk-actions { width: 100%; }
.student-card {
  padding: 1rem;
  border-left: 4px solid #10b981;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  box-sizing: border-box;
  background: var(--bg-surface, #ffffff);
}
.student-card.card-absent { border-left-color: #ef4444; background-color: #fffaf9; }
.card-header { display: flex; justify-content: space-between; align-items: center; gap: 0.5rem; }
.student-meta { display: flex; align-items: center; gap: 0.6rem; min-width: 0; }
.student-info-col { display: flex; flex-direction: column; min-width: 0; }
.index-num { font-size: 0.78rem; color: var(--text-muted, #64748b); font-weight: 700; flex-shrink: 0; }
.student-title { font-size: 0.95rem; font-weight: 700; color: var(--text-primary, #0f172a); margin: 0; word-break: break-word; }
.adm-code { font-size: 0.75rem; color: var(--text-muted, #64748b); font-family: monospace; }
.card-reason {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding-top: 0.5rem;
  border-top: 1px dashed #fecaca;
}
.reason-label { font-size: 0.75rem; font-weight: 600; color: #b91c1c; }

.mobile-save-bar {
  display: none;
  position: sticky;
  bottom: 0;
  left: 0;
  right: 0;
  background: #ffffff;
  border-top: 1px solid var(--border-medium, #cbd5e1);
  padding: 0.85rem 1rem;
  box-shadow: 0 -4px 12px rgba(0,0,0,0.08);
  z-index: 20;
  box-sizing: border-box;
}
.mobile-save-counts {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}

/* History Grid */
.history-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(260px, 100%), 1fr));
  gap: 1.25rem;
  width: 100%;
}
.session-card {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  border-top: 4px solid #0284c7;
  box-sizing: border-box;
}
.session-top { display: flex; justify-content: space-between; align-items: center; }
.session-date { font-weight: 700; font-size: 0.95rem; }
.rate-badge { font-size: 0.75rem; font-weight: 700; padding: 0.2rem 0.5rem; border-radius: 4px; }
.rate-badge.green { background: #dcfce7; color: #15803d; }
.rate-badge.amber { background: #fef3c7; color: #92400e; }
.session-class { margin: 0; font-size: 1.1rem; font-weight: 700; }
.session-sub { margin: 0; font-size: 0.85rem; color: var(--text-muted, #64748b); }
.session-stats {
  display: flex;
  gap: 0.75rem;
  font-size: 0.8rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--border-subtle, #e2e8f0);
  flex-wrap: wrap;
}

/* Summary Section */
.summary-section { display: flex; flex-direction: column; gap: 1rem; width: 100%; }
.search-bar-wrap { padding: 0.75rem 1rem; width: 100%; box-sizing: border-box; }
.search-input { width: 100%; }
.summary-table-card { padding: 0; overflow: hidden; width: 100%; }
.rate-pill {
  font-weight: 800;
  font-size: 0.82rem;
  padding: 0.25rem 0.6rem;
  border-radius: 12px;
  display: inline-block;
}
.rate-pill.high { background: #dcfce7; color: #166534; }
.rate-pill.medium { background: #fef3c7; color: #92400e; }
.rate-pill.low { background: #fee2e2; color: #991b1b; }
.status-pill.absent { background: #fee2e2; color: #b91c1c; font-size: 0.75rem; font-weight: 700; padding: 0.15rem 0.45rem; border-radius: 4px; display: inline-block; }

.desktop-view { display: block; }
.mobile-view { display: none; }
.summary-mobile-list { flex-direction: column; gap: 0.75rem; width: 100%; }
.mobile-summary-card {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  box-sizing: border-box;
}
.mobile-sum-header { display: flex; justify-content: space-between; align-items: center; }
.std-name { margin: 0; font-size: 0.98rem; font-weight: 700; word-break: break-word; }
.mobile-sum-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
  background: var(--bg-surface-secondary, #f8fafc);
  padding: 0.6rem;
  border-radius: 6px;
  text-align: center;
}
.sum-box { display: flex; flex-direction: column; }
.sum-lbl { font-size: 0.68rem; color: var(--text-muted, #64748b); font-weight: 700; text-transform: uppercase; }
.sum-v { font-size: 1rem; font-weight: 800; }

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.55rem 1rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s;
}
.btn-touch { min-height: 44px; }
.btn-primary { background: #0284c7; color: #ffffff; }
.btn-primary:hover:not(:disabled) { background: #0369a1; }
.btn-outline { background: #ffffff; border-color: var(--border-medium, #cbd5e1); color: var(--text-primary, #0f172a); }
.btn-outline:hover:not(:disabled) { background: #f8fafc; }
.btn-sm { padding: 0.35rem 0.65rem; font-size: 0.78rem; min-height: 36px; }
.btn-block { width: 100%; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }

/* Modals */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  padding: 0.75rem;
  box-sizing: border-box;
}
.modal-card {
  width: calc(100% - 24px);
  max-width: 480px;
  max-height: 90vh;
  background: #ffffff;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  border-radius: 8px;
  overflow-y: auto;
  box-sizing: border-box;
}
.modal-card.large { max-width: 700px; }
.modal-header { display: flex; justify-content: space-between; align-items: flex-start; }
.modal-title { margin: 0; font-size: 1.2rem; font-weight: 700; word-break: break-word; }
.modal-close {
  background: none;
  border: none;
  font-size: 1.6rem;
  line-height: 1;
  cursor: pointer;
  color: var(--text-muted, #64748b);
  min-width: 40px;
  min-height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-body { font-size: 0.9rem; }
.confirm-summary-box {
  background: #f8fafc;
  border: 1px solid var(--border-subtle, #e2e8f0);
  border-radius: 6px;
  padding: 0.85rem;
  margin-top: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.confirm-row { display: flex; justify-content: space-between; font-size: 0.88rem; }
.modal-stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem; margin-bottom: 1.25rem; }
.stat-box { background: #f8fafc; padding: 0.65rem; border-radius: 6px; text-align: center; }
.stat-title { font-size: 0.68rem; color: var(--text-muted, #64748b); font-weight: 600; display: block; }
.stat-num { font-size: 1.1rem; font-weight: 800; display: block; }
.sub-heading { font-size: 0.95rem; font-weight: 700; margin: 1rem 0 0.5rem 0; }
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-subtle, #e2e8f0);
}

.empty-loading, .empty-box {
  padding: 3rem 1rem;
  text-align: center;
  color: var(--text-muted, #64748b);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}
.empty-icon { width: 48px; height: 48px; color: #94a3b8; }
.empty-title { font-size: 1.1rem; font-weight: 700; margin: 0; color: var(--text-primary, #0f172a); }
.empty-desc { font-size: 0.85rem; margin: 0; }
.empty-inline { font-size: 0.85rem; color: var(--text-muted, #64748b); font-style: italic; padding: 0.75rem 0; }
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-subtle, #e2e8f0);
  border-top-color: #0284c7;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }

/* Responsive adjustments */
@media (max-width: 768px) {
  .desktop-roster { display: none; }
  .mobile-roster { display: flex; }
  .mobile-save-bar { display: block; }
  .banner-actions { display: none; }
  .summary-banner { flex-direction: column; align-items: stretch; }
  .modal-stats-grid { grid-template-columns: repeat(2, 1fr); }
  .desktop-view { display: none; }
  .mobile-view { display: flex; }
  .btn-block-mobile { width: 100%; }
}

@media (max-width: 480px) {
  .filters-grid { grid-template-columns: 1fr; }
  .history-grid { grid-template-columns: 1fr; }
}
</style>
