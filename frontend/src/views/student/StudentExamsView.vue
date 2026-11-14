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
      academic_year: sampleResult.academic_year || selectedYear.value || '2026/2027',
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
    academicYears.value = ['2026/2027'];
    selectedYear.value = '2026/2027';
  }
  await loadData();
}

onMounted(() => {
  initPage();
});
</script>

<template>
  <div class="exams-portal">
    <!-- Header -->
    <div class="page-header">
      <div class="header-main">
        <div class="header-titles">
          <div class="somroyal-tag">
            <svg class="crown-icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M5 16L3 5l5.5 5L12 4l3.5 6L21 5l-2 11H5m14 3c0 .6-.4 1-1 1H6c-.6 0-1-.4-1-1v-1h14v1z"/>
            </svg>
            <span>ACADEMIC EVALUATIONS & TRANSCRIPTS</span>
          </div>
          <h1 class="page-title">My Exams & Results</h1>
          <p class="page-subtitle">Inspect scheduled examination dates, paper schedules, and certified official academic transcripts.</p>
        </div>

        <!-- Controls: Year Selector & Refresh -->
        <div class="header-controls">
          <div v-if="academicYears.length > 0" class="year-selector-box">
            <label for="exam-year-select" class="selector-lbl">Academic Year</label>
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
            title="Refresh examination records"
            :disabled="isLoading"
            @click="loadData"
          >
            <svg class="refresh-icon" :class="{ spinning: isLoading }" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
            </svg>
            <span>Sync</span>
          </button>
        </div>
      </div>

      <!-- Somroyal Segmented Navigation Tabs -->
      <div class="tabs-bar">
        <button
          type="button"
          class="tab-pill"
          :class="{ active: activeTab === 'schedules' }"
          @click="activeTab = 'schedules'"
        >
          <svg class="tab-svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <span class="tab-text">Published Schedules</span>
          <span class="tab-counter" :class="{ highlight: publishedExams.length > 0 }">
            {{ publishedExams.length }}
          </span>
        </button>

        <button
          type="button"
          class="tab-pill"
          :class="{ active: activeTab === 'results' }"
          @click="activeTab = 'results'"
        >
          <svg class="tab-svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="tab-text">Official Transcripts</span>
          <span class="tab-counter" :class="{ highlight: results.length > 0 }">
            {{ results.length }}
          </span>
        </button>
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
        <h3 class="error-title">Unable to Load Examination Data</h3>
        <p class="error-desc">{{ errorMessage }}</p>
      </div>
      <button class="btn-retry" @click="loadData">Try Again</button>
    </div>

    <!-- Main Container -->
    <div class="exam-body-card">
      <!-- Loading State -->
      <div v-if="isLoading" class="state-container">
        <div class="spinner-ring" />
        <p class="loading-label">Loading examination records from Somroyal database...</p>
      </div>

      <!-- TAB 1: PUBLISHED EXAMS & SCHEDULES -->
      <div v-else-if="activeTab === 'schedules'" class="tab-content">
        <!-- Empty State -->
        <div v-if="publishedExams.length === 0" class="state-container empty">
          <div class="empty-icon-circle">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <h3 class="state-title">No Published Examinations Found</h3>
          <p class="state-desc">
            There are currently no examinations scheduled or published for your enrolled class in academic year {{ selectedYear }}.
            Upcoming examination dates, timetables, and subject schedules announced by school administration will appear here automatically.
          </p>
        </div>

        <!-- Published Exams List -->
        <div v-else class="exam-groups-wrapper">
          <div
            v-for="(groupExams, groupName) in publishedExamGroups"
            :key="groupName"
            class="exam-group-card"
          >
            <!-- Group Header -->
            <div class="exam-group-head">
              <div class="group-title-side">
                <span class="exam-type-pill">{{ groupExams[0]?.exam_type || 'EXAMINATION' }}</span>
                <h2 class="exam-group-heading">{{ groupName }}</h2>
              </div>
              <div class="group-meta-side">
                <span class="papers-pill">
                  <svg viewBox="0 0 20 20" fill="currentColor">
                    <path d="M9 2a2 2 0 00-2 2v8a2 2 0 002 2h6a2 2 0 002-2V6.414A2 2 0 0016.414 5L14 2.586A2 2 0 0012.586 2H9z" />
                    <path d="M3 8a2 2 0 012-2v10h8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z" />
                  </svg>
                  {{ groupExams.length }} {{ groupExams.length === 1 ? 'Subject Paper' : 'Subject Papers' }}
                </span>
              </div>
            </div>

            <!-- Exam Papers Grid -->
            <div class="papers-grid">
              <div
                v-for="exam in groupExams"
                :key="exam.id"
                class="paper-item"
              >
                <!-- Card Header -->
                <div class="paper-header">
                  <div>
                    <span class="subject-badge">{{ exam.subject_code || 'SUBJ' }}</span>
                    <h3 class="subject-name">{{ exam.subject_name || 'Subject Examination' }}</h3>
                  </div>
                  <div class="status-live-tag">
                    <span class="pulse-dot" />
                    <span>PUBLISHED</span>
                  </div>
                </div>

                <!-- Schedule Details Grid -->
                <div class="paper-details-grid">
                  <div class="detail-cell">
                    <span class="detail-label">CLASS / SECTION</span>
                    <span class="detail-value">
                      {{ exam.class_name || 'Enrolled Class' }}
                      <span v-if="exam.section" class="section-tag">Sec {{ exam.section }}</span>
                    </span>
                  </div>

                  <div class="detail-cell">
                    <span class="detail-label">EXAM DATE</span>
                    <span class="detail-value highlight-date">
                      📅 {{ formatDate(exam.start_date) }}
                      <span v-if="exam.end_date && exam.end_date !== exam.start_date"> &ndash; {{ formatDate(exam.end_date) }}</span>
                    </span>
                  </div>

                  <div class="detail-cell">
                    <span class="detail-label">SESSION TIME</span>
                    <span class="detail-value">
                      ⏰ {{ exam.start_time || '08:30' }} &ndash; {{ exam.end_time || '11:30' }}
                    </span>
                  </div>

                  <div class="detail-cell">
                    <span class="detail-label">PASSING CRITERIA</span>
                    <span class="detail-value">
                      {{ exam.pass_marks }} / {{ exam.max_marks }} pts ({{ Math.round((exam.pass_marks / (exam.max_marks || 100)) * 100) }}%)
                    </span>
                  </div>

                  <div v-if="exam.teacher_name" class="detail-cell full-span">
                    <span class="detail-label">INVIGILATOR / FACULTY</span>
                    <span class="detail-value">👨‍🏫 {{ exam.teacher_name }}</span>
                  </div>
                </div>

                <!-- Instructions -->
                <div v-if="exam.instructions" class="paper-instructions-box">
                  <svg class="info-svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                  </svg>
                  <p class="instructions-text">{{ exam.instructions }}</p>
                </div>

                <!-- Footer: Result Status -->
                <div class="paper-card-footer">
                  <div v-if="exam.has_released_result" class="result-ready-bar">
                    <span class="ready-badge">
                      <svg class="check-icon" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                      </svg>
                      Grade {{ exam.grade || 'PASS' }} ({{ exam.marks_obtained ?? '-' }} / {{ exam.total_marks }})
                    </span>
                    <button
                      type="button"
                      class="btn-view-card"
                      @click="switchToResults(exam.name)"
                    >
                      <span>View Transcript</span>
                      <svg viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" />
                      </svg>
                    </button>
                  </div>
                  <div v-else class="result-pending-bar">
                    <svg class="clock-icon" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
                    </svg>
                    <span>Schedule Published • Results will be published by Administration upon grade approval.</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB 2: VERIFIED RESULTS & TRANSCRIPTS -->
      <div v-else-if="activeTab === 'results'" class="tab-content">
        <!-- Empty State -->
        <div v-if="results.length === 0" class="state-container empty">
          <div class="empty-icon-circle">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 class="state-title">Results Are Being Processed</h3>
          <p class="state-desc">
            No examination results have been officially released for academic year {{ selectedYear }} yet.
            Marks undergo administrative verification and will appear here immediately upon official release.
          </p>
        </div>

        <div v-else class="results-wrapper">
          <!-- Exam Selector Tabs -->
          <div v-if="Object.keys(examGroups).length > 1" class="exam-pills-bar">
            <button
              v-for="(_, examKey) in examGroups"
              :key="examKey"
              class="exam-pill"
              :class="{ active: selectedExam === examKey }"
              @click="selectExam(examKey)"
            >
              {{ examKey }}
            </button>
          </div>

          <!-- Official Somroyal Certificate Banner -->
          <div class="transcript-banner">
            <div class="banner-crest">
              <div class="crest-circle">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm-2 16l-4-4 1.41-1.41L10 14.17l6.59-6.59L18 9l-8 8z"/>
                </svg>
              </div>
            </div>

            <div class="banner-body">
              <div class="verified-tag">
                <span class="tag-dot" />
                <span>OFFICIALLY RELEASED &amp; VERIFIED</span>
              </div>
              <h2 class="exam-title-text">{{ selectedExam }}</h2>
              <p class="transcript-subtext">Certified Somroyal Student Grade Transcript &bull; Academic Year {{ selectedYear }}</p>
            </div>

            <!-- Big Overall GPA / Grade Badge -->
            <div v-if="examStats" class="gpa-card">
              <div class="gpa-score">{{ examStats.avgPct }}%</div>
              <div class="gpa-badge">Grade: <strong>{{ examStats.overallGrade }}</strong></div>
            </div>
          </div>

          <!-- Performance Metric Cards (2x2 on mobile, 4 columns on desktop) -->
          <div v-if="examStats" class="exam-kpi-grid">
            <div class="kpi-card">
              <div class="kpi-icon-box blue">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
                </svg>
              </div>
              <div class="kpi-info">
                <span class="kpi-label">SUBJECTS</span>
                <span class="kpi-val">{{ examStats.subjectsCount }}</span>
              </div>
            </div>

            <div class="kpi-card">
              <div class="kpi-icon-box amber">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1.323l3.954 1.582 1.599-.8a1 1 0 01.894 1.79l-1.233.616 1.738 5.42a1 1 0 01-.285 1.05A3.989 3.989 0 0115 15a3.989 3.989 0 01-2.667-1.019 1 1 0 01-.285-1.05l1.715-5.349L11 6.477V16h2a1 1 0 110 2H7a1 1 0 110-2h2V6.477L6.237 7.582l1.715 5.349a1 1 0 01-.285 1.05A3.989 3.989 0 015 15a3.989 3.989 0 01-2.667-1.019 1 1 0 01-.285-1.05l1.738-5.42-1.233-.617a1 1 0 01.894-1.788l1.599.799L9 4.323V3a1 1 0 011-1z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="kpi-info">
                <span class="kpi-label">TOTAL SCORE</span>
                <span class="kpi-val">{{ examStats.totalScore }} / {{ examStats.totalMax }}</span>
              </div>
            </div>

            <div class="kpi-card">
              <div class="kpi-icon-box emerald">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="kpi-info">
                <span class="kpi-label">PASSED</span>
                <span class="kpi-val text-emerald">{{ examStats.passedCount }}</span>
              </div>
            </div>

            <div class="kpi-card">
              <div class="kpi-icon-box rose">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="kpi-info">
                <span class="kpi-label">FAILED / ABSENT</span>
                <span class="kpi-val text-rose">{{ examStats.failedCount + examStats.absentCount }}</span>
              </div>
            </div>
          </div>

          <!-- Desktop Table View -->
          <div class="table-container">
            <table class="somroyal-table">
              <thead>
                <tr>
                  <th class="w-idx">#</th>
                  <th>SUBJECT</th>
                  <th>ATTENDANCE</th>
                  <th class="text-center">MARKS</th>
                  <th class="text-center">TOTAL</th>
                  <th class="text-center">PCT</th>
                  <th class="text-center">GRADE</th>
                  <th>FACULTY REMARKS</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, idx) in currentExamResults" :key="row.id">
                  <td class="w-idx text-muted">{{ idx + 1 }}</td>
                  <td>
                    <div class="subj-cell">
                      <strong class="subj-cell-name">{{ row.subject_name || 'Subject' }}</strong>
                      <span v-if="row.subject_code" class="subj-cell-code">{{ row.subject_code }}</span>
                    </div>
                  </td>
                  <td>
                    <span
                      class="att-pill"
                      :class="{
                        present: row.attendance_status === 'PRESENT',
                        absent: row.attendance_status === 'ABSENT',
                        excused: row.attendance_status === 'EXCUSED'
                      }"
                    >
                      <span class="att-dot" />
                      <span>{{ row.attendance_status }}</span>
                    </span>
                  </td>
                  <td class="text-center score-cell">
                    <span v-if="row.marks_obtained !== null" class="score-num">{{ row.marks_obtained }}</span>
                    <span v-else class="text-muted">&ndash;</span>
                  </td>
                  <td class="text-center text-muted">{{ row.total_marks || 100 }}</td>
                  <td class="text-center pct-cell">
                    <span v-if="row.percentage !== null" class="pct-num">{{ row.percentage }}%</span>
                    <span v-else class="text-muted">&ndash;</span>
                  </td>
                  <td class="text-center">
                    <span
                      v-if="row.grade"
                      class="grade-pill"
                      :class="{
                        'grade-high': ['A+', 'A', 'B+', 'B'].includes(row.grade),
                        'grade-pass': ['C+', 'C', 'D'].includes(row.grade),
                        'grade-fail': ['F'].includes(row.grade),
                        'grade-abs': ['ABSENT'].includes(row.grade)
                      }"
                    >
                      {{ row.grade }}
                    </span>
                    <span v-else class="text-muted">&ndash;</span>
                  </td>
                  <td class="remarks-cell">
                    <span class="remarks-text">{{ row.remarks || 'Standard Performance' }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Mobile Cards View (Hidden on desktop, shown on mobile/tablet) -->
          <div class="mobile-results-list">
            <div
              v-for="(row, idx) in currentExamResults"
              :key="row.id"
              class="mobile-result-card"
            >
              <div class="m-card-header">
                <div class="m-idx-subj">
                  <span class="m-idx">#{{ idx + 1 }}</span>
                  <div>
                    <h4 class="m-subj-title">{{ row.subject_name || 'Subject' }}</h4>
                    <span v-if="row.subject_code" class="m-subj-code">{{ row.subject_code }}</span>
                  </div>
                </div>
                <span
                  class="att-pill sm"
                  :class="{
                    present: row.attendance_status === 'PRESENT',
                    absent: row.attendance_status === 'ABSENT',
                    excused: row.attendance_status === 'EXCUSED'
                  }"
                >
                  <span class="att-dot" />
                  <span>{{ row.attendance_status }}</span>
                </span>
              </div>

              <!-- 3-box score strip -->
              <div class="m-score-strip">
                <div class="m-score-box">
                  <span class="m-box-lbl">Marks</span>
                  <span class="m-box-val">{{ row.marks_obtained !== null ? row.marks_obtained : '-' }} / {{ row.total_marks }}</span>
                </div>
                <div class="m-score-box">
                  <span class="m-box-lbl">Percentage</span>
                  <span class="m-box-val">{{ row.percentage !== null ? `${row.percentage}%` : '-' }}</span>
                </div>
                <div class="m-score-box">
                  <span class="m-box-lbl">Grade</span>
                  <span
                    class="grade-pill sm"
                    :class="{
                      'grade-high': ['A+', 'A', 'B+', 'B'].includes(row.grade || ''),
                      'grade-pass': ['C+', 'C', 'D'].includes(row.grade || ''),
                      'grade-fail': ['F'].includes(row.grade || ''),
                      'grade-abs': ['ABSENT'].includes(row.grade || '')
                    }"
                  >
                    {{ row.grade || '-' }}
                  </span>
                </div>
              </div>

              <div v-if="row.remarks" class="m-remarks-box">
                <svg class="quote-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M18 13V5a2 2 0 00-2-2H4a2 2 0 00-2 2v8a2 2 0 002 2h3l3 3 3-3h3a2 2 0 002-2zM5 7a1 1 0 011-1h8a1 1 0 110 2H6a1 1 0 01-1-1zm1 3a1 1 0 000 2h3a1 1 0 100-2H6z" clip-rule="evenodd" />
                </svg>
                <span>{{ row.remarks }}</span>
              </div>
            </div>
          </div>

          <!-- Official Delivery Verification Footer -->
          <div class="verification-footer">
            <div class="footer-seal">
              <svg viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="footer-text">
              <strong>Somroyal Institutional Grade Certification</strong>
              <span>This is an official, digitally generated student transcript verified by the Office of the Registrar. Any alterations render this document invalid.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.exams-portal {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

/* Page Header */
.page-header {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.header-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1.25rem;
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
  letter-spacing: -0.02em;
  margin: 0;
}

.page-subtitle {
  font-size: 0.88rem;
  color: #64748B;
  margin-top: 0.25rem;
  line-height: 1.5;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.year-selector-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  padding: 0.35rem 0.75rem;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.selector-lbl {
  font-size: 0.72rem;
  font-weight: 700;
  color: #64748B;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.year-select {
  background: transparent;
  border: none;
  font-size: 0.85rem;
  font-weight: 700;
  color: #0A192F;
  cursor: pointer;
  outline: none;
}

.btn-refresh {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: #FFFFFF;
  color: #0A192F;
  border: 1px solid #E2E8F0;
  padding: 0.5rem 0.85rem;
  border-radius: 10px;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.btn-refresh:hover:not(:disabled) {
  border-color: #1E3A8A;
  color: #1E3A8A;
  background: #EFF6FF;
}

.refresh-icon {
  width: 15px;
  height: 15px;
}

.refresh-icon.spinning {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Tabs Bar */
.tabs-bar {
  display: flex;
  gap: 0.5rem;
  background: #E2E8F0;
  padding: 0.25rem;
  border-radius: 12px;
  width: fit-content;
}

.tab-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.15rem;
  font-size: 0.86rem;
  font-weight: 700;
  color: #64748B;
  background: transparent;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-pill:hover {
  color: #0A192F;
}

.tab-pill.active {
  background: #FFFFFF;
  color: #0A192F;
  box-shadow: 0 2px 6px rgba(10, 25, 47, 0.08);
}

.tab-svg {
  width: 17px;
  height: 17px;
}

.tab-counter {
  font-size: 0.72rem;
  padding: 0.1rem 0.45rem;
  border-radius: 8px;
  background: #F1F5F9;
  color: #64748B;
}

.tab-pill.active .tab-counter.highlight {
  background: #ECFDF5;
  color: #059669;
  font-weight: 800;
}

/* Error Banner */
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

.error-icon-box svg {
  width: 20px;
  height: 20px;
}

.error-details {
  flex: 1;
}

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

/* Exam Body Card */
.exam-body-card {
  background: #FFFFFF;
  border-radius: 16px;
  border: 1px solid #E2E8F0;
  box-shadow: 0 4px 12px rgba(10, 25, 47, 0.04);
  overflow: hidden;
}

/* Loading & Empty States */
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

.empty-icon-circle svg {
  width: 28px;
  height: 28px;
}

.state-title {
  font-size: 1.15rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
}

.state-desc {
  font-size: 0.86rem;
  color: #64748B;
  max-width: 520px;
  line-height: 1.55;
  margin: 0;
}

/* Tab 1: Schedules */
.tab-content {
  padding: 1.5rem;
}

.exam-groups-wrapper {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.exam-group-card {
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
}

.exam-group-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding-bottom: 0.85rem;
  border-bottom: 2px solid #F1F5F9;
}

.group-title-side {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.exam-type-pill {
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  background: #0A192F;
  color: #FFFFFF;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
}

.exam-group-heading {
  font-size: 1.2rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
}

.papers-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.78rem;
  font-weight: 700;
  color: #059669;
  background: #ECFDF5;
  border: 1px solid #A7F3D0;
  padding: 0.3rem 0.7rem;
  border-radius: 20px;
}

.papers-pill svg {
  width: 14px;
  height: 14px;
}

/* Papers Grid */
.papers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.25rem;
}

.paper-item {
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 14px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  transition: all 0.2s ease;
}

.paper-item:hover {
  border-color: #CBD5E1;
  box-shadow: 0 4px 14px rgba(10, 25, 47, 0.05);
}

.paper-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
}

.subject-badge {
  font-size: 0.7rem;
  font-weight: 800;
  color: #2563EB;
  background: #EFF6FF;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  display: inline-block;
  margin-bottom: 0.35rem;
}

.subject-name {
  font-size: 1.05rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
}

.status-live-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.68rem;
  font-weight: 800;
  color: #059669;
  background: #ECFDF5;
  border: 1px solid #A7F3D0;
  padding: 0.2rem 0.55rem;
  border-radius: 20px;
  letter-spacing: 0.05em;
}

.pulse-dot {
  width: 6px;
  height: 6px;
  background: #10B981;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.85); }
}

.paper-details-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  background: #FFFFFF;
  padding: 0.85rem;
  border-radius: 10px;
  border: 1px solid #E2E8F0;
}

