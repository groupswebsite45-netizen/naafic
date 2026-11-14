<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import {
  formMasterService,
  type FormMasterClassSummary,
  type FormMasterResultsData,
} from '../../../services/formMasterService';

const loading = ref(false);
const errorMsg = ref('');
const myClasses = ref<FormMasterClassSummary[]>([]);
const selectedClassId = ref<number | null>(null);
const resultsData = ref<FormMasterResultsData | null>(null);

// Filters
const selectedExamType = ref<string>('ALL');
const selectedSubjectId = ref<number | string>('ALL');

onMounted(async () => {
  await loadClasses();
});

watch(selectedClassId, async (newId) => {
  if (newId) {
    await loadResults(newId);
  }
});

watch([selectedExamType, selectedSubjectId], async () => {
  if (selectedClassId.value) {
    await loadResults(selectedClassId.value);
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

async function loadResults(classId: number) {
  loading.value = true;
  errorMsg.value = '';
  try {
    const params: any = {};
    if (selectedExamType.value !== 'ALL') {
      params.exam_type = selectedExamType.value;
    }
    if (selectedSubjectId.value !== 'ALL') {
      params.subject_id = Number(selectedSubjectId.value);
    }
    const data = await formMasterService.getResults(classId, params);
    resultsData.value = data;
  } catch (err: any) {
    errorMsg.value = err?.response?.data?.detail || 'Failed to load examination results.';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="results-monitoring-view">
    <!-- Header -->
    <header class="page-header">
      <div class="header-main">
        <div class="title-wrap">
          <div class="icon-wrap bg-blue-subtle text-blue">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h1 class="page-title">Academic Results Monitoring</h1>
              <span class="badge badge-read-only">READ-ONLY SUPERVISORY ACCESS</span>
            </div>
            <p class="page-subtitle">
              Monitor class academic performance across all subjects. Subject teacher mark submissions are locked.
            </p>
          </div>
        </div>

        <!-- Class Switcher -->
        <div v-if="myClasses.length > 1" class="class-picker">
          <span class="picker-label">Class:</span>
          <select v-model="selectedClassId" class="picker-select">
            <option v-for="c in myClasses" :key="c.id" :value="c.id">
              {{ c.name }} ({{ c.division }})
            </option>
          </select>
        </div>
      </div>

      <!-- Read-Only Compliance Banner -->
      <div class="disclaimer-banner">
        <svg class="h-5 w-5 text-blue flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>
          <strong>Supervisory Access Notice:</strong> As Form Master, you can view scores for every subject in this class regardless of which faculty member taught it. You cannot edit marks or modify teacher submissions.
        </span>
      </div>
    </header>

    <!-- Error State -->
    <div v-if="errorMsg" class="alert alert-error">
      <span>{{ errorMsg }}</span>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner" />
      <p>Loading examination results and subject standings...</p>
    </div>

    <!-- Main Content -->
    <div v-else-if="resultsData" class="results-body">
      <!-- Performance Summary Cards -->
      <div class="summary-cards">
        <div class="card">
          <span class="card-label">Class Average</span>
          <span class="card-val text-blue">{{ resultsData.class_average }}%</span>
          <span class="card-sub">{{ resultsData.total_students }} students evaluated</span>
        </div>
        <div class="card">
          <span class="card-label">Overall Pass Rate</span>
          <span class="card-val" :class="resultsData.pass_rate >= 75 ? 'text-green' : 'text-amber'">
            {{ resultsData.pass_rate }}%
          </span>
          <span class="card-sub">&ge; 50% passing threshold</span>
        </div>
        <div class="card">
          <span class="card-label">Top Performers</span>
          <span class="card-val text-green">{{ resultsData.top_performers_count }}</span>
          <span class="card-sub">&ge; 80% Mastery / A Grade</span>
        </div>
        <div class="card">
          <span class="card-label">Needs Academic Support</span>
          <span class="card-val text-red">{{ resultsData.poor_performers_count }}</span>
          <span class="card-sub">Average &lt; 50% or failing subjects</span>
        </div>
      </div>

      <!-- Filters Row -->
      <div class="filters-card">
        <div class="filter-item">
          <label class="filter-label">Exam Type</label>
          <select v-model="selectedExamType" class="filter-select">
            <option value="ALL">All Assessment Types</option>
            <option v-for="t in resultsData.available_exam_types" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>

        <div class="filter-item">
          <label class="filter-label">Subject</label>
          <select v-model="selectedSubjectId" class="filter-select">
            <option value="ALL">All Subjects (Cross-Subject Matrix)</option>
            <option v-for="s in resultsData.subjects" :key="s.id" :value="s.id">{{ s.name }} ({{ s.code }})</option>
          </select>
        </div>
      </div>

      <!-- Results Sheet Table -->
      <div class="table-card">
        <div class="table-header">
          <div>
            <h2 class="table-title">Student Performance Matrix &mdash; {{ resultsData.class_name }}</h2>
            <p class="table-subtitle">Complete cross-subject performance overview</p>
          </div>
          <div class="legend-wrap">
            <span class="legend-item"><span class="dot dot-green" /> Passing (&ge;50%)</span>
            <span class="legend-item"><span class="dot dot-red" /> Needs Improvement (&lt;50%)</span>
          </div>
        </div>

        <div class="table-scroll">
          <table class="matrix-table">
            <thead>
              <tr>
                <th class="sticky-col">Rank</th>
                <th class="sticky-col-2">Student</th>
                <th>Admission #</th>
                <!-- Dynamically show all subjects in this class -->
                <th v-for="sub in resultsData.subjects" :key="sub.id" class="text-center">
                  {{ sub.name }}
                </th>
                <th class="text-center">Total Marks</th>
                <th class="text-center">Average</th>
                <th class="text-center">Grade</th>
                <th class="text-center">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="st in resultsData.students"
                :key="st.student_id"
                :class="{ 'row-warning': st.is_poor_performer }"
              >
                <td class="sticky-col font-bold">
                  {{ st.rank ? `#${st.rank}` : '—' }}
                </td>
                <td class="sticky-col-2 font-medium">
                  {{ st.name }}
                  <span v-if="st.is_poor_performer" class="badge-alert ml-1">Needs Help</span>
                </td>
                <td class="text-xs text-muted">{{ st.admission_number }}</td>

                <!-- Subject scores -->
                <td v-for="sub in resultsData.subjects" :key="sub.id" class="text-center">
                  <template v-if="st.subject_scores[sub.id]">
                    <span
                      v-if="st.subject_scores[sub.id].marks !== null"
                      class="subject-score"
                      :class="st.subject_scores[sub.id].marks >= 50 ? 'score-pass' : 'score-fail'"
                    >
                      {{ st.subject_scores[sub.id].marks }}
                    </span>
                    <span v-else class="text-muted text-xs">
                      {{ st.subject_scores[sub.id].attendance_status }}
                    </span>
                  </template>
                  <span v-else class="text-slate-300">&mdash;</span>
                </td>

                <td class="text-center font-bold">
                  {{ st.total_marks }}
                </td>
                <td class="text-center font-bold" :class="(st.average_marks || 0) >= 50 ? 'text-green' : 'text-red'">
                  {{ st.average_marks !== null ? `${st.average_marks}%` : '—' }}
                </td>
                <td class="text-center">
                  <span class="grade-badge" :class="st.grade === 'F' ? 'grade-f' : 'grade-pass'">
                    {{ st.grade || '—' }}
                  </span>
                </td>
                <td class="text-center">
                  <span v-if="st.is_poor_performer" class="status-alert">Intervention</span>
                  <span v-else class="status-ok">Good Standing</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.results-monitoring-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
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

.bg-blue-subtle { background: #eff6ff; }
.text-blue { color: #2563eb; }
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

.badge-read-only {
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #cbd5e1;
}

.disclaimer-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.8125rem;
  color: #475569;
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

/* Summary Cards */
.summary-cards {
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

/* Filters Card */
.filters-card {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1 1 200px;
}

.filter-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
}

.filter-select {
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #ffffff;
}

/* Table Card */
.table-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
}

.table-title {
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.table-subtitle {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0.125rem 0 0;
}

.legend-wrap {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: #64748b;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot-green { background: #16a34a; }
.dot-red { background: #dc2626; }

.table-scroll {
  overflow-x: auto;
}

.matrix-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8125rem;
}

.matrix-table th {
  padding: 0.75rem 1rem;
  background: #f8fafc;
  font-weight: 700;
  font-size: 0.6875rem;
  text-transform: uppercase;
  color: #64748b;
  border-bottom: 1px solid #e2e8f0;
  white-space: nowrap;
}

.matrix-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f1f5f9;
  white-space: nowrap;
}

.matrix-table tr.row-warning td {
  background: #fffbfb;
}

.subject-score {
  font-weight: 700;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
}

.score-pass {
  color: #15803d;
  background: #dcfce7;
}

.score-fail {
  color: #b91c1c;
  background: #fee2e2;
}

.badge-alert {
  font-size: 0.625rem;
  font-weight: 700;
  padding: 0.1rem 0.375rem;
  border-radius: 4px;
  background: #fee2e2;
  color: #b91c1c;
}

.grade-badge {
  font-size: 0.75rem;
  font-weight: 800;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
}

.grade-pass {
  background: #f0fdf4;
  color: #16a34a;
}

.grade-f {
  background: #fef2f2;
  color: #dc2626;
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

.sticky-col {
  position: sticky;
  left: 0;
  background: inherit;
  z-index: 2;
}

.sticky-col-2 {
  position: sticky;
  left: 50px;
  background: inherit;
  z-index: 2;
}

/* Loading & Spinner */
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

