<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { resultWorkflowService } from '../../../../services/resultWorkflowService';
import { ResultOverviewStats, ClassResultSummaryItem } from '../../../../types/resultWorkflow';
import AcademicYearSelector from '../../../../components/results/AcademicYearSelector.vue';
import ExamSelector from '../../../../components/results/ExamSelector.vue';
import ResultStats from '../../../../components/results/ResultStats.vue';
import ResultStatusBadge from '../../../../components/results/ResultStatusBadge.vue';

const router = useRouter();

const academicYears = ref<string[]>([]);
const selectedYear = ref<string>('2025-2026');
const examNames = ref<string[]>([]);
const selectedExam = ref<string>('Final Examination 2026');

const stats = ref<ResultOverviewStats | null>(null);
const classes = ref<ClassResultSummaryItem[]>([]);

const isLoading = ref(true);
const errorMessage = ref('');

async function loadFilterOptions() {
  try {
    const opts = await resultWorkflowService.getFilterOptions();
    academicYears.value = opts.academic_years;
    if (opts.selected_academic_year) {
      selectedYear.value = opts.selected_academic_year;
    }
    examNames.value = opts.exam_names;
    if (opts.exam_names.length > 0) {
      selectedExam.value = opts.exam_names[0];
    }
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to initialize examination filters.';
  }
}

async function loadData() {
  if (!selectedYear.value || !selectedExam.value) return;
  isLoading.value = true;
  errorMessage.value = '';
  try {
    const [overviewData, classesData] = await Promise.all([
      resultWorkflowService.getOverviewStats(selectedYear.value, selectedExam.value),
      resultWorkflowService.getClassesResultSummary(selectedYear.value, selectedExam.value),
    ]);
    stats.value = overviewData;
    classes.value = classesData;
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to load live examination result telemetry.';
  } finally {
    isLoading.value = false;
  }
}

async function handleYearChange(newYear: string) {
  selectedYear.value = newYear;
  const opts = await resultWorkflowService.getFilterOptions(newYear);
  examNames.value = opts.exam_names;
  if (opts.exam_names.length > 0 && !opts.exam_names.includes(selectedExam.value)) {
    selectedExam.value = opts.exam_names[0];
  }
  await loadData();
}

async function handleExamChange(newExam: string) {
  selectedExam.value = newExam;
  await loadData();
}

function openClassDetail(classId: number) {
  router.push({
    name: 'admin-class-result-detail',
    params: { classId: String(classId) },
    query: {
      academic_year: selectedYear.value,
      exam_name: selectedExam.value,
    },
  });
}

function goToSubmissions() {
  router.push({
    name: 'admin-teacher-submissions',
    query: {
      academic_year: selectedYear.value,
      exam_name: selectedExam.value,
    },
  });
}

onMounted(async () => {
  await loadFilterOptions();
  await loadData();
});
</script>