.detail-cell {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.detail-cell.full-span {
  grid-column: span 2;
  padding-top: 0.35rem;
  border-top: 1px dashed #E2E8F0;
}

.detail-label {
  font-size: 0.65rem;
  font-weight: 700;
  color: #94A3B8;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.detail-value {
  font-size: 0.84rem;
  font-weight: 700;
  color: #1E293B;
}

.detail-value.highlight-date {
  color: #0A192F;
}

.section-tag {
  font-size: 0.7rem;
  background: #F1F5F9;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  color: #475569;
  margin-left: 0.25rem;
}

.paper-instructions-box {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  background: #EFF6FF;
  border-left: 3px solid #3B82F6;
  padding: 0.6rem 0.75rem;
  border-radius: 6px;
}

.info-svg {
  width: 16px;
  height: 16px;
  color: #3B82F6;
  flex-shrink: 0;
  margin-top: 0.1rem;
}

.instructions-text {
  font-size: 0.78rem;
  color: #1E3A8A;
  margin: 0;
  line-height: 1.4;
}

.paper-card-footer {
  margin-top: auto;
  padding-top: 0.5rem;
}

.result-ready-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  background: #ECFDF5;
  border: 1px solid #A7F3D0;
  padding: 0.55rem 0.75rem;
  border-radius: 10px;
}

