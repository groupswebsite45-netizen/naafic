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
    <div class="page-header">
      <div>
        <h1 class="page-title">Students in Assigned Classes</h1>
        <p class="page-subtitle">
          View enrolled students strictly in classes and grade streams assigned to your teaching faculty account.
        </p>
      </div>
      <div class="header-count-badge">
        Total Students: <strong>{{ students.length }}</strong>
      </div>
    </div>

    <!-- Filters Bar -->
    <div class="filters-card card">
      <div class="filters-grid">
        <div class="form-group flex-2">
          <label class="form-label">Search Student</label>
          <input
            v-model="searchQuery"
            type="text"
            class="form-input"
            placeholder="Search by first name, last name, or admission #..."
            @input="onSearchInput"
          />
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

    <div v-if="errorMessage" class="alert-box error">
      {{ errorMessage }}
    </div>

    <div class="table-card card">
      <div v-if="isLoading" class="loading-box">
        <div class="spinner" />
        <span>Loading assigned student rosters from PostgreSQL...</span>
      </div>

      <div v-else-if="students.length === 0" class="empty-box">
        <svg class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
        <p class="empty-title">No Students Found</p>
        <p class="empty-desc">No active students match your search or class filter.</p>
      </div>

      <!-- Desktop Table -->
      <div v-else class="desktop-view">
        <div class="table-responsive">
          <table class="portal-table">
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
                <td class="font-bold">
                  {{ s.first_name }} {{ s.middle_name || '' }} {{ s.last_name }}
                </td>
                <td><code>{{ s.admission_number }}</code></td>
                <td><span class="class-badge">{{ s.class_name }}</span></td>
                <td>{{ s.gender }}</td>
                <td>{{ s.academic_year }}</td>
                <td style="text-align: right;">
                  <button class="btn btn-xs btn-outline" @click="openStudentHistory(s)">
                    Attendance History
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
          <div class="mobile-card-top">
            <span class="mobile-num">#{{ idx + 1 }}</span>
            <span class="class-badge">{{ s.class_name }}</span>
          </div>
          <h4 class="mobile-name">{{ s.first_name }} {{ s.middle_name || '' }} {{ s.last_name }}</h4>
          <div class="mobile-meta-grid">
            <div class="meta-row">
              <span class="meta-label">Admission:</span>
              <code>{{ s.admission_number }}</code>
            </div>
            <div class="meta-row">
              <span class="meta-label">Gender:</span>
              <span>{{ s.gender }}</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">Academic Year:</span>
              <span>{{ s.academic_year }}</span>
            </div>
          </div>
          <div class="mobile-card-actions">
            <button class="btn btn-outline btn-touch btn-block" @click="openStudentHistory(s)">
              Attendance History
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Student Attendance History Modal -->
    <div v-if="isHistoryModalOpen" class="modal-backdrop" @click="isHistoryModalOpen = false">
      <div class="modal-card card large" @click.stop>
        <div v-if="isLoadingStudentHistory" class="loading-box">
          <div class="spinner" />
          <span>Retrieving student attendance record...</span>
        </div>
        <div v-else-if="selectedStudentHistory" class="modal-content-wrap">
          <div class="modal-header">
            <div>
              <h3 class="modal-title">{{ selectedStudentHistory.student_name }}</h3>
              <span class="adm-code">{{ selectedStudentHistory.admission_number }} • {{ selectedStudentHistory.class_name }}</span>
            </div>
            <button class="modal-close" aria-label="Close dialog" @click="isHistoryModalOpen = false">&times;</button>
          </div>

          <div class="modal-body">
            <div class="modal-stats-grid">
              <div class="stat-box">
                <span class="stat-title">Total Sessions</span>
                <span class="stat-num">{{ selectedStudentHistory.total_sessions }}</span>
              </div>
              <div class="stat-box">
                <span class="stat-title">Present Count</span>
                <span class="stat-num text-emerald">{{ selectedStudentHistory.present_count }}</span>
              </div>
              <div class="stat-box">
                <span class="stat-title">Absent Count</span>
                <span class="stat-num text-rose">{{ selectedStudentHistory.absent_count }}</span>
              </div>
              <div class="stat-box">
                <span class="stat-title">Attendance Rate</span>
                <span class="stat-num text-primary">{{ selectedStudentHistory.attendance_percentage }}%</span>
              </div>
            </div>

            <h4 class="sub-heading">Absence Timeline & Justifications</h4>
            <div v-if="selectedStudentHistory.absent_history.length === 0" class="empty-inline">
              Perfect attendance record! No absences recorded in this class stream.
            </div>
            <div v-else class="table-responsive modal-table-wrap">
              <table class="portal-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Subject</th>
                    <th>Status</th>
                    <th>Reason / Remarks</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(h, i) in selectedStudentHistory.absent_history" :key="i">
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
            <button class="btn btn-primary btn-touch btn-block-mobile" @click="isHistoryModalOpen = false">Close</button>
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
  box-sizing: border-box;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}
