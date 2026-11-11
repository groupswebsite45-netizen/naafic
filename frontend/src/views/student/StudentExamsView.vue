<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { studentPortalService } from '../../services/studentPortalService';
import { StudentExamResultItem, StudentPublishedExamItem } from '../../types/studentPortal';

// Active Tab: 'schedules' | 'results'
const activeTab = ref<'schedules' | 'results'>('schedules');

const publishedExams = ref<StudentPublishedExamItem[]>([]);
const results = ref<StudentExamResultItem[]>([]);
const academicYears = ref<string[]>([]);
const selectedYear = ref<string>('');
const selectedExam = ref<string>('');
const isLoading = ref(true);
const errorMessage = ref('');

// Group published exams by Exam Name + Academic Year for cleaner presentation
const publishedExamGroups = computed(() => {
  const groups: Record<string, StudentPublishedExamItem[]> = {};
  for (const ex of publishedExams.value) {
    const key = `${ex.name} (${ex.academic_year})`;
    if (!groups[key]) groups[key] = [];
    groups[key].push(ex);
  }
  return groups;
});

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

// Computed Summary Stats for the selected exam results
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

async function loadData() {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    const [fetchedExams, fetchedResults] = await Promise.all([
      studentPortalService.getPublishedExams(selectedYear.value || undefined),
      studentPortalService.getMyResults(selectedYear.value || undefined),
    ]);

    publishedExams.value = fetchedExams || [];
    results.value = fetchedResults || [];

    // Select active tab based on available data
    if (publishedExams.value.length === 0 && results.value.length > 0) {
      activeTab.value = 'results';
    }

    const keys = Object.keys(examGroups.value);
    if (keys.length > 0) {
      selectedExam.value = keys[0];
      await triggerViewRecord(currentExamResults.value[0]);
    } else {
      selectedExam.value = '';
    }
  } catch (err: any) {
    errorMessage.value = err?.response?.data?.detail || 'Failed to retrieve examination records.';
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

function switchToResults(examName?: string) {
  activeTab.value = 'results';
  if (examName) {
    const matchKey = Object.keys(examGroups.value).find((k) => k.startsWith(examName));
    if (matchKey) {
      selectExam(matchKey);
    }
  }
}

function formatDate(dateStr?: string | null): string {
  if (!dateStr) return 'TBA';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  } catch {
    return dateStr;
  }
}