<template>
  <div class="results-page">
    <!-- Top Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="pre-title">EXAMINATION & RESULTS WORKFLOW</div>
        <h1 class="page-title">Admin Result Monitoring & Verification</h1>
        <p class="page-desc">
          Strict stage-by-stage oversight: Teacher Draft &rarr; Submitted &rarr; Admin Review &rarr; Approved &rarr; Class Release.
        </p>
      </div>

      <div class="header-actions">
        <button type="button" class="submissions-btn" @click="goToSubmissions">
          <svg class="btn-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          <span>Teacher Submissions</span>
        </button>
      </div>
    </div>

    <!-- Error Banner -->
    <div v-if="errorMessage" class="error-banner">
      <span>{{ errorMessage }}</span>
    </div>

    <!-- Scoping Controls: ACADEMIC YEAR FIRST -->
    <div class="controls-panel">
      <div class="filters-wrap">
        <AcademicYearSelector
          :model-value="selectedYear"
          :options="academicYears"
          :disabled="isLoading"
          @change="handleYearChange"
        />

        <ExamSelector
          :model-value="selectedExam"
          :options="examNames"
          :disabled="isLoading"
          @change="handleExamChange"
        />
      </div>

      <div class="filter-hint">
        Scoped strictly by <strong>{{ selectedYear }}</strong> &bull; Results are never mixed across academic sessions.
      </div>
    </div>

    <!-- KPI Metric Cards from PostgreSQL -->
    <ResultStats :stats="stats" :is-loading="isLoading" />

    <!-- Class-First Navigation Section -->
    <div class="classes-section">
      <div class="section-head">
        <div>
          <h3 class="section-title">Class Result Status Overview</h3>
          <p class="section-subtitle">
            Showing all classes for <strong>{{ selectedExam }}</strong> ({{ selectedYear }}). Click a class to inspect subject marks and publish results.
          </p>
        </div>
        <div class="classes-count-tag">
          {{ classes.length }} Classes Configured
        </div>
      </div>

      <!-- Desktop & Tablet Class Table -->
      <div class="table-container desktop-only" tabindex="0" role="region" aria-label="Class Result Summaries">
        <table class="classes-table" aria-label="Class Result Summaries">
          <thead>
            <tr>
              <th scope="col">CLASS</th>
              <th scope="col" class="text-center">STUDENTS</th>
              <th scope="col" class="text-center">SUBJECTS</th>
              <th scope="col" class="text-center">EXPECTED</th>
              <th scope="col" class="text-center">SUBMITTED</th>
              <th scope="col" class="text-center">PENDING</th>
              <th scope="col" class="text-center">APPROVED</th>
              <th scope="col" class="text-center">RELEASED</th>
              <th scope="col" class="text-center">VIEWED</th>
              <th scope="col" class="text-center">STATUS</th>
              <th scope="col" class="text-right">ACTION</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="isLoading">
              <td colspan="11" class="loading-cell">Loading real PostgreSQL class completion telemetry...</td>
            </tr>
            <tr v-else-if="classes.length === 0">
              <td colspan="11" class="empty-cell">No classes enrolled for {{ selectedYear }}.</td>
            </tr>
            <tr v-for="c in classes" :key="c.class_id" class="class-row">
              <td class="class-name-col">
                <div class="class-name-text">{{ c.class_name }}</div>
                <div class="class-code-text">{{ c.class_code }}</div>
              </td>
              <td class="text-center metric-num">{{ c.students_count }}</td>
              <td class="text-center metric-num">{{ c.subjects_count }}</td>
              <td class="text-center metric-num font-bold">{{ c.expected_results }}</td>
              <td class="text-center metric-num highlight-amber">{{ c.submitted_results }}</td>
              <td class="text-center metric-num" :class="{ 'highlight-red': c.pending_results > 0 }">
                {{ c.pending_results }}
              </td>
              <td class="text-center metric-num highlight-blue">{{ c.approved_results }}</td>
              <td class="text-center metric-num highlight-emerald">{{ c.released_results }}</td>
              <td class="text-center metric-num highlight-viewed">
                {{ c.viewed_results }} <span class="viewed-denom">/ {{ c.released_results }}</span>
              </td>
              <td class="text-center">
                <ResultStatusBadge :status="c.status" size="sm" />
              </td>
              <td class="text-right">
                <button
                  type="button"
                  class="inspect-btn"
                  @click="openClassDetail(c.class_id)"
                >
                  View Details &rarr;
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile Class Cards (320px - 768px) -->
      <div class="mobile-only mobile-class-list">
        <div v-if="isLoading" class="mobile-loading">Loading classes...</div>
        <div v-else-if="classes.length === 0" class="empty-cell">No classes enrolled.</div>
        <div
          v-for="c in classes"
          :key="`mob-cls-${c.class_id}`"
          class="mobile-class-card"
        >
          <div class="mobile-class-head">
            <div>
              <h4 class="mob-title">{{ c.class_name }}</h4>
              <span class="mob-sub">{{ c.class_code }} &bull; {{ c.students_count }} Students</span>
            </div>
            <ResultStatusBadge :status="c.status" size="sm" />
          </div>

          <div class="mob-stats-grid">
            <div class="mob-stat">
              <span class="mob-stat-lbl">Expected</span>
              <span class="mob-stat-val">{{ c.expected_results }}</span>
            </div>
            <div class="mob-stat">
              <span class="mob-stat-lbl">Submitted</span>
              <span class="mob-stat-val text-amber">{{ c.submitted_results }}</span>
            </div>
            <div class="mob-stat">
              <span class="mob-stat-lbl">Approved</span>
              <span class="mob-stat-val text-blue">{{ c.approved_results }}</span>
            </div>
            <div class="mob-stat">
              <span class="mob-stat-lbl">Released</span>
              <span class="mob-stat-val text-emerald">{{ c.released_results }}</span>
            </div>
          </div>

          <button
            type="button"
            class="mob-action-btn"
            @click="openClassDetail(c.class_id)"
          >
            Inspect Class Results Matrix
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.results-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
  box-sizing: border-box;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.pre-title {
  font-size: 0.6875rem;
  font-weight: 700;
  color: #38bdf8;
  letter-spacing: 0.08em;
}

