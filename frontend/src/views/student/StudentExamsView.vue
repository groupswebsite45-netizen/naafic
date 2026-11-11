<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { studentPortalService } from '../../services/studentPortalService';
import { StudentExamResultItem } from '../../types/studentPortal';

const results = ref<StudentExamResultItem[]>([]);
const academicYears = ref<string[]>([]);
const selectedYear = ref<string>('');
const selectedExam = ref<string>('');
const isLoading = ref(true);
const errorMessage = ref('');

// Group results by exam name + academic year
const examGroups = computed(() => {
  const groups: Record<string, StudentExamResultItem[]> = {};
  for (const r of results.value) {
    const key = `${r.exam_name || 'Official Examination'} (${r.academic_year || selectedYear.value})`;
    if (!groups[key]) groups[key] = [];
    groups[key].push(r);
  }
  return groups;
});

const currentExamResults = computed(() => {
  if (!selectedExam.value) return [];
  return examGroups.value[selectedExam.value] || [];
});

// Computed Summary Stats for the selected exam
const examStats = computed(() => {
  const list = currentExamResults.value;
  if (list.length === 0) return null;

  const attendedList = list.filter((r) => r.attendance_status === 'PRESENT' && r.marks_obtained !== null);
  const totalScore = attendedList.reduce((acc, r) => acc + (Number(r.marks_obtained) || 0), 0);
  const totalMax = attendedList.reduce((acc, r) => acc + (Number(r.total_marks) || 100), 0);
  const avgPct = totalMax > 0 ? Math.round((totalScore / totalMax) * 100) : 0;
  const absentCount = list.filter((r) => r.attendance_status === 'ABSENT').length;
  const passedCount = attendedList.filter((r) => (Number(r.percentage) || 0) >= 50).length;
  const failedCount = attendedList.length - passedCount;

  let overallGrade = 'F';
  if (avgPct >= 90) overallGrade = 'A+';
  else if (avgPct >= 80) overallGrade = 'A';
  else if (avgPct >= 70) overallGrade = 'B+';
  else if (avgPct >= 60) overallGrade = 'B';
  else if (avgPct >= 50) overallGrade = 'C';

  return {
    subjectsCount: list.length,
    attendedCount: attendedList.length,
    absentCount,
    passedCount,
    failedCount,
    totalScore: Math.round(totalScore * 100) / 100,
    totalMax,
    avgPct,
    overallGrade,
  };
});

async function loadResults() {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    results.value = await studentPortalService.getMyExams(selectedYear.value || undefined);

    const keys = Object.keys(examGroups.value);
    if (keys.length > 0) {
      selectedExam.value = keys[0];
      await triggerViewRecord(currentExamResults.value[0]);
    } else {
      selectedExam.value = '';
    }
  } catch (err: any) {
    errorMessage.value = err?.response?.data?.detail || 'Failed to retrieve released exam results.';
  } finally {
    isLoading.value = false;
  }
}

async function triggerViewRecord(sampleResult?: StudentExamResultItem) {
  if (!sampleResult || !sampleResult.exam_name) return;
  try {
    await studentPortalService.recordExamView({
      exam_name: sampleResult.exam_name,
      academic_year: sampleResult.academic_year || selectedYear.value || '2025-2026',
      class_id: sampleResult.class_id,
    });
  } catch {
    // Non-blocking view tracking
  }
}