async function initPage() {
  try {
    academicYears.value = await studentPortalService.getAcademicYears();
    if (academicYears.value.length > 0) {
      selectedYear.value = academicYears.value[0];
    }
  } catch {
    academicYears.value = ['2026/2027', '2025/2026'];
    selectedYear.value = '2026/2027';
  }
  await loadData();
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
          <h1 class="page-title">My Examinations & Academic Transcripts</h1>
          <p class="page-subtitle">View published examination schedules, timetables, and officially released transcripts.</p>
        </div>

        <!-- Controls: Year Selector & Refresh -->
        <div class="header-actions">
          <div v-if="academicYears.length > 0" class="year-selector-wrap">
            <label for="exam-year-select" class="selector-lbl">Academic Year:</label>
            <select
              id="exam-year-select"
              v-model="selectedYear"
              class="year-select"
              @change="loadData"
            >
              <option v-for="y in academicYears" :key="y" :value="y">{{ y }}</option>
            </select>
          </div>

          <button
            type="button"
            class="btn-refresh"
            title="Refresh examination data"
            :disabled="isLoading"
            @click="loadData"
          >
            <svg class="refresh-icon" :class="{ spinning: isLoading }" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
            </svg>
            <span class="btn-text">Refresh</span>
          </button>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div class="tabs-nav">
        <button
          type="button"
          class="tab-btn"
          :class="{ active: activeTab === 'schedules' }"
          @click="activeTab = 'schedules'"
        >
          <svg class="tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <span>Published Exams & Schedules</span>
          <span class="badge-count" :class="{ highlight: publishedExams.length > 0 }">
            {{ publishedExams.length }}
          </span>
        </button>

        <button
          type="button"
          class="tab-btn"
          :class="{ active: activeTab === 'results' }"
          @click="activeTab = 'results'"
        >
          <svg class="tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>Verified Results & Transcripts</span>
          <span class="badge-count" :class="{ highlight: results.length > 0 }">
            {{ results.length }}
          </span>
        </button>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="errorMessage" class="card error-card">
      <p class="error-title">Unable to Load Examination Data</p>
      <p class="error-desc">{{ errorMessage }}</p>
      <button class="retry-btn" @click="loadData">Try Again</button>
    </div>

    <!-- Main Container -->
    <div class="report-container card">
      <!-- Loading State -->
      <div v-if="isLoading" class="loading-state">
        <div class="spinner" />
        <span>Loading examination schedules and transcripts from database...</span>
      </div>

      <!-- TAB 1: PUBLISHED EXAMS & SCHEDULES -->
      <div v-else-if="activeTab === 'schedules'" class="schedules-view">
        <!-- Empty State -->
        <div v-if="publishedExams.length === 0" class="empty-state">
          <div class="empty-icon-wrap">
            <svg class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <h3 class="empty-title">No Published Examinations Found</h3>
          <p class="empty-desc">
            There are currently no examinations scheduled or published for your enrolled class in academic year {{ selectedYear }}.
            Upcoming examination dates, timetables, and subject schedules announced by school administration will appear here automatically.
          </p>
        </div>

        <!-- Published Exams List -->
        <div v-else class="published-exams-wrap">
          <div
            v-for="(groupExams, groupName) in publishedExamGroups"
            :key="groupName"
            class="exam-group-block"
          >
            <!-- Group Header -->
            <div class="exam-group-header">
              <div class="group-header-left">
                <span class="exam-cycle-badge">{{ groupExams[0]?.exam_type || 'EXAMINATION' }}</span>
                <h2 class="exam-group-title">{{ groupName }}</h2>
              </div>
              <div class="group-header-right">
                <span class="subject-count-pill">{{ groupExams.length }} {{ groupExams.length === 1 ? 'Paper' : 'Papers' }} Scheduled</span>
              </div>
            </div>

            <!-- Exam Papers Grid -->
            <div class="papers-grid">
              <div
                v-for="exam in groupExams"
                :key="exam.id"
                class="paper-card"
              >
                <!-- Card Top: Subject & Status -->
                <div class="paper-top">
                  <div>
                    <div class="paper-subj-code">{{ exam.subject_code || 'SUBJ' }}</div>
                    <h3 class="paper-subj-name">{{ exam.subject_name || 'Subject Examination' }}</h3>
                  </div>
                  <div class="paper-status-pill">
                    <span class="live-dot" />
                    <span>PUBLISHED</span>
                  </div>
                </div>

                <!-- Schedule Details Grid -->
                <div class="paper-meta-grid">
                  <div class="meta-cell">
                    <span class="cell-label">CLASS / SECTION</span>
                    <span class="cell-val">
                      {{ exam.class_name || 'Assigned Class' }}
                      <span v-if="exam.section" class="section-tag">Section {{ exam.section }}</span>
                    </span>
                  </div>

                  <div class="meta-cell">
                    <span class="cell-label">EXAM DATE</span>
                    <span class="cell-val bold">
                      📅 {{ formatDate(exam.start_date) }}
                      <span v-if="exam.end_date && exam.end_date !== exam.start_date"> - {{ formatDate(exam.end_date) }}</span>
                    </span>
                  </div>

                  <div class="meta-cell">
                    <span class="cell-label">SESSION TIME</span>
                    <span class="cell-val">
                      ⏰ {{ exam.start_time || '08:30' }} - {{ exam.end_time || '11:30' }}
                    </span>
                  </div>

                  <div class="meta-cell">
                    <span class="cell-label">PASSING MARKS</span>
                    <span class="cell-val">
                      {{ exam.pass_marks }} / {{ exam.max_marks }} pts ({{ Math.round((exam.pass_marks / (exam.max_marks || 100)) * 100) }}%)
                    </span>
                  </div>

                  <div v-if="exam.teacher_name" class="meta-cell full-width">
                    <span class="cell-label">INVIGILATOR / TEACHER</span>
                    <span class="cell-val">👤 {{ exam.teacher_name }}</span>
                  </div>
                </div>

                <!-- Instructions -->
                <div v-if="exam.instructions" class="paper-instructions">
                  <svg class="instr-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                  </svg>
                  <p class="instr-text">{{ exam.instructions }}</p>
                </div>

                <!-- Card Bottom: Result Visibility Status -->
                <div class="paper-footer">
                  <div v-if="exam.has_released_result" class="result-released-banner">
                    <span class="rel-badge">
                      <svg class="check-sm" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                      </svg>
                      Official Result Released: Grade {{ exam.grade || 'PASS' }} ({{ exam.marks_obtained ?? '-' }} / {{ exam.total_marks }})
                    </span>
                    <button
                      type="button"
                      class="btn-view-transcript"
                      @click="switchToResults(exam.name)"
                    >
                      View Report Card &rarr;
                    </button>
                  </div>
                  <div v-else class="result-pending-banner">
                    <svg class="pending-icon" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
                    </svg>
                    <span>Schedule Published • Marks will be released by School Administration once grading is complete.</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB 2: VERIFIED RESULTS & TRANSCRIPTS -->
      <div v-else-if="activeTab === 'results'" class="results-view">
        <!-- Empty State -->
        <div v-if="results.length === 0" class="empty-state">
          <div class="empty-icon-wrap">
            <svg class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 class="empty-title">Results Are Being Processed</h3>
          <p class="empty-desc">
            No examination results have been officially released for academic year {{ selectedYear }} yet.
            Marks undergo administrative review and will appear here immediately upon official release.
          </p>
        </div>

        <div v-else class="results-content">
          <!-- Exam Selector Tabs -->
          <div v-if="Object.keys(examGroups).length > 1" class="exam-tabs-strip">
            <button
              v-for="(_, examKey) in examGroups"
              :key="examKey"
              class="exam-tab-pill"
              :class="{ active: selectedExam === examKey }"
              @click="selectExam(examKey)"
            >
              {{ examKey }}
            </button>
          </div>

          <!-- Selected Exam Report Card Banner -->
          <div class="report-card-banner">
            <div class="banner-info">
              <div class="badge-official">OFFICIALLY RELEASED &amp; VERIFIED</div>
              <h2 class="exam-headline">{{ selectedExam }}</h2>
              <span class="academic-cycle">Class Assessment Record &bull; Academic Year {{ selectedYear }}</span>
            </div>

            <!-- Big Overall GPA / Grade Badge -->
            <div v-if="examStats" class="gpa-box">
              <div class="gpa-val">{{ examStats.avgPct }}%</div>
              <div class="gpa-grade">Grade: {{ examStats.overallGrade }}</div>
            </div>
          </div>

          <!-- Stats Strip -->
          <div v-if="examStats" class="stats-strip">
            <div class="stat-box">
              <span class="stat-lbl">SUBJECTS</span>
              <span class="stat-num">{{ examStats.subjectsCount }}</span>
            </div>
            <div class="stat-box">
              <span class="stat-lbl">TOTAL SCORE</span>
              <span class="stat-num">{{ examStats.totalScore }} / {{ examStats.totalMax }}</span>
            </div>
            <div class="stat-box">
              <span class="stat-lbl">PASSED</span>
              <span class="stat-num text-success">{{ examStats.passedCount }}</span>
            </div>
            <div class="stat-box">
              <span class="stat-lbl">FAILED / ABSENT</span>
              <span class="stat-num text-danger">{{ examStats.failedCount + examStats.absentCount }}</span>
            </div>
          </div>

          <!-- Desktop Table -->
          <div class="desktop-table-wrap">
            <table class="report-table">
              <thead>
                <tr>
                  <th class="idx-col">#</th>
                  <th>SUBJECT</th>
                  <th>ATTENDANCE</th>
                  <th class="text-center">MARKS</th>
                  <th class="text-center">MAX</th>
                  <th class="text-center">PCT</th>
                  <th class="text-center">GRADE</th>
                  <th>REMARKS</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, idx) in currentExamResults" :key="row.id">
                  <td class="idx-col">{{ idx + 1 }}</td>
                  <td class="subject-col">
                    <strong>{{ row.subject_name || 'Subject' }}</strong>
                    <span v-if="row.subject_code" class="sub-code">{{ row.subject_code }}</span>
                  </td>
                  <td>
                    <span
                      class="attendance-pill"
                      :class="{
                        present: row.attendance_status === 'PRESENT',
                        absent: row.attendance_status === 'ABSENT',
                        excused: row.attendance_status === 'EXCUSED'
                      }"
                    >
                      {{ row.attendance_status }}
                    </span>
                  </td>
                  <td class="text-center score-col">
                    <span v-if="row.marks_obtained !== null">{{ row.marks_obtained }}</span>
                    <span v-else class="text-muted">-</span>
                  </td>
                  <td class="text-center max-col">{{ row.total_marks || 100 }}</td>
                  <td class="text-center pct-col">
                    <span v-if="row.percentage !== null">{{ row.percentage }}%</span>
                    <span v-else class="text-muted">-</span>
                  </td>
                  <td class="text-center">
                    <span
                      v-if="row.grade"
                      class="grade-pill"
                      :class="{
                        'grade-high': ['A+', 'A', 'B+', 'B'].includes(row.grade),
                        'grade-low': ['F'].includes(row.grade),
                        'grade-abs': ['ABSENT'].includes(row.grade)
                      }"
                    >
                      {{ row.grade }}
                    </span>
                    <span v-else class="text-muted">-</span>
                  </td>
                  <td class="remarks-col">{{ row.remarks || 'Standard Performance' }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Mobile Cards -->
          <div class="mobile-results-cards">
            <div v-for="(row, idx) in currentExamResults" :key="row.id" class="mobile-res-card">
              <div class="res-card-top">
                <span class="res-idx">#{{ idx + 1 }}</span>
                <span
                  class="attendance-pill"
                  :class="{
                    present: row.attendance_status === 'PRESENT',
                    absent: row.attendance_status === 'ABSENT',
                    excused: row.attendance_status === 'EXCUSED'
                  }"
                >
                  {{ row.attendance_status }}
                </span>
              </div>
              <h4 class="res-subj-name">{{ row.subject_name || 'Subject' }}</h4>
              <div class="res-score-row">
                <div class="res-score-item">
                  <span class="lbl">Marks</span>
                  <strong class="val">{{ row.marks_obtained !== null ? row.marks_obtained : '-' }} / {{ row.total_marks }}</strong>
                </div>
                <div class="res-score-item">
                  <span class="lbl">Percentage</span>
                  <strong class="val">{{ row.percentage !== null ? `${row.percentage}%` : '-' }}</strong>
                </div>
                <div class="res-score-item">
                  <span class="lbl">Grade</span>
                  <strong class="val">{{ row.grade || '-' }}</strong>
                </div>
              </div>
              <div v-if="row.remarks" class="res-card-remarks">
                &ldquo;{{ row.remarks }}&rdquo;
              </div>
            </div>
          </div>

          <!-- Official Delivery Receipt Footer -->
          <div class="delivery-receipt-footer">
            <svg class="check-badge-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <span>
              This is a digitally generated transcript for the authenticated student profile. Official grade certification by School Registry.
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.portal-page {
  padding: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-header {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.header-content-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-title {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 0.88rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.year-selector-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: var(--bg-surface-secondary);
  padding: 0.35rem 0.75rem;
  border-radius: 8px;
  border: 1px solid var(--border-subtle);
}

.selector-lbl {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
}

.year-select {
  background: transparent;
  border: none;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-primary);
  cursor: pointer;
  outline: none;
}

.btn-refresh {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background-color: var(--bg-surface-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-subtle);
  padding: 0.45rem 0.85rem;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-refresh:hover:not(:disabled) {
  background-color: var(--bg-surface-hover, #e2e8f0);
}

.refresh-icon {
  width: 16px;
  height: 16px;
}

.refresh-icon.spinning {
  animation: spin 0.8s linear infinite;
}

/* Tabs Navigation */
.tabs-nav {
  display: flex;
  gap: 0.5rem;
  border-bottom: 2px solid var(--border-subtle);
  padding-bottom: 0.15rem;
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1.15rem;
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--text-muted);
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  transition: all 0.15s ease;
  margin-bottom: -2px;
}

.tab-btn:hover {
  color: var(--text-primary);
}

.tab-btn.active {
  color: #2563eb;
  border-bottom-color: #2563eb;
}

.tab-icon {
  width: 18px;
  height: 18px;
}

.badge-count {
  font-size: 0.72rem;
  padding: 0.1rem 0.45rem;
  border-radius: 10px;
  background-color: var(--bg-surface-secondary);
  color: var(--text-muted);
}

.badge-count.highlight {
  background-color: rgba(37, 99, 235, 0.12);
  color: #2563eb;
}

/* Container */
.report-container {
  background: var(--bg-surface);
  border-radius: 12px;
  border: 1px solid var(--border-subtle);
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

/* Tab 1: Published Exams Schedules View */
.published-exams-wrap {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.exam-group-block {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.exam-group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-subtle);
}

.group-header-left {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.exam-cycle-badge {
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background-color: #ede9fe;
  color: #7c3aed;
  padding: 0.2rem 0.55rem;
  border-radius: 4px;
}

.exam-group-title {
  font-size: 1.2rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}

.subject-count-pill {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-muted);
  background-color: var(--bg-surface-secondary);
  padding: 0.25rem 0.65rem;
  border-radius: 6px;
}

.papers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 1.25rem;
}

.paper-card {
  background-color: var(--bg-surface-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.paper-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px -4px rgba(0, 0, 0, 0.08);
}

.paper-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
}

.paper-subj-code {
  font-size: 0.72rem;
  font-weight: 700;
  color: #2563eb;
  letter-spacing: 0.05em;
}

.paper-subj-name {
  font-size: 1.05rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0.15rem 0 0 0;
}

.paper-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.68rem;
  font-weight: 800;
  color: #059669;
  background-color: rgba(16, 185, 129, 0.15);
  padding: 0.2rem 0.55rem;
  border-radius: 12px;
  letter-spacing: 0.05em;
}

.live-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: #10b981;
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.3);
}

