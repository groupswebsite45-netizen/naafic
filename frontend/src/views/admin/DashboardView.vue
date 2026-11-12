<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { adminService } from '../../services/adminService';
import { examService } from '../../services/examService';
import { classService } from '../../services/classService';
import { resultWorkflowService } from '../../services/resultWorkflowService';
import { DashboardOverview } from '../../types/admin';
import { Exam, SchoolClass } from '../../types/school';

// Component Imports
import DashboardHero from './dashboard/components/DashboardHero.vue';
import StatCard from './dashboard/components/StatCard.vue';
import StudentLevelWidget from './dashboard/components/StudentLevelWidget.vue';
import FeesWidget from './dashboard/components/FeesWidget.vue';
import ResultsProgressWidget from './dashboard/components/ResultsProgressWidget.vue';
import RecentActivityWidget from './dashboard/components/RecentActivityWidget.vue';
import QuickActionsWidget from './dashboard/components/QuickActionsWidget.vue';
import { useSchoolBrandingStore } from '../../stores/schoolBranding';
import { useI18n } from '../../i18n';

const { t } = useI18n();
const brandingStore = useSchoolBrandingStore();

// Reactive State
const overview = ref<DashboardOverview | null>(null);
const upcomingExams = ref<Exam[]>([]);
const classesList = ref<SchoolClass[]>([]);
const resultsOverview = ref<any>(null);

const selectedAcademicYear = ref<string>('2026/2027');
const availableAcademicYears = ref<string[]>(['2026/2027', '2025/2026']);

const isLoading = ref<boolean>(false);
const fetchError = ref<string | null>(null);

// Metric calculations
const totalStudentsCount = computed(() => {
  return overview.value?.metrics?.total_students ?? 0;
});

const totalTeachersCount = computed(() => {
  return overview.value?.metrics?.total_teachers ?? 0;
});

const totalClassesCount = computed(() => {
  return overview.value?.metrics?.total_classes ?? 0;
});

const totalSubjectsCount = computed(() => {
  return overview.value?.metrics?.total_subjects ?? 0;
});

const upcomingExamsCount = computed(() => {
  return overview.value?.metrics?.upcoming_exams_count ?? upcomingExams.value?.length ?? 0;
});

const todayClassesCount = computed(() => {
  return overview.value?.metrics?.today_timetable_count ?? 0;
});

const feesCollectedFormatted = computed(() => {
  const val = overview.value?.metrics?.total_fees_collected ?? 0;
  return `$${Number(val).toFixed(2)}`;
});

const feesOutstandingFormatted = computed(() => {
  const val = overview.value?.metrics?.total_fees_outstanding ?? 0;
  return `$${Number(val).toFixed(2)}`;
});

async function loadDashboardData() {
  isLoading.value = true;
  fetchError.value = null;

  try {
    const [overviewRes, examsRes, classesRes, resultFiltersRes] = await Promise.allSettled([
      adminService.getDashboardOverview(),
      examService.getExams({ limit: 10 }),
      classService.getClasses(),
      resultWorkflowService.getFilterOptions(),
    ]);

    if (overviewRes.status === 'fulfilled') {
      overview.value = overviewRes.value;
      if ((overviewRes.value as any).school) {
        brandingStore.setLiveSchoolInfo((overviewRes.value as any).school);
      }
    }

    if (examsRes.status === 'fulfilled' && Array.isArray(examsRes.value)) {
      upcomingExams.value = examsRes.value;
    }

    if (classesRes.status === 'fulfilled' && Array.isArray(classesRes.value)) {
      classesList.value = classesRes.value;
    }

    if (resultFiltersRes.status === 'fulfilled' && resultFiltersRes.value) {
      if (resultFiltersRes.value.academic_years?.length) {
        availableAcademicYears.value = Array.from(new Set(resultFiltersRes.value.academic_years));
      }
    }
  } catch (err: any) {
    // Keep UI gracefully displayed with verified default state
    console.warn('Dashboard live telemetry fetch warning:', err);
  } finally {
    isLoading.value = false;
  }
}

function handleYearChange(newYear: string) {
  selectedAcademicYear.value = newYear;
}

onMounted(() => {
  loadDashboardData();
});
</script>

