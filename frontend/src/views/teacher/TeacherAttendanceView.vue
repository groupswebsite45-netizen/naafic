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
        <svg v-if="notification.type === 'success'" class="toast-icon" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        <svg v-else class="toast-icon" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
        <span>{{ notification.message }}</span>
        <button class="toast-close" aria-label="Dismiss alert" @click="notification = null">&times;</button>
      </div>
    </div>

    <!-- Header & Navigation -->
    <div class="page-header">
      <div class="header-main">
        <div class="somroyal-tag">
          <svg class="crown-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M5 16L3 5l5.5 5L12 4l3.5 6L21 5l-2 11H5m14 3c0 .6-.4 1-1 1H6c-.6 0-1-.4-1-1v-1h14v1z"/>
          </svg>
          <span>DAILY ATTENDANCE &bull; PERIOD ROLL CALL</span>
        </div>
        <h1 class="page-title">Class Attendance</h1>
        <p class="page-subtitle">
          Record daily student attendance, specify absence reasons, inspect session logs, and monitor attendance analytics.
        </p>
      </div>

      <!-- Segmented Navigation Tabs -->
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
          <span>Session Logs</span>
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
    <div class="filters-card">
      <div class="filters-grid">
        <div class="form-group">
          <label class="form-label">Academic Year</label>
          <select v-model="selectedYear" class="form-select" :disabled="isLoadingOptions">
            <option v-for="yr in options?.academic_years" :key="yr" :value="yr">{{ yr }}</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Assigned Class</label>
          <select v-model="selectedClassId" class="form-select" :disabled="isLoadingOptions || availableClasses.length === 0">
            <option v-if="availableClasses.length === 0" :value="null">No assigned classes</option>
            <option v-for="c in availableClasses" :key="c.id" :value="c.id">
              {{ c.name }} ({{ c.code }})
            </option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Assigned Subject</label>
          <select v-model="selectedSubjectId" class="form-select" :disabled="isLoadingOptions || availableSubjects.length === 0">
            <option v-if="availableSubjects.length === 0" :value="null">No assigned subjects</option>
            <option v-for="s in availableSubjects" :key="s.id" :value="s.id">
              {{ s.name }} ({{ s.code }})
            </option>
          </select>
        </div>

        <div v-if="activeTab === 'take'" class="form-group">
          <label class="form-label">Attendance Date</label>
          <div class="date-input-row">
            <input
              v-model="selectedDate"
              type="date"
              class="form-input"
              :max="getTodayDateString()"
              :disabled="isLoadingOptions"
            />
            <button
              class="btn-today-shortcut"
              :class="{ active: selectedDate === getTodayDateString() }"
              @click="selectedDate = getTodayDateString()"
            >
              Today
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 1: TAKE ATTENDANCE -->
    <div v-if="activeTab === 'take'" class="tab-content">
      <!-- Loading State -->
      <div v-if="isLoadingRoster" class="state-card loading">
        <div class="spinner-ring" />
        <span class="loading-label">Loading student roster from database...</span>
      </div>

      <!-- Future Date Alert -->
      <div v-else-if="isFutureDate" class="alert-box error">
        <strong>Future Date Blocked:</strong> Attendance cannot be recorded for future dates. Please select today or a previous date.
      </div>

      <!-- Empty State -->
      <div v-else-if="!rosterData || rosterData.students.length === 0" class="state-card empty">
        <div class="empty-icon-circle">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
        </div>
        <h3 class="state-title">No Enrolled Students Found</h3>
        <p class="state-desc">No active students are currently enrolled in this class.</p>
      </div>

      <!-- Roster Active View -->
      <div v-else class="roster-view">
        <!-- Live Summary Banner -->
        <div class="summary-banner">
          <div class="summary-left">
            <div class="session-status-row">
              <span class="session-badge" :class="rosterData.is_recorded ? 'recorded' : 'new'">
                <span class="dot" :class="rosterData.is_recorded ? 'green' : 'amber'" />
                {{ rosterData.is_recorded ? 'Saved Session' : 'New Session (Unsaved)' }}
              </span>
              <strong class="session-class-name">{{ rosterData.class_name }}</strong>
            </div>
            <div class="session-sub-details">
              <span>Subject: <strong>{{ rosterData.subject_name }}</strong></span>
              <span class="bullet">&bull;</span>
              <span>Date: <strong>{{ rosterData.date }}</strong></span>
            </div>
          </div>

          <!-- Stats Pills -->
          <div class="summary-pills">
            <div class="stat-pill total">
              <span class="pill-label">TOTAL</span>
              <span class="pill-val">{{ rosterData.total_students }}</span>
            </div>
            <div class="stat-pill present">
              <span class="pill-label">PRESENT</span>
              <span class="pill-val text-emerald">{{ presentCount }}</span>
            </div>
            <div class="stat-pill absent">
              <span class="pill-label">ABSENT</span>
              <span class="pill-val text-rose">{{ absentCount }}</span>
            </div>
          </div>

          <!-- Actions -->
          <div class="banner-actions">
            <button class="btn-all-present" @click="markAllPresent">
              <svg viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
              <span>Mark All Present</span>
            </button>
            <button class="btn-save-attendance" :disabled="isSaving" @click="isConfirmSaveModalOpen = true">
              <span>Save Attendance</span>
              <svg viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Desktop Roster Table -->
        <div class="desktop-roster">
          <div class="table-responsive-wrapper">
            <table class="somroyal-table">
              <thead>
                <tr>
                  <th style="width: 50px;">#</th>
                  <th>Student Name</th>
                  <th>Admission #</th>
                  <th style="width: 150px; text-align: center;">Status (Present / Absent)</th>
                  <th>Absence Reason / Remarks</th>
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
                    <span class="student-name text-navy">{{ std.student_name }}</span>
                    <span v-if="std.gender" class="gender-pill">{{ std.gender }}</span>
                  </td>
                  <td><code class="adm-code">{{ std.admission_number }}</code></td>
                  <td style="text-align: center;">
                    <!-- ON / OFF Toggle Switch -->
                    <button
                      type="button"
                      class="toggle-switch"
                      :class="{
                        'is-on': std.status === 'PRESENT' || std.status === 'LATE',
                        'is-off': std.status === 'ABSENT' || std.status === 'EXCUSED'
                      }"
                      :aria-label="`Toggle attendance for ${std.student_name}`"
                      @click="toggleStudentStatus(std)"
                    >
                      <span class="switch-handle" />
                      <span class="switch-text">{{ (std.status === 'PRESENT' || std.status === 'LATE') ? 'PRESENT' : 'ABSENT' }}</span>
                    </button>
                  </td>
                  <td>
                    <div v-if="std.status === 'ABSENT' || std.status === 'EXCUSED'" class="reason-wrap">
                      <input
                        v-model="std.remarks"
                        type="text"
                        class="reason-input"
                        placeholder="e.g. Sick, Family emergency, Unexcused"
                      />
                    </div>
                    <span v-else class="text-present-tag">
                      <svg viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                      </svg>
                      Present in session
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Mobile Roster Cards (<= 768px) -->
        <div class="mobile-roster">
          <div class="mobile-bulk-actions">
            <button class="btn-all-present block" @click="markAllPresent">
              Mark All Present
            </button>
          </div>

          <div
            v-for="(std, idx) in rosterData.students"
            :key="std.student_id"
            class="student-card-mobile"
            :class="{ 'card-absent': std.status === 'ABSENT' || std.status === 'EXCUSED' }"
          >
            <div class="m-card-header">
              <div class="m-student-meta">
                <span class="m-index">#{{ idx + 1 }}</span>
                <div>
                  <h4 class="m-student-title">{{ std.student_name }}</h4>
                  <code class="adm-code">{{ std.admission_number }}</code>
                </div>
              </div>

              <!-- Switch -->
              <button
                type="button"
                class="toggle-switch"
                :class="{
                  'is-on': std.status === 'PRESENT' || std.status === 'LATE',
                  'is-off': std.status === 'ABSENT' || std.status === 'EXCUSED'
                }"
                :aria-label="`Toggle attendance for ${std.student_name}`"
                @click="toggleStudentStatus(std)"
              >
                <span class="switch-handle" />
                <span class="switch-text">{{ (std.status === 'PRESENT' || std.status === 'LATE') ? 'PRESENT' : 'ABSENT' }}</span>
              </button>
            </div>

            <div v-if="std.status === 'ABSENT' || std.status === 'EXCUSED'" class="m-card-reason">
              <label class="reason-label">Absence reason / notes:</label>
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
          <button class="btn-save-attendance block" :disabled="isSaving" @click="isConfirmSaveModalOpen = true">
            Save Attendance
          </button>
        </div>
      </div>
    </div>

    <!-- TAB 2: SESSION HISTORY -->
    <div v-else-if="activeTab === 'history'" class="tab-content">
      <div v-if="isLoadingHistory" class="state-card loading">
        <div class="spinner-ring" />
        <span class="loading-label">Loading attendance session logs...</span>
      </div>

      <div v-else-if="historySessions.length === 0" class="state-card empty">
        <h3 class="state-title">No Previous Sessions Recorded</h3>
        <p class="state-desc">No attendance logs exist yet for this class and academic year.</p>
      </div>

      <div v-else class="history-grid">
        <div v-for="s in historySessions" :key="s.session_key" class="session-card">
          <div class="session-top">
            <span class="session-date">📅 {{ s.date }}</span>
            <span class="rate-badge" :class="s.attendance_percentage >= 80 ? 'green' : 'amber'">
              {{ s.attendance_percentage }}% Present
            </span>
          </div>

          <div class="session-body">
            <h4 class="session-class">{{ s.class_name }}</h4>
            <span class="session-sub">{{ s.subject_name }}</span>

            <div class="session-stats">
              <span>Total: <strong>{{ s.total_students }}</strong></span>
              <span class="text-emerald">Present: <strong>{{ s.present_count }}</strong></span>
              <span class="text-rose">Absent: <strong>{{ s.absent_count }}</strong></span>
            </div>
          </div>

          <div class="session-footer">
            <button class="btn-edit-session" @click="loadSessionFromHistory(s)">
              <span>View / Edit Attendance</span>
              <svg viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 3: STUDENT ABSENCE ANALYTICS -->
    <div v-else-if="activeTab === 'summary'" class="tab-content">
      <div v-if="isLoadingSummary" class="state-card loading">
        <div class="spinner-ring" />
        <span class="loading-label">Calculating student attendance rates...</span>
      </div>

      <div v-else-if="!summaryData || summaryData.students.length === 0" class="state-card empty">
        <h3 class="state-title">No Summary Records Available</h3>
        <p class="state-desc">No attendance logs found for this class.</p>
      </div>

      <div v-else class="summary-section">
        <!-- Search bar -->
        <div class="search-bar-wrap">
          <svg class="search-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            v-model="summarySearchQuery"
            type="text"
            class="search-input"
            placeholder="Search student by name or admission number..."
          />
        </div>

        <!-- Table View -->
        <div class="table-card">
          <div class="table-responsive-wrapper">
            <table class="somroyal-table">
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
                  <td class="font-bold text-navy">{{ std.student_name }}</td>
                  <td><code class="adm-code">{{ std.admission_number }}</code></td>
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
                    <button class="btn-summary-detail" @click="openStudentHistoryModal(std)">
                      <span>View History</span>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- CONFIRM SAVE MODAL -->
    <div v-if="isConfirmSaveModalOpen" class="modal-backdrop" @click="isConfirmSaveModalOpen = false">
      <div class="modal-card small" @click.stop>
        <div class="confirm-modal-header">
          <div class="confirm-icon-box">
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
          </div>
          <h3 class="confirm-title">Confirm Attendance Records</h3>
          <p class="confirm-subtitle">Verify your class attendance roll call before committing to database.</p>
        </div>

        <div class="confirm-modal-body">
          <div class="confirm-counts-box">
            <div class="confirm-count-item">
              <span class="lbl">Present</span>
              <strong class="val text-emerald">{{ presentCount }}</strong>
            </div>
            <div class="confirm-count-item">
              <span class="lbl">Absent</span>
              <strong class="val text-rose">{{ absentCount }}</strong>
            </div>
            <div class="confirm-count-item">
              <span class="lbl">Total Enrolled</span>
              <strong class="val">{{ rosterData?.total_students }}</strong>
            </div>
          </div>
          <p class="confirm-note">
            Attendance will be recorded for <strong>{{ rosterData?.class_name }}</strong> on <strong>{{ selectedDate }}</strong>.
          </p>
        </div>

        <div class="confirm-modal-footer">
          <button class="btn-cancel" @click="isConfirmSaveModalOpen = false">Cancel</button>
          <button class="btn-confirm-save" :disabled="isSaving" @click="handleSaveAttendance">
            {{ isSaving ? 'Saving...' : 'Confirm & Save' }}
          </button>
        </div>
      </div>
    </div>

    <!-- STUDENT ABSENCE HISTORY MODAL -->
    <div v-if="isStudentModalOpen" class="modal-backdrop" @click="isStudentModalOpen = false">
      <div class="modal-card" @click.stop>
        <div v-if="selectedStudentDetail" class="modal-content-wrap">
          <div class="modal-header">
            <div>
              <div class="modal-badge-line">
                <span class="class-badge-pill">{{ selectedStudentDetail.class_name }}</span>
                <code class="adm-code">{{ selectedStudentDetail.admission_number }}</code>
              </div>
              <h3 class="modal-title">{{ selectedStudentDetail.student_name }}</h3>
              <p class="modal-subtitle">Attendance rate: {{ selectedStudentDetail.attendance_percentage }}%</p>
            </div>
            <button class="modal-close" @click="isStudentModalOpen = false">&times;</button>
          </div>

          <div class="modal-body">
            <div class="modal-stats-grid">
              <div class="stat-box">
                <span class="stat-title">Total Sessions</span>
                <span class="stat-num text-navy">{{ selectedStudentDetail.total_sessions }}</span>
              </div>
              <div class="stat-box">
                <span class="stat-title">Present</span>
                <span class="stat-num text-emerald">{{ selectedStudentDetail.present_count }}</span>
              </div>
              <div class="stat-box">
                <span class="stat-title">Absent</span>
                <span class="stat-num text-rose">{{ selectedStudentDetail.absent_count }}</span>
              </div>
              <div class="stat-box">
                <span class="stat-title">Attendance %</span>
                <span class="stat-num text-navy">{{ selectedStudentDetail.attendance_percentage }}%</span>
              </div>
            </div>

            <h4 class="sub-heading">Absence Timeline</h4>
            <div v-if="selectedStudentDetail.absent_history.length === 0" class="empty-inline-success">
              No absences recorded. Perfect attendance!
            </div>
            <div v-else class="table-responsive-wrapper">
              <table class="somroyal-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Subject</th>
                    <th>Status</th>
                    <th>Reason / Notes</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(h, i) in selectedStudentDetail.absent_history" :key="i">
                    <td class="font-bold text-navy">{{ h.date }}</td>
                    <td>{{ h.subject_name || 'Class Session' }}</td>
                    <td><span class="status-pill-absent">{{ h.status }}</span></td>
                    <td class="text-slate-600">{{ h.remarks || 'None specified' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-modal-close" @click="isStudentModalOpen = false">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.attendance-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 1300px;
  margin: 0 auto;
  width: 100%;
}

/* Toast */
.toast-banner {
  padding: 0.85rem 1.25rem;
  border-radius: 12px;
  font-size: 0.86rem;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.toast-banner.success {
  background: #ECFDF5;
  border: 1px solid #A7F3D0;
  color: #065F46;
}

.toast-banner.error {
  background: #FEF2F2;
  border: 1px solid #FCA5A5;
  color: #991B1B;
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.toast-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.toast-close {
  margin-left: auto;
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: inherit;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1.25rem;
  flex-wrap: wrap;
}

.somroyal-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #10B981;
  text-transform: uppercase;
  margin-bottom: 0.35rem;
}

.crown-icon {
  width: 14px;
  height: 14px;
  color: #F59E0B;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 0.88rem;
  color: #64748B;
  margin-top: 0.25rem;
  line-height: 1.5;
  max-width: 780px;
}

/* Tabs Nav */
.tab-nav {
  display: flex;
  gap: 0.4rem;
  background: #E2E8F0;
  padding: 0.25rem;
  border-radius: 12px;
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.55rem 1rem;
  font-size: 0.84rem;
  font-weight: 700;
  color: #64748B;
  background: transparent;
  border: none;
  border-radius: 9px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn:hover { color: #0A192F; }

.tab-btn.active {
  background: #FFFFFF;
  color: #0A192F;
  box-shadow: 0 2px 6px rgba(10, 25, 47, 0.08);
}

.tab-icon {
  width: 16px;
  height: 16px;
}

/* Filters */
.filters-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 1.25rem 1.5rem;
  box-shadow: 0 2px 6px rgba(10, 25, 47, 0.03);
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-label {
  font-size: 0.72rem;
  font-weight: 700;
  color: #64748B;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.form-select, .form-input {
  background: #F8FAFC;
  border: 1px solid #CBD5E1;
  color: #0A192F;
  padding: 0.55rem 0.75rem;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 600;
  outline: none;
}

.date-input-row {
  display: flex;
  gap: 0.5rem;
}

.date-input-row .form-input { flex: 1; }

.btn-today-shortcut {
  background: #EFF6FF;
  border: 1px solid #BFDBFE;
  color: #1E40AF;
  padding: 0.5rem 0.75rem;
  border-radius: 10px;
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
}

.btn-today-shortcut.active {
  background: #2563EB;
  color: #FFFFFF;
}

/* Roster View */
.roster-view {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.summary-banner {
  background: linear-gradient(135deg, #0A192F 0%, #0F2A4A 60%, #081528 100%);
  border-radius: 16px;
  padding: 1.5rem 2rem;
  color: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1.25rem;
  box-shadow: 0 10px 25px -5px rgba(10, 25, 47, 0.25);
}

.summary-left {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.session-status-row {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.session-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.7rem;
  font-weight: 800;
  padding: 0.2rem 0.55rem;
  border-radius: 20px;
}

.session-badge.recorded {
  background: rgba(16, 185, 129, 0.2);
  color: #10B981;
  border: 1px solid rgba(16, 185, 129, 0.4);
}

.session-badge.new {
  background: rgba(245, 158, 11, 0.2);
  color: #F59E0B;
  border: 1px solid rgba(245, 158, 11, 0.4);
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.dot.green { background: #10B981; }
.dot.amber { background: #F59E0B; }

.session-class-name {
  font-size: 1.25rem;
  color: #FFFFFF;
}

.session-sub-details {
  font-size: 0.82rem;
  color: #94A3B8;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.bullet { color: #64748B; }

.summary-pills {
  display: flex;
  gap: 0.75rem;
}

.stat-pill {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  padding: 0.5rem 0.95rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.1rem;
}

.pill-label {
  font-size: 0.62rem;
  font-weight: 800;
  color: #94A3B8;
}

.pill-val {
  font-size: 1.25rem;
  font-weight: 900;
  color: #FFFFFF;
}

.text-emerald { color: #10B981 !important; }
.text-rose { color: #EF4444 !important; }

.banner-actions {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.btn-all-present {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.25);
  color: #FFFFFF;
  padding: 0.6rem 1rem;
  border-radius: 10px;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-all-present:hover {
  background: rgba(255, 255, 255, 0.2);
}

.btn-all-present svg { width: 15px; height: 15px; }

.btn-save-attendance {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: #1E3A8A;
  border: none;
  color: #FFFFFF;
  padding: 0.6rem 1.2rem;
  border-radius: 10px;
  font-size: 0.84rem;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(30, 58, 138, 0.3);
  transition: all 0.2s;
}

.btn-save-attendance:hover:not(:disabled) {
  background: #1E40AF;
}

.btn-save-attendance svg { width: 15px; height: 15px; }

/* Table */
.desktop-roster {
  background: #FFFFFF;
  border-radius: 16px;
  border: 1px solid #E2E8F0;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(10, 25, 47, 0.03);
}

.table-responsive-wrapper {
  overflow-x: auto;
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
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #F1F5F9;
  color: #1E293B;
  vertical-align: middle;
}

.row-absent {
  background: #FFF5F5;
}

.text-navy { color: #0A192F !important; }

.student-name {
  margin-right: 0.5rem;
}

.adm-code {
  font-family: monospace;
  font-weight: 700;
  color: #2563EB;
  background: #EFF6FF;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.gender-pill {
  font-size: 0.7rem;
  color: #64748B;
  background: #F1F5F9;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}

/* ON / OFF Switch Toggle */
.toggle-switch {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.65rem;
  border-radius: 20px;
  cursor: pointer;
  border: none;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.05em;
  transition: all 0.2s ease;
}

.toggle-switch.is-on {
  background: #ECFDF5;
  color: #065F46;
  border: 1px solid #A7F3D0;
}

.toggle-switch.is-off {
  background: #FEF2F2;
  color: #991B1B;
  border: 1px solid #FECACA;
}

.switch-handle {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.is-on .switch-handle { background: #10B981; }
.is-off .switch-handle { background: #EF4444; }

.reason-input {
  width: 100%;
  background: #FFFFFF;
  border: 1px solid #FCA5A5;
  padding: 0.4rem 0.65rem;
  border-radius: 6px;
  font-size: 0.8rem;
  color: #991B1B;
  outline: none;
}

.text-present-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.78rem;
  color: #059669;
  font-weight: 600;
}

.text-present-tag svg {
  width: 14px;
  height: 14px;
}

/* Mobile Roster */
.mobile-roster {
  display: none;
  flex-direction: column;
  gap: 1rem;
}

.student-card-mobile {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.student-card-mobile.card-absent {
  background: #FFF5F5;
  border-color: #FECACA;
}

.m-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
}

.m-student-meta {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.m-index {
  font-size: 0.75rem;
  color: #94A3B8;
  font-weight: 700;
  padding-top: 0.15rem;
}

.m-student-title {
  font-size: 1rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0 0 0.25rem 0;
}

.m-card-reason {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding-top: 0.5rem;
  border-top: 1px dashed #E2E8F0;
}

.reason-label {
  font-size: 0.7rem;
  font-weight: 700;
  color: #991B1B;
}

.mobile-save-bar {
  display: none;
  position: sticky;
  bottom: 1rem;
  background: #0A192F;
  color: #FFFFFF;
  border-radius: 14px;
  padding: 0.85rem 1.25rem;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  z-index: 20;
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
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.15rem;
}

.session-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 14px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  box-shadow: 0 2px 6px rgba(10, 25, 47, 0.03);
}

.session-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.session-date {
  font-size: 0.84rem;
  font-weight: 700;
  color: #0A192F;
}

.rate-badge {
  font-size: 0.72rem;
  font-weight: 800;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
}

.rate-badge.green {
  background: #ECFDF5;
  color: #065F46;
}

.rate-badge.amber {
  background: #FEF3C7;
  color: #92400E;
}

.session-class {
  font-size: 1.05rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
}

.session-sub {
  font-size: 0.78rem;
  color: #64748B;
  font-weight: 600;
}

.session-stats {
  display: flex;
  gap: 0.75rem;
  font-size: 0.8rem;
  background: #F8FAFC;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  margin-top: 0.5rem;
}

.btn-edit-session {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  width: 100%;
  background: #F8FAFC;
  border: 1px solid #CBD5E1;
  color: #0A192F;
  padding: 0.5rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-edit-session:hover {
  background: #0A192F;
  color: #FFFFFF;
}

.btn-edit-session svg { width: 14px; height: 14px; }

/* Summary / Absence Analytics */
.summary-section {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.search-bar-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 0.65rem 1rem;
}

.search-icon {
  width: 18px;
  height: 18px;
  color: #94A3B8;
  flex-shrink: 0;
}

.search-input {
  background: transparent;
  border: none;
  font-size: 0.88rem;
  color: #0A192F;
  width: 100%;
  outline: none;
}

.table-card {
  background: #FFFFFF;
  border-radius: 16px;
  border: 1px solid #E2E8F0;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(10, 25, 47, 0.03);
}

.rate-pill {
  font-size: 0.76rem;
  font-weight: 800;
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
}

.rate-pill.high {
  background: #ECFDF5;
  color: #065F46;
}

.rate-pill.medium {
  background: #FEF3C7;
  color: #92400E;
}

.rate-pill.low {
  background: #FEF2F2;
  color: #991B1B;
}

.btn-summary-detail {
  background: #F1F5F9;
  border: 1px solid #CBD5E1;
  color: #0A192F;
  padding: 0.35rem 0.65rem;
  border-radius: 6px;
  font-size: 0.76rem;
  font-weight: 700;
  cursor: pointer;
}

.btn-summary-detail:hover {
  background: #0A192F;
  color: #FFFFFF;
}

/* Modals */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(10, 25, 47, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 60;
  padding: 1rem;
}

.modal-card {
  background: #FFFFFF;
  border-radius: 20px;
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.modal-card.small {
  max-width: 480px;
}

.confirm-modal-header {
  padding: 1.5rem 1.5rem 0.75rem;
  text-align: center;
}

.confirm-icon-box {
  width: 48px;
  height: 48px;
  background: #ECFDF5;
  color: #10B981;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 0.75rem;
}

.confirm-icon-box svg { width: 24px; height: 24px; }

.confirm-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
}

.confirm-subtitle {
  font-size: 0.84rem;
  color: #64748B;
  margin-top: 0.25rem;
}

.confirm-modal-body {
  padding: 1rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.confirm-counts-box {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
  background: #F8FAFC;
  padding: 0.85rem;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
  text-align: center;
}

.confirm-count-item {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.confirm-count-item .lbl {
  font-size: 0.68rem;
  font-weight: 700;
  color: #64748B;
  text-transform: uppercase;
}

.confirm-count-item .val {
  font-size: 1.35rem;
  font-weight: 900;
}

.confirm-note {
  font-size: 0.84rem;
  color: #475569;
  text-align: center;
  margin: 0;
}

.confirm-modal-footer {
  padding: 1rem 1.5rem;
  background: #F8FAFC;
  border-top: 1px solid #E2E8F0;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-cancel {
  background: #FFFFFF;
  border: 1px solid #CBD5E1;
  color: #475569;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.84rem;
  font-weight: 700;
  cursor: pointer;
}

.btn-confirm-save {
  background: #1E3A8A;
  border: none;
  color: #FFFFFF;
  padding: 0.5rem 1.25rem;
  border-radius: 8px;
  font-size: 0.84rem;
  font-weight: 800;
  cursor: pointer;
}

.btn-confirm-save:hover { background: #1E40AF; }

/* Student Detail Modal */
.modal-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #E2E8F0;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: #F8FAFC;
}

.modal-badge-line {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.35rem;
}

.class-badge-pill {
  font-size: 0.76rem;
  font-weight: 800;
  background: #F1F5F9;
  color: #0A192F;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
}

.modal-title {
  font-size: 1.35rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
}

.modal-subtitle {
  font-size: 0.82rem;
  color: #64748B;
  margin-top: 0.2rem;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.75rem;
  color: #94A3B8;
  cursor: pointer;
}

.modal-close:hover { color: #0A192F; }

.modal-body {
  padding: 1.5rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.modal-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.stat-box {
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 0.85rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.stat-title {
  font-size: 0.65rem;
  font-weight: 800;
  color: #64748B;
  text-transform: uppercase;
}

.stat-num {
  font-size: 1.45rem;
  font-weight: 900;
}

.sub-heading {
  font-size: 1.05rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0.5rem 0 0 0;
}

.empty-inline-success {
  background: #ECFDF5;
  border: 1px solid #A7F3D0;
  color: #065F46;
  padding: 0.85rem 1rem;
  border-radius: 8px;
  font-size: 0.84rem;
  font-weight: 600;
}

.status-pill-absent {
  font-size: 0.72rem;
  font-weight: 800;
  background: #FEF2F2;
  color: #DC2626;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.modal-footer {
  padding: 1rem 2rem;
  background: #F8FAFC;
  border-top: 1px solid #E2E8F0;
  display: flex;
  justify-content: flex-end;
}

.btn-modal-close {
  background: #0A192F;
  color: #FFFFFF;
  border: none;
  padding: 0.5rem 1.25rem;
  border-radius: 8px;
  font-size: 0.84rem;
  font-weight: 700;
  cursor: pointer;
}

/* States */
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

@keyframes spin { to { transform: rotate(360deg); } }

.loading-label {
  font-size: 0.88rem;
  color: #64748B;
  font-weight: 600;
}

.empty-icon-circle {
  width: 56px;
  height: 56px;
  background: #F1F5F9;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94A3B8;
}

.empty-icon-circle svg { width: 28px; height: 28px; }

.state-title {
  font-size: 1.15rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
}

.state-desc {
  font-size: 0.86rem;
  color: #64748B;
  max-width: 500px;
  line-height: 1.5;
  margin: 0;
}

.alert-box.error {
  background: #FEF2F2;
  border: 1px solid #FCA5A5;
  color: #991B1B;
  padding: 0.85rem 1.25rem;
  border-radius: 12px;
  font-size: 0.84rem;
}

/* Responsive Rules */
@media (max-width: 1024px) {
  .filters-grid { grid-template-columns: repeat(2, 1fr); }
  .modal-stats-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .desktop-roster { display: none; }
  .mobile-roster { display: flex; }
  .mobile-save-bar { display: block; }
  .summary-banner {
    flex-direction: column;
    align-items: flex-start;
    padding: 1.25rem;
  }
  .summary-pills { width: 100%; justify-content: space-between; }
  .banner-actions { width: 100%; }
  .btn-all-present, .btn-save-attendance { flex: 1; justify-content: center; }
  .filters-grid { grid-template-columns: 1fr; }
}

@media (max-width: 480px) {
  .page-header { flex-direction: column; align-items: stretch; }
  .tab-nav { width: 100%; }
  .tab-btn { flex: 1; justify-content: center; padding: 0.5rem; font-size: 0.78rem; }
  .modal-stats-grid { grid-template-columns: 1fr; }
}
</style>