.paper-meta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.65rem;
  background-color: var(--bg-surface);
  padding: 0.75rem;
  border-radius: 8px;
  border: 1px solid var(--border-subtle);
}

.meta-cell {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.meta-cell.full-width {
  grid-column: span 2;
}

.cell-label {
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 0.03em;
}

.cell-val {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-primary);
}

.cell-val.bold {
  font-weight: 700;
}

.section-tag {
  display: inline-block;
  font-size: 0.68rem;
  font-weight: 700;
  color: #475569;
  background-color: #e2e8f0;
  padding: 0.05rem 0.35rem;
  border-radius: 4px;
  margin-left: 0.25rem;
}

.paper-instructions {
  display: flex;
  gap: 0.5rem;
  background-color: rgba(245, 158, 11, 0.08);
  border-left: 3px solid #f59e0b;
  padding: 0.6rem 0.75rem;
  border-radius: 4px;
}

.instr-icon {
  width: 16px;
  height: 16px;
  color: #d97706;
  flex-shrink: 0;
  margin-top: 0.1rem;
}

.instr-text {
  font-size: 0.76rem;
  color: var(--text-secondary, #475569);
  line-height: 1.4;
  margin: 0;
}

.paper-footer {
  margin-top: auto;
  padding-top: 0.5rem;
}

.result-released-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  background-color: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.3);
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
}

