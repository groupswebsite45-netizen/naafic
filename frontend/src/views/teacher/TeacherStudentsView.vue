<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { teacherPortalService } from '../../services/teacherPortalService';
import { attendanceService } from '../../services/attendanceService';
import { TeacherAssignedStudent } from '../../types/portal';
import { TeacherAssignment } from '../../types/school';
import { TeacherStudentAttendanceSummaryItem } from '../../types/attendance';

const students = ref<TeacherAssignedStudent[]>([]);
const myClasses = ref<TeacherAssignment[]>([]);
const selectedClassId = ref<number | undefined>(undefined);
const searchQuery = ref<string>('');
const isLoading = ref(true);
const errorMessage = ref('');

// Student History Modal
const isHistoryModalOpen = ref(false);
const isLoadingStudentHistory = ref(false);
const selectedStudentHistory = ref<TeacherStudentAttendanceSummaryItem | null>(null);

async function loadData() {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    const [cls, stds] = await Promise.all([
      teacherPortalService.getMyClasses(),
      teacherPortalService.getMyStudents(selectedClassId.value, searchQuery.value),
    ]);
    myClasses.value = cls;
    students.value = stds;
  } catch (err: any) {
    errorMessage.value = err.response?.data?.error?.message || err.response?.data?.detail || 'Failed to load assigned students.';
  } finally {
    isLoading.value = false;
  }
}

// Distinct assigned classes for filter
const uniqueClasses = computed(() => {
  const map = new Map<number, { id: number; name: string; code: string }>();
  for (const a of myClasses.value) {
    if (!map.has(a.class_id)) {
      map.set(a.class_id, { id: a.class_id, name: a.class_name || '', code: a.class_code || '' });
    }
  }
  return Array.from(map.values());
});

async function filterStudents() {
  isLoading.value = true;
  try {
    students.value = await teacherPortalService.getMyStudents(selectedClassId.value, searchQuery.value);
  } catch (err: any) {
    errorMessage.value = err.response?.data?.error?.message || 'Failed to filter students.';
  } finally {
    isLoading.value = false;
  }
}

watch(selectedClassId, () => {
  filterStudents();
});

let searchTimeout: any = null;
function onSearchInput() {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    filterStudents();
  }, 300);
}

async function openStudentHistory(student: TeacherAssignedStudent) {
  isHistoryModalOpen.value = true;
  isLoadingStudentHistory.value = true;
  try {
    const summary = await attendanceService.getSummary({ class_id: student.class_id });
    const match = summary.students.find((s) => s.student_id === student.student_id);
    if (match) {
      selectedStudentHistory.value = match;
    } else {
      selectedStudentHistory.value = {
        student_id: student.student_id,
        student_name: `${student.first_name} ${student.last_name}`,
        admission_number: student.admission_number,
        class_id: student.class_id,
        class_name: student.class_name,
        total_sessions: 0,
        present_count: 0,
        absent_count: 0,
        excused_count: 0,
        attendance_percentage: 100.0,
        absent_history: [],
      };
    }
  } catch (err) {
    console.error('Failed to load student attendance', err);
  } finally {
    isLoadingStudentHistory.value = false;
  }
}

onMounted(() => {
  loadData();
});
</script>