.page-title { font-size: 1.5rem; font-weight: 800; color: var(--text-primary, #0f172a); margin: 0; word-break: break-word; }
.page-subtitle { font-size: 0.85rem; color: var(--text-muted, #64748b); margin-top: 0.2rem; }
.header-count-badge {
  background: #f1f5f9;
  color: #334155;
  padding: 0.4rem 0.85rem;
  border-radius: 20px;
  font-size: 0.85rem;
  white-space: nowrap;
}

.filters-card { padding: 1.25rem; width: 100%; box-sizing: border-box; }
.filters-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}
.flex-2 { flex: 2; min-width: 240px; }
.flex-1 { flex: 1; min-width: 180px; }
.form-group { display: flex; flex-direction: column; gap: 0.35rem; }
.form-label { font-size: 0.78rem; font-weight: 700; text-transform: uppercase; color: var(--text-muted, #64748b); }
.form-input, .form-select {
  padding: 0.55rem 0.75rem;
  border: 1px solid var(--border-medium, #cbd5e1);
  border-radius: 6px;
  background: var(--bg-surface, #ffffff);
  font-size: 0.88rem;
  color: var(--text-primary, #0f172a);
  width: 100%;
  box-sizing: border-box;
}

.table-card { padding: 0; overflow: hidden; width: 100%; box-sizing: border-box; }
.table-responsive { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; }
.portal-table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.88rem; min-width: 580px; }
.portal-table th { background: var(--bg-surface-secondary, #f8fafc); padding: 0.85rem 1.25rem; font-weight: 700; color: var(--text-secondary, #475569); border-bottom: 1px solid var(--border-subtle, #e2e8f0); }
.portal-table td { padding: 0.85rem 1.25rem; border-bottom: 1px solid var(--border-subtle, #e2e8f0); color: var(--text-primary, #0f172a); }
.font-bold { font-weight: 700; }
.class-badge { background: #e0f2fe; color: #0369a1; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.78rem; font-weight: 700; display: inline-block; }

.desktop-view { display: block; }
.mobile-view { display: none; padding: 0.75rem; flex-direction: column; gap: 0.75rem; }
.mobile-student-card {
  padding: 1rem;
  border: 1px solid var(--border-subtle, #e2e8f0);
  border-radius: 8px;
  background: var(--bg-surface, #ffffff);
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  box-sizing: border-box;
}
.mobile-card-top { display: flex; justify-content: space-between; align-items: center; }
.mobile-num { font-size: 0.75rem; color: var(--text-muted, #64748b); font-weight: 700; }
.mobile-name { margin: 0; font-size: 0.98rem; font-weight: 700; color: var(--text-primary, #0f172a); word-break: break-word; }
.mobile-meta-grid {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.82rem;
  color: var(--text-secondary, #475569);
  background: var(--bg-surface-secondary, #f8fafc);
  padding: 0.6rem;
  border-radius: 6px;
}
.meta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.meta-label {
  font-size: 0.75rem;
  color: var(--text-muted, #64748b);
  font-weight: 600;
}
.mobile-card-actions { padding-top: 0.4rem; border-top: 1px solid var(--border-subtle, #e2e8f0); }

/* Modal */
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
.modal-card.large {
  width: calc(100% - 24px);
  max-width: 650px;
  max-height: 90vh;
  background: #ffffff;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  border-radius: 8px;
  overflow-y: auto;
}
.modal-content-wrap {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.modal-header { display: flex; justify-content: space-between; align-items: flex-start; }
.modal-title { margin: 0; font-size: 1.2rem; font-weight: 800; word-break: break-word; }
.adm-code { font-size: 0.8rem; color: var(--text-muted, #64748b); display: block; margin-top: 0.2rem; }
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

.modal-stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem; margin-bottom: 0.75rem; }
.stat-box { background: var(--bg-surface-secondary, #f8fafc); padding: 0.65rem; border-radius: 6px; text-align: center; }
.stat-title { font-size: 0.68rem; color: var(--text-muted, #64748b); font-weight: 700; text-transform: uppercase; display: block; }
.stat-num { font-size: 1.15rem; font-weight: 800; display: block; margin-top: 0.15rem; }
.sub-heading { font-size: 0.95rem; font-weight: 700; margin: 0.75rem 0 0.5rem 0; }
.status-pill.absent { background: #fee2e2; color: #b91c1c; font-size: 0.75rem; font-weight: 700; padding: 0.15rem 0.45rem; border-radius: 4px; display: inline-block; }

.modal-footer { display: flex; justify-content: flex-end; padding-top: 0.75rem; border-top: 1px solid var(--border-subtle, #e2e8f0); }

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 0.9rem;
  border-radius: 6px;
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s;
}
.btn-touch { min-height: 44px; }
.btn-primary { background: #0284c7; color: #ffffff; }
.btn-primary:hover { background: #0369a1; }
.btn-outline { background: #ffffff; border-color: var(--border-medium, #cbd5e1); color: var(--text-primary, #0f172a); }
.btn-outline:hover { background: #f8fafc; }
.btn-xs { padding: 0.3rem 0.6rem; font-size: 0.78rem; }
.btn-block { width: 100%; }

.loading-box, .empty-box {
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
.spinner { width: 32px; height: 32px; border: 3px solid var(--border-subtle, #e2e8f0); border-top-color: #0284c7; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.alert-box.error { background: #fef2f2; color: #991b1b; padding: 1rem; border-radius: 6px; }

@media (max-width: 768px) {
  .desktop-view { display: none; }
  .mobile-view { display: flex; }
  .modal-stats-grid { grid-template-columns: repeat(2, 1fr); }
  .btn-block-mobile { width: 100%; }
}

@media (max-width: 480px) {
  .flex-2, .flex-1 { min-width: 100%; }
  .modal-stats-grid { grid-template-columns: 1fr 1fr; }
}
</style>