.rel-badge {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.78rem;
  font-weight: 700;
  color: #065f46;
}

.check-sm {
  width: 16px;
  height: 16px;
  color: #059669;
}

.btn-view-transcript {
  background-color: #059669;
  color: #fff;
  border: none;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.3rem 0.65rem;
  border-radius: 4px;
  cursor: pointer;
  white-space: nowrap;
}

.btn-view-transcript:hover {
  background-color: #047857;
}

.result-pending-banner {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.74rem;
  color: var(--text-muted);
  background-color: var(--bg-surface);
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  border: 1px dashed var(--border-subtle);
}

.pending-icon {
  width: 16px;
  height: 16px;
  color: #94a3b8;
  flex-shrink: 0;
}

/* Tab 2: Verified Results View */
.results-content {
  display: flex;
  flex-direction: column;
}

.exam-tabs-strip {
  display: flex;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  background-color: var(--bg-surface-secondary);
  border-bottom: 1px solid var(--border-subtle);
  overflow-x: auto;
}

.exam-tab-pill {
  padding: 0.45rem 1rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 700;
  background-color: var(--bg-surface);
  color: var(--text-muted);
  border: 1px solid var(--border-subtle);
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
}

.exam-tab-pill.active {
  background-color: #0f172a;
  color: #ffffff;
  border-color: #0f172a;
}

