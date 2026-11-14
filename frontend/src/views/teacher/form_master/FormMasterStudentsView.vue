<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import {
  formMasterService,
  type FormMasterClassSummary,
  type FormMasterStudentItem,
} from '../../../services/formMasterService';

const loading = ref(false);
const errorMsg = ref('');
const myClasses = ref<FormMasterClassSummary[]>([]);
const selectedClassId = ref<number | null>(null);
const students = ref<FormMasterStudentItem[]>([]);

const searchQuery = ref('');
const filterStatus = ref<'ALL' | 'POOR_ACADEMIC' | 'CHRONIC_ABSENT' | 'OVERDUE_FEES'>('ALL');

onMounted(async () => {
  await loadClasses();
});

watch(selectedClassId, async (newId) => {
  if (newId) {
    await loadStudents(newId);
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

async function loadStudents(classId: number) {
  loading.value = true;
  errorMsg.value = '';
  try {
    const data = await formMasterService.getStudents(classId);
    students.value = data;
  } catch (err: any) {
    errorMsg.value = err?.response?.data?.detail || 'Failed to load students.';
  } finally {
    loading.value = false;
  }
}

const filteredStudents = computed(() => {
  return students.value.filter((s) => {
    if (searchQuery.value.trim()) {
      const q = searchQuery.value.toLowerCase();
      const matchName = s.full_name.toLowerCase().includes(q);
      const matchAdm = s.admission_number.toLowerCase().includes(q);
      if (!matchName && !matchAdm) return false;
    }

    if (filterStatus.value === 'POOR_ACADEMIC') {
      return s.has_poor_academic_performance;
    }
    if (filterStatus.value === 'CHRONIC_ABSENT') {
      return s.has_frequent_absences;
    }
    if (filterStatus.value === 'OVERDUE_FEES') {
      return s.has_overdue_fees;
    }

    return true;
  });
});
</script>

<template>
  <div class="students-roster-view">
    <!-- Header -->
    <header class="page-header">
      <div class="header-main">
        <div class="title-wrap">
          <div class="icon-wrap bg-purple-subtle text-purple">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
          <div>
            <h1 class="page-title">Form Class Students Roster</h1>
            <p class="page-subtitle">
              Comprehensive student registry with holistic academic, attendance, and fee standing.
            </p>
          </div>
        </div>

        <!-- Class Picker -->
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
      <p>Loading class roster...</p>
    </div>

    <!-- Main Content -->
    <div v-else class="roster-body">
      <!-- Toolbar -->
      <div class="toolbar-card">
        <div class="search-wrap">
          <input
            v-model="searchQuery"
            type="text"
            class="search-input"
            placeholder="Search by student name or admission number..."
          />
        </div>

        <div class="filter-pills">
          <button
            type="button"
            class="pill-btn"
            :class="{ active: filterStatus === 'ALL' }"
            @click="filterStatus = 'ALL'"
          >
            All Students ({{ students.length }})
          </button>
          <button
            type="button"
            class="pill-btn"
            :class="{ active: filterStatus === 'POOR_ACADEMIC' }"
            @click="filterStatus = 'POOR_ACADEMIC'"
          >
            Academic Help Needed
          </button>
          <button
            type="button"
            class="pill-btn"
            :class="{ active: filterStatus === 'CHRONIC_ABSENT' }"
            @click="filterStatus = 'CHRONIC_ABSENT'"
          >
            Chronic Absences
          </button>
          <button
            type="button"
            class="pill-btn"
            :class="{ active: filterStatus === 'OVERDUE_FEES' }"
            @click="filterStatus = 'OVERDUE_FEES'"
          >
            Outstanding Fees
          </button>
        </div>
      </div>

      <!-- Students Table -->
      <div class="table-card">
        <table class="data-table">
          <thead>
            <tr>
              <th>Student</th>
              <th>Admission #</th>
              <th>Gender</th>
              <th>Guardian Contact</th>
              <th>Academic Avg</th>
              <th>Attendance</th>
              <th>Fee Status</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="s in filteredStudents"
              :key="s.student_id"
              :class="{
                'row-alert': s.has_poor_academic_performance || s.has_frequent_absences
              }"
            >
              <td class="font-medium">
                <div class="student-name-row">{{ s.full_name }}</div>
                <div class="tags-row">
                  <span v-if="s.has_poor_academic_performance" class="tag tag-red">Academic Alert</span>
                  <span v-if="s.has_frequent_absences" class="tag tag-amber">Chronic Absence</span>
                  <span v-if="s.has_overdue_fees" class="tag tag-orange">Fee Due</span>
                </div>
              </td>
              <td class="text-xs text-muted font-mono">{{ s.admission_number }}</td>
              <td>{{ s.gender }}</td>
              <td class="text-xs text-muted">
                <div>{{ s.guardian_name || 'Guardian' }} ({{ s.guardian_relationship || 'Contact' }})</div>
                <div>{{ s.guardian_phone || s.phone || 'No phone recorded' }}</div>
              </td>
              <td>
                <span
                  class="score-badge"
                  :class="s.average_marks != null && s.average_marks >= 50 ? 'text-green font-bold' : (s.average_marks != null ? 'text-red font-bold' : 'text-slate-400')"
                >
                  {{ s.average_marks != null ? `${s.average_marks}%` : 'No scores' }}
                </span>
                <span v-if="s.failing_subjects_count > 0" class="failing-hint">
                  ({{ s.failing_subjects_count }} fail)
                </span>
              </td>
              <td>
                <span
                  class="font-bold"
                  :class="s.attendance_rate >= 80 ? 'text-green' : 'text-amber'"
                >
                  {{ s.attendance_rate }}%
                </span>
                <span class="text-xs text-muted block">{{ s.absent_count }} absences</span>
              </td>
              <td>
                <span
                  class="status-pill"
                  :class="{
                    'status-paid': s.fee_status === 'PAID',
                    'status-partial': s.fee_status === 'PARTIALLY_PAID',
                    'status-unpaid': s.fee_status === 'UNPAID',
                    'status-nofees': s.fee_status === 'NO_FEES',
                  }"
                >
                  {{ s.fee_status }}
                </span>
                <span v-if="s.fee_balance > 0" class="balance-hint">
                  ${{ s.fee_balance }} due
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.students-roster-view {
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

.bg-purple-subtle { background: #faf5ff; }
.text-purple { color: #9333ea; }
.text-green { color: #16a34a; }
.text-red { color: #dc2626; }
.text-amber { color: #d97706; }

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

/* Toolbar */
.toolbar-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  flex-wrap: wrap;
}

.search-wrap {
  flex: 1 1 280px;
  max-width: 400px;
}

.search-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  outline: none;
}

.search-input:focus {
  border-color: #ff6500;
}

.filter-pills {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.pill-btn {
  padding: 0.375rem 0.75rem;
  font-size: 0.8125rem;
  font-weight: 600;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #64748b;
  cursor: pointer;
}

.pill-btn.active {
  background: #ff6500;
  border-color: #ff6500;
  color: #ffffff;
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

.data-table tr.row-alert td {
  background: #fffdfb;
}

.student-name-row {
  font-weight: 600;
  color: #0f172a;
}

.tags-row {
  display: flex;
  gap: 0.25rem;
  margin-top: 0.25rem;
}

.tag {
  font-size: 0.625rem;
  font-weight: 700;
  padding: 0.1rem 0.375rem;
  border-radius: 4px;
}

.tag-red { background: #fee2e2; color: #b91c1c; }
.tag-amber { background: #fef3c7; color: #b45309; }
.tag-orange { background: #fff7ed; color: #c2410c; }

.failing-hint {
  font-size: 0.6875rem;
  color: #dc2626;
  display: block;
}

.balance-hint {
  font-size: 0.6875rem;
  color: #dc2626;
  font-weight: 700;
  display: block;
  margin-top: 0.125rem;
}

.status-pill {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
}

.status-paid { background: #dcfce7; color: #166534; }
.status-partial { background: #fef3c7; color: #92400e; }
.status-unpaid { background: #fee2e2; color: #991b1b; }
.status-nofees { background: #f1f5f9; color: #64748b; }

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