.page-title {
  font-size: 1.625rem;
  font-weight: 800;
  color: #ffffff;
  margin: 0.15rem 0 0.35rem 0;
  line-height: 1.2;
}

.page-desc {
  font-size: 0.8125rem;
  color: #94a3b8;
  margin: 0;
}

.submissions-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #1e293b;
  color: #f8fafc;
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 0.6rem 1rem;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.submissions-btn:hover {
  background-color: #334155;
  border-color: #0284c7;
  color: #ffffff;
}

.btn-icon {
  width: 1rem;
  height: 1rem;
  color: #38bdf8;
}

.error-banner {
  background-color: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.8125rem;
}

.controls-panel {
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 1.15rem 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.filters-wrap {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  flex-wrap: wrap;
}

.filter-hint {
  font-size: 0.75rem;
  color: #64748b;
}

.classes-section {
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.section-head {
  padding: 1.25rem 1.5rem;
  background-color: #0f172a;
  border-bottom: 1px solid #334155;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 0.2rem 0;
}

.section-subtitle {
  font-size: 0.75rem;
  color: #94a3b8;
  margin: 0;
}

.classes-count-tag {
  background-color: #1e293b;
  border: 1px solid #334155;
  color: #38bdf8;
  padding: 0.3rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 700;
}

.table-container {
  overflow-x: auto;
}

.classes-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8125rem;
  text-align: left;
}

.classes-table th {
  background-color: #0f172a;
  color: #94a3b8;
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #334155;
  white-space: nowrap;
}

.classes-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #334155;
  color: #f8fafc;
}

.class-row:hover {
  background-color: rgba(51, 65, 85, 0.4);
}

.class-name-col { min-width: 140px; }
.class-name-text { font-weight: 700; color: #ffffff; }
.class-code-text { font-size: 0.6875rem; color: #94a3b8; }

.metric-num { font-variant-numeric: tabular-nums; font-weight: 600; }
.font-bold { font-weight: 700; }
.highlight-amber { color: #fbbf24; }
.highlight-blue { color: #60a5fa; }
.highlight-emerald { color: #34d399; }
.highlight-red { color: #f87171; font-weight: 700; }
.highlight-viewed { color: #34d399; font-weight: 700; }
.viewed-denom { font-size: 0.75rem; color: #64748b; font-weight: 500; }

.text-center { text-align: center; }
.text-right { text-align: right; }

.inspect-btn {
  background-color: #0284c7;
  color: #ffffff;
  border: none;
  padding: 0.4rem 0.85rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.inspect-btn:hover { background-color: #0369a1; }
.loading-cell, .empty-cell { text-align: center; padding: 2.5rem 1rem; color: #94a3b8; }

/* Mobile Card View */
.mobile-only { display: none; }
.desktop-only { display: block; }

@media (max-width: 820px) {
  .desktop-only { display: none; }
  .mobile-only { display: block; }

  .mobile-class-list {
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
  }

  .mobile-class-card {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .mobile-class-head {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
  }

  .mob-title {
    font-size: 1rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0;
  }

  .mob-sub {
    font-size: 0.6875rem;
    color: #94a3b8;
  }

  .mob-stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.4rem;
    background-color: #1e293b;
    border-radius: 6px;
    padding: 0.5rem;
    text-align: center;
  }

  .mob-stat-lbl {
    display: block;
    font-size: 0.5625rem;
    color: #64748b;
    text-transform: uppercase;
    font-weight: 700;
  }

  .mob-stat-val {
    font-size: 0.875rem;
    font-weight: 800;
    color: #ffffff;
  }

  .text-amber { color: #fbbf24; }
  .text-blue { color: #60a5fa; }
  .text-emerald { color: #34d399; }

  .mob-action-btn {
    width: 100%;
    background-color: #0284c7;
    color: #ffffff;
    border: none;
    padding: 0.5rem;
    border-radius: 6px;
    font-size: 0.8125rem;
    font-weight: 600;
    cursor: pointer;
  }
}
</style>