.report-card-banner {
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.05) 0%, rgba(16, 185, 129, 0.05) 100%);
  border-bottom: 1px solid var(--border-subtle);
  gap: 1rem;
}

.badge-official {
  font-size: 0.65rem;
  font-weight: 800;
  color: #10b981;
  letter-spacing: 0.05em;
  margin-bottom: 0.25rem;
}

.exam-headline {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}

.academic-cycle {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.gpa-box {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  padding: 0.75rem 1.25rem;
  border-radius: 10px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.gpa-val {
  font-size: 1.8rem;
  font-weight: 900;
  color: #10b981;
  line-height: 1;
}

.gpa-grade {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.stats-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  border-bottom: 1px solid var(--border-subtle);
  background-color: var(--bg-surface);
}

.stat-box {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  border-right: 1px solid var(--border-subtle);
}

.stat-box:last-child {
  border-right: none;
}

.stat-lbl {
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 0.05em;
}

.stat-num {
  font-size: 1.2rem;
  font-weight: 800;
  color: var(--text-primary);
}

.text-success { color: #10b981; }
.text-danger { color: #ef4444; }

/* Table */
.desktop-table-wrap {
  overflow-x: auto;
}

.report-table {
  width: 100%;
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

/* Loading & Empty States */
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
  border-top-color: #2563eb;
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
  .papers-grid {
    grid-template-columns: 1fr;
  }
}
</style>