.ready-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8rem;
  font-weight: 700;
  color: #065F46;
}

.check-icon {
  width: 15px;
  height: 15px;
  color: #10B981;
}

.btn-view-card {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  background: #059669;
  color: #FFFFFF;
  border: none;
  padding: 0.35rem 0.65rem;
  border-radius: 6px;
  font-size: 0.76rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-view-card svg {
  width: 13px;
  height: 13px;
}

.btn-view-card:hover {
  background: #047857;
}

.result-pending-bar {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.75rem;
  color: #64748B;
  background: #F1F5F9;
  padding: 0.55rem 0.75rem;
  border-radius: 8px;
  line-height: 1.35;
}

.clock-icon {
  width: 15px;
  height: 15px;
  color: #94A3B8;
  flex-shrink: 0;
}

/* Tab 2: Results */
.results-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.exam-pills-bar {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #E2E8F0;
}

.exam-pill {
  font-size: 0.82rem;
  font-weight: 700;
  padding: 0.45rem 0.95rem;
  border-radius: 8px;
  border: 1px solid #E2E8F0;
  background: #F8FAFC;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s ease;
}

.exam-pill:hover {
  border-color: #CBD5E1;
  color: #0A192F;
}

.exam-pill.active {
  background: #0A192F;
  color: #FFFFFF;
  border-color: #0A192F;
}

/* Official Somroyal Transcript Banner */
.transcript-banner {
  background: linear-gradient(135deg, #0A192F 0%, #0F2A4A 60%, #081528 100%);
  border-radius: 16px;
  padding: 1.75rem 2rem;
  color: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 10px 25px -5px rgba(10, 25, 47, 0.25);
  position: relative;
  overflow: hidden;
}

.transcript-banner::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 300px;
  background: radial-gradient(circle at right, rgba(16, 185, 129, 0.15) 0%, transparent 70%);
  pointer-events: none;
}

.banner-crest {
  flex-shrink: 0;
}

.crest-circle {
  width: 52px;
  height: 52px;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #10B981;
}

.crest-circle svg {
  width: 28px;
  height: 28px;
}

.banner-body {
  flex: 1;
  min-width: 240px;
}

.verified-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #10B981;
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.25);
  padding: 0.2rem 0.55rem;
  border-radius: 20px;
  margin-bottom: 0.5rem;
}