async function selectExam(examKey: string) {
  selectedExam.value = examKey;
  const sample = currentExamResults.value[0];
  if (sample) {
    await triggerViewRecord(sample);
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
  await loadResults();
}

onMounted(() => {
  initPage();
});
</script>

<template>
  <div class="portal-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content-row">
        <div>
          <h1 class="page-title">My Official Examination Results</h1>
          <p class="page-subtitle">Verified academic transcripts and subject score breakdowns released by School Administration.</p>
        </div>

        <!-- Academic Year Selector -->
        <div v-if="academicYears.length > 0" class="year-selector-wrap">
          <label for="exam-year-select" class="selector-lbl">Academic Year:</label>
          <select
            id="exam-year-select"
            v-model="selectedYear"
            class="year-select"
            @change="loadResults"
          >
            <option v-for="y in academicYears" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="errorMessage" class="card error-card">
      <p class="error-title">Unable to Load Examination Results</p>
      <p class="error-desc">{{ errorMessage }}</p>
      <button class="retry-btn" @click="loadResults">Try Again</button>
    </div>

    <!-- Main Container -->
    <div class="report-container card">
      <!-- Loading State -->
      <div v-if="isLoading" class="loading-state">
        <div class="spinner" />
        <span>Loading released assessment records from PostgreSQL...</span>
      </div>

      <!-- Empty State -->
      <div v-else-if="results.length === 0" class="empty-state">
        <div class="empty-icon-wrap">
          <svg class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 class="empty-title">Results Are Being Processed</h3>
        <p class="empty-desc">
          No examination results have been officially released for academic year {{ selectedYear }} yet.
          Marks are undergoing administrative review and will appear here immediately upon official release.
        </p>
      </div>

      <div v-else class="results-content">
        <!-- Exam Switcher Pills if multiple exams available -->
        <div v-if="Object.keys(examGroups).length > 1" class="exam-selector-bar">
          <button
            v-for="key in Object.keys(examGroups)"
            :key="key"
            type="button"
            class="exam-pill-btn"
            :class="{ active: selectedExam === key }"
            @click="selectExam(key)"
          >
            {{ key }}
          </button>
        </div>

        <!-- Official Report Card Banner -->
        <div class="report-card-banner">
          <div class="banner-left">
            <div class="school-seal-badge">EMS</div>
            <div>
              <h2 class="exam-heading">{{ selectedExam }}</h2>
              <div class="meta-row">
                <span>Official Transcript &bull; Academic Year: <strong>{{ selectedYear }}</strong></span>
              </div>
            </div>
          </div>
          <div class="banner-right">
            <div class="gpa-box">
              <span class="gpa-lbl">OVERALL GRADE</span>
              <span class="gpa-val">{{ examStats?.overallGrade }}</span>
              <span class="gpa-sub">{{ examStats?.avgPct }}%</span>
            </div>
          </div>
        </div>

        <!-- Summary KPI Strip -->
        <div class="stats-strip">
          <div class="strip-item">
            <span class="strip-lbl">TOTAL SUBJECTS</span>
            <span class="strip-val">{{ examStats?.subjectsCount }}</span>
          </div>
          <div class="strip-item">
            <span class="strip-lbl">ATTENDED</span>
            <span class="strip-val text-emerald">{{ examStats?.attendedCount }}</span>
          </div>
          <div class="strip-item">
            <span class="strip-lbl">PASSED</span>
            <span class="strip-val text-emerald">{{ examStats?.passedCount }}</span>
          </div>
          <div class="strip-item">
            <span class="strip-lbl">TOTAL MARKS</span>
            <span class="strip-val font-bold">
              {{ examStats?.totalScore }} / {{ examStats?.totalMax }}
            </span>
          </div>
        </div>

        <!-- Desktop Report Table -->
        <div class="desktop-table-wrap" tabindex="0" role="region" aria-label="Exam report table">
          <table class="report-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Subject</th>
                <th class="text-center">Attendance</th>
                <th class="text-center">Score</th>
                <th class="text-center">Max Marks</th>
                <th class="text-center">Percentage</th>
                <th class="text-center">Grade</th>
                <th>Remarks</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(r, idx) in currentExamResults" :key="r.id" class="result-row">
                <td class="idx-col">{{ idx + 1 }}</td>
                <td class="subject-col">
                  <strong>{{ r.subject_name }}</strong>
                  <span v-if="r.subject_code" class="sub-code">{{ r.subject_code }}</span>
                </td>
                <td class="text-center">
                  <span class="attendance-pill" :class="r.attendance_status.toLowerCase()">
                    {{ r.attendance_status }}
                  </span>
                </td>
                <td class="text-center score-col">
                  <span v-if="r.attendance_status === 'PRESENT' && r.marks_obtained !== null">
                    {{ r.marks_obtained }}
                  </span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td class="text-center max-col">{{ r.total_marks }}</td>
                <td class="text-center pct-col">
                  <span v-if="r.attendance_status === 'PRESENT' && r.percentage !== null">
                    {{ r.percentage }}%
                  </span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td class="text-center">
                  <span
                    class="grade-pill"
                    :class="{
                      'grade-high': r.grade === 'A+' || r.grade === 'A' || r.grade === 'B' || r.grade === 'B+',
                      'grade-low': r.grade === 'F',
                      'grade-abs': r.grade === 'ABSENT' || r.grade === 'EXCUSED',
                    }"
                  >
                    {{ r.grade || '—' }}
                  </span>
                </td>
                <td class="remarks-col">{{ r.remarks || 'Satisfactory progress' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile Stacked Cards Layout -->
        <div class="mobile-results-cards">
          <div v-for="(r, idx) in currentExamResults" :key="r.id" class="mobile-res-card">
            <div class="res-card-top">
              <span class="res-idx">#{{ idx + 1 }}</span>
              <span class="grade-pill" :class="r.grade === 'F' ? 'grade-low' : 'grade-high'">
                {{ r.grade || '—' }}
              </span>
            </div>
            <h4 class="res-subj-name">{{ r.subject_name }}</h4>
            <div class="res-score-row">
              <div class="res-score-item">
                <span class="lbl">Score</span>
                <strong class="val">
                  {{ r.marks_obtained !== null ? `${r.marks_obtained} / ${r.total_marks}` : 'Absent' }}
                </strong>
              </div>
              <div class="res-score-item">
                <span class="lbl">Percentage</span>
                <strong class="val">{{ r.percentage !== null ? `${r.percentage}%` : '—' }}</strong>
              </div>
              <div class="res-score-item">
                <span class="lbl">Status</span>
                <span class="attendance-pill" :class="r.attendance_status.toLowerCase()">
                  {{ r.attendance_status }}
                </span>
              </div>
            </div>
            <div v-if="r.remarks" class="res-card-remarks">Remarks: {{ r.remarks }}</div>
          </div>
        </div>

        <!-- Official Seal / Verification Footer -->
        <div class="delivery-receipt-footer">
          <svg class="check-badge-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
          <span>
            Official Education Management System digital report card. Only officially approved and released marks are published. Result view timestamp is recorded in the audit log.
          </span>
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

.header-content-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1rem;
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

.year-selector-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  padding: 0.4rem 0.75rem;
  border-radius: 8px;
}

.selector-lbl {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
}

.year-select {
  background: var(--bg-surface-secondary);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
  padding: 0.35rem 0.65rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  outline: none;
  cursor: pointer;
}

.report-container {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  overflow: hidden;
}

/* Exam Selector Bar */
.exam-selector-bar {
  display: flex;
  gap: 0.5rem;
  padding: 1rem 1.25rem 0.5rem 1.25rem;
  overflow-x: auto;
  border-bottom: 1px solid var(--border-subtle);
}

.exam-pill-btn {
  background: var(--bg-surface-secondary);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  border-radius: 20px;
  padding: 0.4rem 1rem;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
}

.exam-pill-btn.active {
  background: #10b981;
  color: #fff;
  border-color: #10b981;
}

/* Banner */
.report-card-banner {
  padding: 1.5rem;
  background: linear-gradient(135deg, var(--bg-surface) 0%, rgba(16, 185, 129, 0.08) 100%);
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.banner-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.school-seal-badge {
  background: linear-gradient(135deg, #047857 0%, #10b981 100%);
  color: #fff;
  font-weight: 900;
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  padding: 0.75rem 0.85rem;
  border-radius: 10px;
}

.exam-heading {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}

.meta-row {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.meta-row strong {
  color: var(--text-primary);
}

.gpa-box {
  background-color: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 10px;
  padding: 0.65rem 1.25rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.gpa-lbl {
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  color: #10b981;
}

.gpa-val {
  font-size: 1.5rem;
  font-weight: 900;
  color: #10b981;
}

.gpa-sub {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-secondary);
}

/* Stats Strip */
.stats-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
  background-color: var(--bg-surface-secondary);
  padding: 0.85rem 1.5rem;
  border-bottom: 1px solid var(--border-subtle);
  text-align: center;
}

.strip-item {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.strip-lbl {
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 0.05em;
}

.strip-val {
  font-size: 1.2rem;
  font-weight: 800;
  color: var(--text-primary);
}

.text-emerald { color: #10b981; }

/* Table */
.desktop-table-wrap {
  overflow-x: auto;
}

.report-table {
  width: 100%;
  min-width: 580px;
  border-collapse: collapse;
  font-size: 0.88rem;
  text-align: left;
}

.report-table th {
  background-color: var(--bg-surface-secondary);
  color: var(--text-muted);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  padding: 0.85rem 1.25rem;
  border-bottom: 1px solid var(--border-subtle);
}

.report-table td {
  padding: 0.85rem 1.25rem;
  border-bottom: 1px solid var(--border-subtle);
  color: var(--text-primary);
  vertical-align: middle;
}

.idx-col { color: var(--text-muted); width: 35px; }
.subject-col strong { color: var(--text-primary); }
.sub-code { display: block; font-size: 0.72rem; color: var(--text-muted); }
.score-col { font-weight: 800; font-size: 0.95rem; }
.max-col { color: var(--text-muted); }
.pct-col { font-weight: 700; }
.remarks-col { font-size: 0.8rem; color: var(--text-secondary); }

.attendance-pill {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.attendance-pill.present { background-color: rgba(16, 185, 129, 0.15); color: #10b981; }
.attendance-pill.absent { background-color: rgba(239, 68, 68, 0.15); color: #ef4444; }
.attendance-pill.excused { background-color: rgba(245, 158, 11, 0.15); color: #f59e0b; }

.grade-pill {
  display: inline-block;
  padding: 0.2rem 0.55rem;
  border-radius: 4px;
  font-weight: 800;
  font-size: 0.82rem;
}

.grade-high { background-color: rgba(16, 185, 129, 0.18); color: #10b981; }
.grade-low { background-color: rgba(239, 68, 68, 0.18); color: #ef4444; }
.grade-abs { background-color: rgba(245, 158, 11, 0.18); color: #f59e0b; }

.text-center { text-align: center; }
.text-muted { color: var(--text-muted); }

/* Mobile Cards */
.mobile-results-cards {
  display: none;
  flex-direction: column;
  gap: 0.85rem;
  padding: 1rem;
}

.mobile-res-card {
  padding: 1rem;
  background: var(--bg-surface-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.res-card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.res-idx {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-muted);
}

.res-subj-name {
  font-size: 1.05rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}

.res-score-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  background: var(--bg-surface);
  padding: 0.65rem;
  border-radius: 6px;
}

.res-score-item {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.res-score-item .lbl {
  font-size: 0.68rem;
  color: var(--text-muted);
}

.res-score-item .val {
  font-size: 0.95rem;
  color: var(--text-primary);
}

.res-card-remarks {
  font-size: 0.78rem;
  color: var(--text-muted);
  font-style: italic;
}

/* Footer Verification Badge */
.delivery-receipt-footer {
  padding: 0.85rem 1.5rem;
  background-color: var(--bg-surface-secondary);
  border-top: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  gap: 0.65rem;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.check-badge-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: #10b981;
  flex-shrink: 0;
}

/* Common */
.loading-state, .empty-state, .error-card {
  padding: 4rem 1.5rem;
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
  width: 52px;
  height: 52px;
  background-color: var(--bg-surface-secondary);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-icon {
  width: 1.75rem;
  height: 1.75rem;
  color: var(--text-muted);
}

.empty-title, .error-title {
  font-size: 1.2rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}

.empty-desc, .error-desc {
  font-size: 0.85rem;
  color: var(--text-muted);
  max-width: 500px;
  line-height: 1.5;
  margin: 0;
}

.retry-btn {
  background-color: #0f172a;
  color: #fff;
  border: 1px solid #334155;
  padding: 0.4rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

@media (max-width: 768px) {
  .desktop-table-wrap {
    display: none;
  }
  .mobile-results-cards {
    display: flex;
  }
  .stats-strip {
    grid-template-columns: repeat(2, 1fr);
  }
  .report-card-banner {
    flex-direction: column;
    align-items: flex-start;
  }
  .gpa-box {
    width: 100%;
  }
}
</style>