<template>
  <div class="dashboard-viewport">
    
    <!-- 1. Top Hero Welcome Banner Card -->
    <DashboardHero
      :admin-name="brandingStore.adminName"
      :school-name="brandingStore.schoolName"
      :school-code="brandingStore.schoolCode"
      :academic-year="selectedAcademicYear"
      :academic-years="availableAcademicYears"
      @update:academic-year="handleYearChange"
    />

    <!-- 2. Primary KPI Stats Row (4 Cards) -->
    <section class="kpi-grid primary-kpi-grid" aria-label="Primary Key Performance Indicators">
      <StatCard
        :title="t('dashboard.totalStudents')"
        :value="totalStudentsCount"
        :trend-badge="totalStudentsCount > 0 ? 'Active' : 'Zero Records'"
        :subtext="`${totalStudentsCount} Enrolled Students`"
        icon-variant="blue"
        :loading="isLoading"
      />

      <StatCard
        :title="t('dashboard.totalTeachers')"
        :value="totalTeachersCount"
        :trend-badge="totalTeachersCount > 0 ? 'Active' : 'Zero Records'"
        :subtext="`${totalTeachersCount} Active Faculty`"
        icon-variant="green"
        :loading="isLoading"
      />

      <StatCard
        :title="t('dashboard.totalClasses')"
        :value="totalClassesCount"
        :trend-badge="totalClassesCount > 0 ? 'Active' : 'Zero Records'"
        :subtext="`${totalClassesCount} Grade Levels & Sections`"
        icon-variant="purple"
        :loading="isLoading"
      />

      <StatCard
        :title="t('dashboard.totalSubjects')"
        :value="totalSubjectsCount"
        :trend-badge="totalSubjectsCount > 0 ? 'Active' : 'Zero Records'"
        :subtext="`${totalSubjectsCount} Curriculum Subjects`"
        icon-variant="orange"
        :loading="isLoading"
      />
    </section>

    <!-- 3. Secondary Operational KPI Row (4 Cards) -->
    <section class="kpi-grid secondary-kpi-grid" aria-label="Operational Key Performance Indicators">
      <StatCard
        title="Today's Classes"
        :value="todayClassesCount"
        subtext="Scheduled Class Periods"
        icon-variant="amber"
        :has-chevron="true"
        :loading="isLoading"
      />

      <StatCard
        title="Upcoming Exams"
        :value="upcomingExamsCount"
        subtext="Scheduled Assessments"
        icon-variant="red"
        :has-chevron="true"
        :loading="isLoading"
      />

      <StatCard
        title="Fees Collected"
        :value="feesCollectedFormatted"
        subtext="Recorded Realized Payments"
        icon-variant="emerald"
        :has-chevron="true"
        :loading="isLoading"
      />

      <StatCard
        title="Outstanding Fees"
        :value="feesOutstandingFormatted"
        subtext="Total Unpaid Student Balances"
        icon-variant="purple"
        :has-chevron="true"
        :loading="isLoading"
      />
    </section>

    <!-- 4. Analytics & Visualization Row (3 Cards Grid) -->
    <section class="analytics-3col-grid" aria-label="Analytics and Performance Charts">
      <!-- Card 1: Student Enrollment Overview Donut Chart -->
      <StudentLevelWidget
        :total-students="totalStudentsCount"
        :primary-count="totalStudentsCount"
        :secondary-count="0"
        :others-count="0"
        :loading="isLoading"
      />

      <!-- Card 2: Fees & Revenue Overview Monthly Bar Chart -->
      <FeesWidget
        :billed="overview?.metrics?.total_fees_billed ?? 0"
        :collected="overview?.metrics?.total_fees_collected ?? 0"
        :outstanding="overview?.metrics?.total_fees_outstanding ?? 0"
        :loading="isLoading"
      />

      <!-- Card 3: Academic Performance Radial Gauge Chart -->
      <ResultsProgressWidget
        :results-data="resultsOverview"
        :loading="isLoading"
      />
    </section>

    <!-- 5. Bottom Section (2 Columns: Recent Activities & Quick Actions) -->
    <section class="bottom-2col-grid" aria-label="Recent Activities and Quick Actions">
      <!-- Left: Recent Activities -->
      <RecentActivityWidget
        :logs="overview?.recent_activity"
        :loading="isLoading"
      />

      <!-- Right: Quick Actions -->
      <QuickActionsWidget />
    </section>

  </div>
</template>

<style scoped>
.dashboard-viewport {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
  max-width: 1440px;
  margin: 0 auto;
  box-sizing: border-box;
}

/* 4-Card Grid for Primary and Secondary KPIs */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1.25rem;
}

/* 3-Column Grid for Analytics Row */
.analytics-3col-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.25rem;
}

/* 2-Column Grid for Bottom Section */
.bottom-2col-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1.25rem;
}

/* Responsive Breakpoints */
@media (max-width: 1360px) {
  .analytics-3col-grid {
    grid-template-columns: 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem;
  }
  .bottom-2col-grid {
    grid-template-columns: 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 580px) {
  .dashboard-viewport {
    gap: 1rem;
  }
  .kpi-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.65rem;
  }
}
</style>