.tag-dot {
  width: 6px;
  height: 6px;
  background: #10B981;
  border-radius: 50%;
}

.exam-title-text {
  font-size: 1.45rem;
  font-weight: 800;
  letter-spacing: -0.01em;
  margin: 0;
  color: #FFFFFF;
}

.transcript-subtext {
  font-size: 0.84rem;
  color: #94A3B8;
  margin-top: 0.35rem;
}

.gpa-card {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 14px;
  padding: 0.85rem 1.5rem;
  text-align: center;
  backdrop-filter: blur(8px);
}

.gpa-score {
  font-size: 2.2rem;
  font-weight: 900;
  color: #FFFFFF;
  line-height: 1;
}

.gpa-badge {
  font-size: 0.78rem;
  color: #E2E8F0;
  margin-top: 0.35rem;
}

.gpa-badge strong {
  color: #F59E0B;
  font-size: 0.92rem;
}

/* KPI Cards Strip */
.exam-kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.kpi-card {
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 1rem 1.15rem;
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.kpi-icon-box {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kpi-icon-box svg {
  width: 20px;
  height: 20px;
}

.kpi-icon-box.blue {
  background: #EFF6FF;
  color: #2563EB;
}

.kpi-icon-box.amber {
  background: #FEF3C7;
  color: #D97706;
}

.kpi-icon-box.emerald {
  background: #ECFDF5;
  color: #059669;
}

.kpi-icon-box.rose {
  background: #FEF2F2;
  color: #DC2626;
}

.kpi-info {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.kpi-label {
  font-size: 0.68rem;
  font-weight: 700;
  color: #64748B;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.kpi-val {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0A192F;
}

.text-emerald {
  color: #059669 !important;
}

.text-rose {
  color: #DC2626 !important;
}

/* Desktop Results Table */
.table-container {
  overflow-x: auto;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
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

.w-idx {
  width: 44px;
}

.subj-cell {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.subj-cell-name {
  font-weight: 700;
  color: #0A192F;
}

.subj-cell-code {
  font-size: 0.72rem;
  color: #64748B;
}

.att-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.74rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 20px;
}

.att-pill.sm {
  font-size: 0.7rem;
  padding: 0.15rem 0.45rem;
}

.att-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.att-pill.present {
  background: #ECFDF5;
  color: #065F46;
}
.att-pill.present .att-dot {
  background: #10B981;
}

.att-pill.absent {
  background: #FEF2F2;
  color: #991B1B;
}
.att-pill.absent .att-dot {
  background: #EF4444;
}

.att-pill.excused {
  background: #FEF3C7;
  color: #92400E;
}
.att-pill.excused .att-dot {
  background: #F59E0B;
}

.score-num {
  font-weight: 800;
  color: #0A192F;
  font-size: 0.95rem;
}

.pct-num {
  font-weight: 700;
  color: #059669;
}

.grade-pill {
  display: inline-block;
  font-size: 0.8rem;
  font-weight: 800;
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
  min-width: 32px;
  text-align: center;
}

.grade-pill.sm {
  font-size: 0.75rem;
  padding: 0.15rem 0.45rem;
}

.grade-pill.grade-high {
  background: #ECFDF5;
  color: #065F46;
  border: 1px solid #A7F3D0;
}

.grade-pill.grade-pass {
  background: #EFF6FF;
  color: #1E40AF;
  border: 1px solid #BFDBFE;
}

.grade-pill.grade-fail {
  background: #FEF2F2;
  color: #991B1B;
  border: 1px solid #FECACA;
}

.grade-pill.grade-abs {
  background: #F1F5F9;
  color: #64748B;
  border: 1px solid #E2E8F0;
}

.remarks-text {
  font-size: 0.8rem;
  color: #64748B;
  font-style: italic;
}

/* Mobile Results Cards */
.mobile-results-list {
  display: none;
  flex-direction: column;
  gap: 1rem;
}

.mobile-result-card {
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.m-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
}

.m-idx-subj {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.m-idx {
  font-size: 0.75rem;
  font-weight: 700;
  color: #94A3B8;
  padding-top: 0.15rem;
}

.m-subj-title {
  font-size: 0.98rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
}

.m-subj-code {
  font-size: 0.7rem;
  color: #64748B;
}

.m-score-strip {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  padding: 0.65rem;
  text-align: center;
}

.m-score-box {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.m-box-lbl {
  font-size: 0.65rem;
  font-weight: 700;
  color: #94A3B8;
  text-transform: uppercase;
}

.m-box-val {
  font-size: 0.88rem;
  font-weight: 800;
  color: #0A192F;
}

.m-remarks-box {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.76rem;
  color: #64748B;
  font-style: italic;
  padding: 0.4rem 0.6rem;
  background: #F1F5F9;
  border-radius: 6px;
}

.quote-icon {
  width: 14px;
  height: 14px;
  color: #94A3B8;
  flex-shrink: 0;
}

/* Verification Footer */
.verification-footer {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 1rem 1.25rem;
}

.footer-seal {
  width: 38px;
  height: 38px;
  background: #ECFDF5;
  border: 1px solid #A7F3D0;
  color: #059669;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.footer-seal svg {
  width: 22px;
  height: 22px;
}

.footer-text {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.footer-text strong {
  font-size: 0.82rem;
  color: #0A192F;
}

.footer-text span {
  font-size: 0.74rem;
  color: #64748B;
  line-height: 1.4;
}

/* Responsive Breakpoints */
@media (max-width: 900px) {
  .exam-kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .header-main {
    flex-direction: column;
    align-items: stretch;
  }

  .header-controls {
    justify-content: space-between;
  }

  .tabs-bar {
    width: 100%;
  }

  .tab-pill {
    flex: 1;
    justify-content: center;
  }

  .transcript-banner {
    flex-direction: column;
    align-items: stretch;
    text-align: left;
    padding: 1.5rem;
  }

  .banner-crest {
    display: none;
  }

  .gpa-card {
    text-align: center;
  }

  .table-container {
    display: none;
  }

  .mobile-results-list {
    display: flex;
  }

  .papers-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .exam-kpi-grid {
    grid-template-columns: 1fr;
  }

  .verification-footer {
    flex-direction: column;
    align-items: flex-start;
    text-align: left;
  }
}
</style>