<template>
  <div class="portal-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="somroyal-tag">
          <svg class="crown-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M5 16L3 5l5.5 5L12 4l3.5 6L21 5l-2 11H5m14 3c0 .6-.4 1-1 1H6c-.6 0-1-.4-1-1v-1h14v1z"/>
          </svg>
          <span>STUDENT ROSTERS &bull; ENROLLED COHORTS</span>
        </div>
        <h1 class="page-title">Assigned Students</h1>
        <p class="page-subtitle">
          View enrolled students strictly in classes and grade streams assigned to your teaching faculty account.
        </p>
      </div>

      <div class="header-count-pill">
        <span class="count-lbl">Total Students:</span>
        <strong class="count-val">{{ students.length }}</strong>
      </div>
    </div>

    <!-- Filters Bar -->
    <div class="filters-card">
      <div class="filters-grid">
        <div class="form-group flex-2">
          <label class="form-label">Search Student</label>
          <div class="search-input-wrap">
            <svg class="search-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              class="search-input"
              placeholder="Search by first name, last name, or admission number..."
              @input="onSearchInput"
            />
            <button v-if="searchQuery" class="clear-search-btn" @click="searchQuery = ''; filterStudents()">&times;</button>
          </div>
        </div>

        <div class="form-group flex-1">
          <label class="form-label">Filter by Class</label>
          <select v-model="selectedClassId" class="form-select">
            <option :value="undefined">All My Classes ({{ uniqueClasses.length }})</option>
            <option v-for="c in uniqueClasses" :key="c.id" :value="c.id">
              {{ c.name }} ({{ c.code }})
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="errorMessage" class="error-banner">
      <div class="error-icon-box">
        <svg viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
      </div>
      <div class="error-details">
        <h4 class="error-title">Unable to Load Assigned Students</h4>
        <p class="error-desc">{{ errorMessage }}</p>
      </div>
      <button class="btn-retry" @click="loadData">Try Again</button>
    </div>

    <!-- Table & List Wrapper Card -->
    <div class="table-card">
      <div v-if="isLoading" class="state-container loading">
        <div class="spinner-ring" />
        <span class="loading-label">Retrieving student records from database...</span>
      </div>

      <div v-else-if="students.length === 0" class="state-container empty">
        <div class="empty-icon-circle">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        </div>
        <h3 class="state-title">No Students Found</h3>
        <p class="state-desc">No active student records matched your search query or class filter.</p>
      </div>

      <!-- Desktop Table -->
      <div v-else class="desktop-view">
        <div class="table-responsive-wrapper">
          <table class="somroyal-table">
            <thead>
              <tr>
                <th style="width: 50px;">#</th>
                <th>Student Name</th>
                <th>Admission #</th>
                <th>Assigned Class</th>
                <th>Gender</th>
                <th>Academic Year</th>
                <th style="text-align: right;">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(s, idx) in students" :key="s.student_id">
                <td class="text-muted">{{ idx + 1 }}</td>
                <td class="font-bold text-navy">
                  {{ s.first_name }} {{ s.middle_name || '' }} {{ s.last_name }}
                </td>
                <td>
                  <code class="adm-code">{{ s.admission_number }}</code>
                </td>
                <td>
                  <span class="class-badge-pill">{{ s.class_name }}</span>
                </td>
                <td>
                  <span class="gender-pill">{{ s.gender }}</span>
                </td>
                <td class="text-slate-600 font-semibold">{{ s.academic_year }}</td>
                <td style="text-align: right;">
                  <button class="btn-history-action" @click="openStudentHistory(s)">
                    <svg viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
                    </svg>
                    <span>Attendance Logs</span>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Mobile Student Cards -->
      <div v-if="students.length > 0" class="mobile-view">
        <div v-for="(s, idx) in students" :key="s.student_id" class="mobile-student-card">
          <div class="m-card-top">
            <span class="m-student-idx">#{{ idx + 1 }}</span>
            <span class="class-badge-pill">{{ s.class_name }}</span>
          </div>

          <h4 class="m-student-name">{{ s.first_name }} {{ s.middle_name || '' }} {{ s.last_name }}</h4>

          <div class="m-meta-grid">
            <div class="m-meta-item">
              <span class="m-meta-lbl">Admission:</span>
              <code class="adm-code">{{ s.admission_number }}</code>
            </div>
            <div class="m-meta-item">
              <span class="m-meta-lbl">Gender:</span>
              <span class="gender-pill">{{ s.gender }}</span>
            </div>
            <div class="m-meta-item full">
              <span class="m-meta-lbl">Academic Year:</span>
              <span class="m-meta-val">{{ s.academic_year }}</span>
            </div>
          </div>

          <button class="btn-mobile-history" @click="openStudentHistory(s)">
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
            </svg>
            <span>View Attendance History</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Student Attendance History Modal -->
    <div v-if="isHistoryModalOpen" class="modal-backdrop" @click="isHistoryModalOpen = false">
      <div class="modal-card" @click.stop>
        <div v-if="isLoadingStudentHistory" class="modal-loading-box">
          <div class="spinner-ring" />
          <span>Retrieving student attendance records...</span>
        </div>

        <div v-else-if="selectedStudentHistory" class="modal-content-wrap">
          <div class="modal-header">
            <div>
              <div class="modal-badge-line">
                <span class="class-badge-pill">{{ selectedStudentHistory.class_name }}</span>
                <code class="adm-code">{{ selectedStudentHistory.admission_number }}</code>
              </div>
              <h3 class="modal-title">{{ selectedStudentHistory.student_name }}</h3>
              <p class="modal-subtitle">Official Student Attendance Ledger &amp; Absence Timeline</p>
            </div>
            <button class="modal-close" aria-label="Close dialog" @click="isHistoryModalOpen = false">&times;</button>
          </div>

          <div class="modal-body">
            <!-- 4-Stat KPI Grid -->
            <div class="modal-stats-grid">
              <div class="stat-box">
                <span class="stat-title">TOTAL SESSIONS</span>
                <span class="stat-num text-navy">{{ selectedStudentHistory.total_sessions }}</span>
              </div>
              <div class="stat-box">
                <span class="stat-title">PRESENT COUNT</span>
                <span class="stat-num text-emerald">{{ selectedStudentHistory.present_count }}</span>
              </div>
              <div class="stat-box">
                <span class="stat-title">ABSENT COUNT</span>
                <span class="stat-num text-rose">{{ selectedStudentHistory.absent_count }}</span>
              </div>
              <div class="stat-box">
                <span class="stat-title">ATTENDANCE RATE</span>
                <span class="stat-num text-navy">{{ selectedStudentHistory.attendance_percentage }}%</span>
              </div>
            </div>

            <h4 class="sub-heading">Absence Timeline &amp; Justifications</h4>
            <div v-if="selectedStudentHistory.absent_history.length === 0" class="empty-inline-success">
              <svg viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
              <span>Perfect attendance record! Zero absences recorded for this student in this class stream.</span>
            </div>
            <div v-else class="table-responsive-wrapper">
              <table class="somroyal-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Subject</th>
                    <th>Status</th>
                    <th>Reason / Justification</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(h, i) in selectedStudentHistory.absent_history" :key="i">
                    <td class="font-bold text-navy">{{ h.date }}</td>
                    <td>{{ h.subject_name || 'Class Period' }}</td>
                    <td>
                      <span class="status-pill-absent">{{ h.status }}</span>
                    </td>
                    <td class="font-normal text-slate-600">{{ h.remarks || 'No reason specified' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-modal-close" @click="isHistoryModalOpen = false">Close Window</button>
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
  max-width: 1300px;
  margin: 0 auto;
  width: 100%;
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
  color: #38BDF8;
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

.header-count-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  padding: 0.5rem 1rem;
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.count-lbl {
  font-size: 0.78rem;
  color: #64748B;
  font-weight: 700;
}

.count-val {
  font-size: 1.15rem;
  color: #0A192F;
  font-weight: 900;
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
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-group.flex-2 { flex: 2; min-width: 280px; }
.form-group.flex-1 { flex: 1; min-width: 220px; }

.form-label {
  font-size: 0.72rem;
  font-weight: 700;
  color: #64748B;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.search-input-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #F8FAFC;
  border: 1px solid #CBD5E1;
  border-radius: 10px;
  padding: 0.5rem 0.85rem;
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
  font-size: 0.86rem;
  color: #0A192F;
  width: 100%;
  outline: none;
}

.clear-search-btn {
  background: none;
  border: none;
  color: #94A3B8;
  font-size: 1.1rem;
  cursor: pointer;
}

.form-select {
  background: #F8FAFC;
  border: 1px solid #CBD5E1;
  color: #0A192F;
  padding: 0.55rem 0.75rem;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 600;
  outline: none;
  cursor: pointer;
}

/* Table Card */
.table-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
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
  padding: 0.9rem 1rem;
  border-bottom: 1px solid #F1F5F9;
  color: #1E293B;
  vertical-align: middle;
}

.somroyal-table tbody tr:hover {
  background: #F8FAFC;
}

.text-navy { color: #0A192F !important; }
.text-emerald { color: #059669 !important; }
.text-rose { color: #DC2626 !important; }

.adm-code {
  font-family: monospace;
  font-weight: 700;
  color: #2563EB;
  background: #EFF6FF;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.class-badge-pill {
  font-size: 0.76rem;
  font-weight: 800;
  background: #F1F5F9;
  color: #0A192F;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
  border: 1px solid #E2E8F0;
}

.gender-pill {
  font-size: 0.74rem;
  font-weight: 600;
  color: #475569;
  background: #F8FAFC;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.btn-history-action {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: #FFFFFF;
  border: 1px solid #CBD5E1;
  color: #0A192F;
  padding: 0.4rem 0.75rem;
  border-radius: 8px;
  font-size: 0.76rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-history-action:hover {
  background: #0A192F;
  color: #FFFFFF;
  border-color: #0A192F;
}

.btn-history-action svg {
  width: 14px;
  height: 14px;
}

/* Mobile Cards View */
.mobile-view {
  display: none;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
}

.mobile-student-card {
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.m-card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.m-student-idx {
  font-size: 0.75rem;
  font-weight: 700;
  color: #94A3B8;
}

.m-student-name {
  font-size: 1.05rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
}

.m-meta-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
  background: #FFFFFF;
  padding: 0.75rem;
  border-radius: 8px;
  border: 1px solid #E2E8F0;
}

.m-meta-item {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.m-meta-item.full {
  grid-column: span 2;
}

.m-meta-lbl {
  font-size: 0.65rem;
  color: #94A3B8;
  font-weight: 700;
  text-transform: uppercase;
}

.m-meta-val {
  font-size: 0.84rem;
  font-weight: 600;
  color: #1E293B;
}

.btn-mobile-history {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  width: 100%;
  background: #0A192F;
  color: #FFFFFF;
  border: none;
  padding: 0.55rem;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
}

.btn-mobile-history svg {
  width: 15px;
  height: 15px;
}

/* Modal */
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
  display: flex;
  flex-direction: column;
}

.modal-loading-box {
  padding: 4rem 2rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  color: #64748B;
}

.modal-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #E2E8F0;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  background: #F8FAFC;
}

.modal-badge-line {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.35rem;
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
  line-height: 1;
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
  display: flex;
  align-items: center;
  gap: 0.65rem;
  background: #ECFDF5;
  border: 1px solid #A7F3D0;
  color: #065F46;
  padding: 1rem 1.25rem;
  border-radius: 10px;
  font-size: 0.86rem;
  font-weight: 600;
}

.empty-inline-success svg {
  width: 20px;
  height: 20px;
  color: #10B981;
  flex-shrink: 0;
}

.status-pill-absent {
  font-size: 0.72rem;
  font-weight: 800;
  background: #FEF2F2;
  color: #DC2626;
  border: 1px solid #FECACA;
  padding: 0.15rem 0.5rem;
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

.btn-modal-close:hover { background: #1E3A8A; }

/* Common States */
.state-container {
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
  border-top-color: #1E3A8A;
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

.error-icon-box svg { width: 20px; height: 20px; }
.error-details { flex: 1; }
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
@media (max-width: 768px) {
  .desktop-view { display: none; }
  .mobile-view { display: flex; }
  .filters-grid { flex-direction: column; }
  .modal-stats-grid { grid-template-columns: repeat(2, 1fr); }
  .modal-header, .modal-body, .modal-footer { padding: 1rem; }
}

@media (max-width: 480px) {
  .modal-stats-grid { grid-template-columns: 1fr; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-count-pill { justify-content: space-between; }
}
</style>
