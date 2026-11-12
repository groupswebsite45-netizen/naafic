<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { teacherPortalService } from '../../services/teacherPortalService';
import { TeacherClassDetailResponse } from '../../types/portal';
import { TeacherAssignment } from '../../types/school';
import StatusBadge from '../../components/common/StatusBadge.vue';

const router = useRouter();
const assignments = ref<TeacherAssignment[]>([]);
const isLoading = ref(true);
const errorMessage = ref('');

// Filters & Search
const searchQuery = ref('');
const selectedYear = ref<string>('ALL');
const selectedClass = ref<string>('ALL');
const selectedSubject = ref<string>('ALL');
const selectedStatus = ref<string>('ALL');

// Class Detail Modal
const isDetailModalOpen = ref(false);
const isLoadingDetail = ref(false);
const selectedAssignment = ref<TeacherAssignment | null>(null);
const classDetail = ref<TeacherClassDetailResponse | null>(null);
const activeDetailTab = ref<'students' | 'timetable' | 'exams'>('students');
const studentSearchQuery = ref('');

async function loadData() {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    const list = await teacherPortalService.getMyClasses();
    assignments.value = list;

    // Auto-select active academic year if present and not already customized
    if (selectedYear.value === 'ALL' && list.length > 0) {
      const activeAssignment = list.find((a) => a.is_current_academic_year || a.display_status === 'ACTIVE');
      if (activeAssignment) {
        selectedYear.value = activeAssignment.academic_year;
      }
    }
  } catch (err: any) {
    errorMessage.value =
      err.response?.data?.error?.message ||
      err.response?.data?.detail ||
      'Unable to load your assigned classes and subjects.';
  } finally {
    isLoading.value = false;
  }
}

// Dynamic Filter Options strictly generated from teacher's assignments
const availableYears = computed(() => {
  return Array.from(new Set(assignments.value.map((a) => a.academic_year)))
    .filter(Boolean)
    .sort()
    .reverse();
});

const availableClassNames = computed(() => {
  let filtered = assignments.value;
  if (selectedYear.value !== 'ALL') {
    filtered = filtered.filter((a) => a.academic_year === selectedYear.value);
  }
  return Array.from(new Set(filtered.map((a) => a.class_name || a.school_class?.name || `Class ${a.class_id}`)))
    .filter(Boolean)
    .sort();
});

const availableSubjectNames = computed(() => {
  let filtered = assignments.value;
  if (selectedYear.value !== 'ALL') {
    filtered = filtered.filter((a) => a.academic_year === selectedYear.value);
  }
  if (selectedClass.value !== 'ALL') {
    filtered = filtered.filter(
      (a) => (a.class_name || a.school_class?.name || `Class ${a.class_id}`) === selectedClass.value
    );
  }
  return Array.from(new Set(filtered.map((a) => a.subject_name || a.subject?.name || `Subject ${a.subject_id}`)))
    .filter(Boolean)
    .sort();
});

const filteredAssignments = computed(() => {
  return assignments.value.filter((a) => {
    const className = a.class_name || a.school_class?.name || `Class ${a.class_id}`;
    const subjectName = a.subject_name || a.subject?.name || `Subject ${a.subject_id}`;
    const subjectCode = a.subject_code || a.subject?.code || '';
    const classCode = a.class_code || a.school_class?.code || '';
    const status = a.display_status || (a.is_current_academic_year ? 'ACTIVE' : 'HISTORICAL');

    // Year filter
    if (selectedYear.value !== 'ALL' && a.academic_year !== selectedYear.value) return false;

    // Class filter
    if (selectedClass.value !== 'ALL' && className !== selectedClass.value) return false;

    // Subject filter
    if (selectedSubject.value !== 'ALL' && subjectName !== selectedSubject.value) return false;

    // Status filter
    if (selectedStatus.value !== 'ALL' && status !== selectedStatus.value) return false;

    // Text Search
    if (searchQuery.value.trim()) {
      const q = searchQuery.value.toLowerCase().trim();
      const matchName = subjectName.toLowerCase().includes(q);
      const matchCode = subjectCode.toLowerCase().includes(q);
      const matchClass = className.toLowerCase().includes(q);
      const matchClassCode = classCode.toLowerCase().includes(q);
      const matchDept = (a.department || a.subject?.department || '').toLowerCase().includes(q);
      if (!matchName && !matchCode && !matchClass && !matchClassCode && !matchDept) return false;
    }

    return true;
  });
});

const isFiltered = computed(() => {
  return (
    selectedYear.value !== 'ALL' ||
    selectedClass.value !== 'ALL' ||
    selectedSubject.value !== 'ALL' ||
    selectedStatus.value !== 'ALL' ||
    searchQuery.value.trim() !== ''
  );
});

function resetFilters() {
  selectedYear.value = 'ALL';
  selectedClass.value = 'ALL';
  selectedSubject.value = 'ALL';
  selectedStatus.value = 'ALL';
  searchQuery.value = '';
}

// Summary Metrics Computed strictly from teacher's assignments
const totalAssignedStreams = computed(() => assignments.value.length);
const totalUniqueClasses = computed(() => {
  return new Set(assignments.value.map((a) => a.class_id)).size;
});
const totalUniqueSubjects = computed(() => {
  return new Set(assignments.value.map((a) => a.subject_id)).size;
});
const totalStudentsEnrolled = computed(() => {
  const mapByClass = new Map<number, number>();
  for (const a of assignments.value) {
    if (!mapByClass.has(a.class_id)) {
      mapByClass.set(a.class_id, a.student_count || 0);
    }
  }
  return Array.from(mapByClass.values()).reduce((sum, count) => sum + count, 0);
});

// Class Detail Modal
async function openClassDetail(assignment: TeacherAssignment) {
  selectedAssignment.value = assignment;
  isDetailModalOpen.value = true;
  isLoadingDetail.value = true;
  activeDetailTab.value = 'students';
  studentSearchQuery.value = '';
  try {
    const detail = await teacherPortalService.getClassDetail(assignment.class_id);
    classDetail.value = detail;
  } catch (err: any) {
    errorMessage.value =
      err.response?.data?.error?.message ||
      err.response?.data?.detail ||
      'Failed to load class profile details.';
    isDetailModalOpen.value = false;
  } finally {
    isLoadingDetail.value = false;
  }
}

const filteredModalStudents = computed(() => {
  if (!classDetail.value?.students) return [];
  if (!studentSearchQuery.value.trim()) return classDetail.value.students;
  const q = studentSearchQuery.value.toLowerCase().trim();
  return classDetail.value.students.filter((s) => {
    const fullName = `${s.first_name} ${s.middle_name || ''} ${s.last_name}`.toLowerCase();
    const adm = s.admission_number.toLowerCase();
    return fullName.includes(q) || adm.includes(q);
  });
});

// Routing to workflows with actual assignment context
function navigateToAttendance(a: TeacherAssignment) {
  router.push({
    path: '/teacher/attendance',
    query: {
      class_id: a.class_id,
      subject_id: a.subject_id,
      academic_year: a.academic_year,
    },
  });
}

function navigateToExams(a: TeacherAssignment) {
  router.push({
    path: '/teacher/exams',
    query: {
      class_id: a.class_id,
      subject_id: a.subject_id,
      academic_year: a.academic_year,
      class_name: a.class_name || a.school_class?.name,
      subject_name: a.subject_name || a.subject?.name,
    },
  });
}

// Subject Icon & Accent Palette
function getSubjectTheme(subjectName?: string, department?: string | null) {
  const name = (subjectName || '').toLowerCase();
  const dept = (department || '').toLowerCase();

  if (name.includes('math') || name.includes('algebra') || name.includes('geom')) {
    return { icon: '📘', badgeClass: 'theme-blue', color: '#2563EB' };
  }
  if (name.includes('physic') || name.includes('chem') || name.includes('bio') || dept.includes('science')) {
    return { icon: '🔬', badgeClass: 'theme-emerald', color: '#10B981' };
  }
  if (name.includes('social') || name.includes('geograph') || name.includes('history')) {
    return { icon: '🌍', badgeClass: 'theme-teal', color: '#0D9488' };
  }
  if (name.includes('ict') || name.includes('comput') || name.includes('tech')) {
    return { icon: '💻', badgeClass: 'theme-indigo', color: '#4F46E5' };
  }
  if (name.includes('somali') || name.includes('english') || name.includes('arabic') || name.includes('islam') || dept.includes('language')) {
    return { icon: '📖', badgeClass: 'theme-purple', color: '#7C3AED' };
  }
  return { icon: '📚', badgeClass: 'theme-amber', color: '#D97706' };
}

onMounted(() => {
  loadData();
});
</script>

<template>
  <div class="portal-page">
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-left">
        <div class="somroyal-tag">
          <svg class="crown-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M5 16L3 5l5.5 5L12 4l3.5 6L21 5l-2 11H5m14 3c0 .6-.4 1-1 1H6c-.6 0-1-.4-1-1v-1h14v1z"/>
          </svg>
          <span>TEACHING CURRICULUM &bull; ASSIGNED STREAMS</span>
        </div>
        <h1 class="page-title">My Classes &amp; Subjects</h1>
        <p class="page-subtitle">
          Curriculum courses, student rosters, and schedules strictly assigned to your faculty account by School Administration.
        </p>
      </div>

      <div class="header-actions">
        <button class="btn-refresh" :disabled="isLoading" @click="loadData">
          <svg class="refresh-icon" :class="{ 'spin-active': isLoading }" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
          </svg>
          <span>{{ isLoading ? 'Syncing...' : 'Refresh Assignments' }}</span>
        </button>
      </div>
    </div>

    <!-- Summary KPI Cards -->
    <div class="summary-metrics-grid">
      <div class="metric-card">
        <div class="metric-icon-wrap icon-blue">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
        </div>
        <div class="metric-content">
          <span class="metric-label">ASSIGNED STREAMS</span>
          <span class="metric-value">{{ totalAssignedStreams }}</span>
          <span class="metric-sub">Active Subject-Class Pairings</span>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon-wrap icon-emerald">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
        </div>
        <div class="metric-content">
          <span class="metric-label">ASSIGNED CLASSES</span>
          <span class="metric-value text-emerald">{{ totalUniqueClasses }}</span>
          <span class="metric-sub">Distinct Student Groups</span>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon-wrap icon-purple">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        </div>
        <div class="metric-content">
          <span class="metric-label">TEACHING SUBJECTS</span>
          <span class="metric-value">{{ totalUniqueSubjects }}</span>
          <span class="metric-sub">Curriculum Disciplines</span>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon-wrap icon-amber">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
        </div>
        <div class="metric-content">
          <span class="metric-label">ENROLLED STUDENTS</span>
          <span class="metric-value text-amber">{{ totalStudentsEnrolled }}</span>
          <span class="metric-sub">Under Your Instruction</span>
        </div>
      </div>
    </div>

    <!-- Filters & Search Toolbar -->
    <div class="filters-card">
      <div class="toolbar-top">
        <div class="search-input-wrap">
          <svg class="search-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by subject, code, class or department..."
            class="search-input"
          />
          <button v-if="searchQuery" class="clear-search-btn" @click="searchQuery = ''">&times;</button>
        </div>

        <div v-if="isFiltered" class="filter-reset-wrap">
          <button class="reset-btn" @click="resetFilters">
            <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            Clear Filters
          </button>
        </div>
      </div>

      <div class="filters-grid">
        <div class="form-group">
          <label class="form-label">Academic Year</label>
          <select v-model="selectedYear" class="form-select">
            <option value="ALL">All Academic Years ({{ availableYears.length }})</option>
            <option v-for="yr in availableYears" :key="yr" :value="yr">
              {{ yr }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Class</label>
          <select v-model="selectedClass" class="form-select">
            <option value="ALL">All Assigned Classes ({{ availableClassNames.length }})</option>
            <option v-for="c in availableClassNames" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Subject</label>
          <select v-model="selectedSubject" class="form-select">
            <option value="ALL">All Assigned Subjects ({{ availableSubjectNames.length }})</option>
            <option v-for="s in availableSubjectNames" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Assignment Status</label>
          <select v-model="selectedStatus" class="form-select">
            <option value="ALL">All Statuses</option>
            <option value="ACTIVE">Active (Current)</option>
            <option value="HISTORICAL">Historical (Past)</option>
            <option value="INACTIVE">Inactive (Disabled)</option>
          </select>
        </div>
      </div>

      <div class="filter-results-bar">
        <span class="results-count">
          Showing <strong>{{ filteredAssignments.length }}</strong> of <strong>{{ assignments.length }}</strong> assignments
        </span>
        <span v-if="selectedYear !== 'ALL'" class="active-filter-tag">
          Year: {{ selectedYear }}
        </span>
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
        <h4 class="error-title">Unable to Load Assigned Classes</h4>
        <p class="error-desc">{{ errorMessage }}</p>
      </div>
      <button class="btn-retry" @click="loadData">
        Retry Request
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="state-card loading">
      <div class="spinner-ring" />
      <span class="loading-label">Loading assigned teaching streams from database...</span>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredAssignments.length === 0" class="state-card empty">
      <div class="empty-icon-circle">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      </div>
      <h3 class="state-title">
        {{ assignments.length === 0 ? 'No Classes or Subjects Assigned Yet' : 'No Matching Assignments Found' }}
      </h3>
      <p class="state-desc">
        {{
          assignments.length === 0
            ? 'No curriculum classes or subjects have been assigned to your faculty account yet. Please contact the School Administrator.'
            : 'No assigned courses match your current search query and filter selections.'
        }}
      </p>
      <button v-if="assignments.length > 0" class="btn-reset-filters" @click="resetFilters">
        Reset Filter Criteria
      </button>
    </div>

    <!-- Assignments Cards Grid -->
    <div v-else class="assignments-grid">
      <div
        v-for="a in filteredAssignments"
        :key="a.id"
        class="assignment-card"
        :style="{ borderTopColor: getSubjectTheme(a.subject_name || a.subject?.name, a.department || a.subject?.department).color }"
      >
        <!-- Card Top Bar -->
        <div class="card-top-bar">
          <div class="subject-header-group">
            <div class="subject-avatar" :class="getSubjectTheme(a.subject_name || a.subject?.name, a.department || a.subject?.department).badgeClass">
              {{ getSubjectTheme(a.subject_name || a.subject?.name, a.department || a.subject?.department).icon }}
            </div>
            <div class="subject-title-area">
              <h3 class="subject-name">
                {{ a.subject_name || a.subject?.name || `Subject ${a.subject_id}` }}
              </h3>
              <div class="code-dept-row">
                <span v-if="a.subject_code || a.subject?.code" class="code-pill">
                  {{ a.subject_code || a.subject?.code }}
                </span>
                <span v-else class="code-pill muted">
                  Not assigned
                </span>
                <span v-if="a.department || a.subject?.department" class="dept-pill">
                  {{ a.department || a.subject?.department }}
                </span>
              </div>
            </div>
          </div>

          <!-- Status Indicator -->
          <div class="status-wrap">
            <span
              v-if="a.display_status === 'ACTIVE' || (a.is_current_academic_year && a.status === 'ACTIVE')"
              class="status-badge-stream active"
              title="Active teaching stream for current academic year"
            >
              <span class="pulse-dot green" />
              ACTIVE
            </span>
            <span
              v-else-if="a.display_status === 'HISTORICAL' || (!a.is_current_academic_year && a.status === 'ACTIVE')"
              class="status-badge-stream historical"
              title="Historical assignment from previous academic year"
            >
              <span class="pulse-dot amber" />
              HISTORICAL
            </span>
            <span v-else class="status-badge-stream inactive" title="Assignment deactivated by administrator">
              <span class="pulse-dot gray" />
              INACTIVE
            </span>
          </div>
        </div>

        <!-- Card Meta Key-Values -->
        <div class="card-details-grid">
          <!-- Class Row -->
          <div class="detail-item">
            <span class="detail-label">CLASS</span>
            <div class="class-val-row">
              <span class="class-badge-pill">
                {{ a.class_name || a.school_class?.name || `Class ${a.class_id}` }}
              </span>
              <span v-if="a.section || a.school_class?.section" class="section-tag">
                Sec {{ a.section || a.school_class?.section }}
              </span>
              <span v-if="a.class_code || a.school_class?.code" class="class-code-tag">
                {{ a.class_code || a.school_class?.code }}
              </span>
            </div>
          </div>

          <!-- Academic Year Row -->
          <div class="detail-item">
            <span class="detail-label">ACADEMIC YEAR</span>
            <div class="year-val-row">
              <svg class="item-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span class="detail-value font-semibold">{{ a.academic_year }}</span>
            </div>
          </div>

          <!-- Students Row -->
          <div class="detail-item">
            <span class="detail-label">STUDENTS</span>
            <div class="students-val-row">
              <svg class="item-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
              <span class="detail-value font-bold text-navy">
                {{ a.student_count ?? a.school_class?.students_count ?? 0 }} students
              </span>
              <span v-if="a.school_class?.capacity" class="capacity-ratio">
                (Cap: {{ a.school_class.capacity }})
              </span>
            </div>
          </div>

          <!-- Teacher Row -->
          <div class="detail-item">
            <span class="detail-label">ASSIGNMENT</span>
            <div class="teacher-val-row">
              <span class="teacher-name-tag">
                {{ a.teacher_name || 'Assigned Faculty' }}
              </span>
              <span class="role-subtag">Subject Teacher</span>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="card-footer-actions">
          <button
            class="btn-view-class"
            title="View student roster and comprehensive class profile"
            @click="openClassDetail(a)"
          >
            <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            <span>View Class</span>
          </button>

          <div class="quick-nav-group">
            <button
              class="btn-quick-action"
              title="Record or review student attendance for this assignment"
              @click="navigateToAttendance(a)"
            >
              <svg class="btn-icon text-emerald" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
              <span>Attendance</span>
            </button>

            <button
              class="btn-quick-action"
              title="Enter marks and manage assessments for this course"
              @click="navigateToExams(a)"
            >
              <svg class="btn-icon text-purple" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>Exams</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- CLASS DETAIL MODAL -->
    <div v-if="isDetailModalOpen" class="modal-backdrop" @click="isDetailModalOpen = false">
      <div class="modal-card" @click.stop>
        <!-- Modal Loading State -->
        <div v-if="isLoadingDetail" class="modal-loading-box">
          <div class="spinner-ring" />
          <span>Retrieving class roster and schedule from database...</span>
        </div>

        <div v-else-if="classDetail" class="modal-content-wrap">
          <!-- Modal Header -->
          <div class="modal-header">
            <div class="modal-header-text">
              <div class="modal-badge-line">
                <span class="class-badge-pill">
                  {{ classDetail.name }} ({{ classDetail.code }})
                </span>
                <span class="year-badge-pill">{{ classDetail.academic_year }}</span>
                <span v-if="classDetail.section" class="section-tag">{{ classDetail.section }}</span>
              </div>
              <h2 class="modal-class-title">
                {{ selectedAssignment?.subject_name || selectedAssignment?.subject?.name || 'Class' }} &mdash; {{ classDetail.name }}
              </h2>
              <p class="modal-subtitle">
                Assigned to: <strong>{{ selectedAssignment?.teacher_name || 'Faculty Account' }}</strong> &bull;
                Academic Year: <strong>{{ classDetail.academic_year }}</strong>
              </p>
            </div>
            <button class="modal-close" title="Close modal" @click="isDetailModalOpen = false">&times;</button>
          </div>

          <!-- Class Stats KPI Strip -->
          <div class="modal-kpi-grid">
            <div class="modal-kpi-box">
              <span class="modal-kpi-label">ENROLLED STUDENTS</span>
              <span class="modal-kpi-val text-navy">{{ classDetail.enrolled_students_count }}</span>
              <span class="modal-kpi-sub">Capacity: {{ classDetail.capacity }}</span>
            </div>

            <div class="modal-kpi-box">
              <span class="modal-kpi-label">CLASS ATTENDANCE</span>
              <span class="modal-kpi-val text-emerald">{{ classDetail.attendance_rate }}%</span>
              <span class="modal-kpi-sub">Overall Average</span>
            </div>

            <div class="modal-kpi-box">
              <span class="modal-kpi-label">ASSIGNED SUBJECTS</span>
              <span class="modal-kpi-val text-purple">{{ classDetail.my_subjects.length }}</span>
              <span class="modal-kpi-sub">Taught By You</span>
            </div>

            <div class="modal-kpi-box">
              <span class="modal-kpi-label">WEEKLY PERIODS</span>
              <span class="modal-kpi-val text-amber">{{ classDetail.timetables.length }}</span>
              <span class="modal-kpi-sub">Scheduled Slots</span>
            </div>
          </div>

          <!-- Modal Navigation Tabs -->
          <div class="modal-tabs">
            <button
              class="modal-tab-btn"
              :class="{ active: activeDetailTab === 'students' }"
              @click="activeDetailTab === 'students'"
            >
              Enrolled Students ({{ classDetail.students.length }})
            </button>
            <button
              class="modal-tab-btn"
              :class="{ active: activeDetailTab === 'timetable' }"
              @click="activeDetailTab === 'timetable'"
            >
              Class Timetable ({{ classDetail.timetables.length }})
            </button>
            <button
              class="modal-tab-btn"
              :class="{ active: activeDetailTab === 'exams' }"
              @click="activeDetailTab === 'exams'"
            >
              Assessments &amp; Exams ({{ classDetail.exams.length }})
            </button>
          </div>

          <!-- Tab Content 1: Enrolled Students Roster -->
          <div v-if="activeDetailTab === 'students'" class="modal-tab-pane">
            <div class="modal-toolbar-row">
              <div class="modal-search-box">
                <svg class="search-icon sm" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <input
                  v-model="studentSearchQuery"
                  type="text"
                  placeholder="Filter roster by student name or admission number..."
                  class="modal-search-input"
                />
              </div>
              <span class="roster-count-text">
                {{ filteredModalStudents.length }} student{{ filteredModalStudents.length === 1 ? '' : 's' }} listed
              </span>
            </div>

            <div v-if="filteredModalStudents.length === 0" class="empty-inline">
              No enrolled students match your search filter.
            </div>

            <div v-else class="table-responsive-wrapper">
              <table class="somroyal-table">
                <thead>
                  <tr>
                    <th style="width: 45px;">#</th>
                    <th>Admission #</th>
                    <th>Student Full Name</th>
                    <th>Gender</th>
                    <th>Portal Access</th>
                    <th>Enrollment Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(std, idx) in filteredModalStudents" :key="std.id">
                    <td class="text-muted">{{ idx + 1 }}</td>
                    <td>
                      <code class="adm-code">{{ std.admission_number }}</code>
                    </td>
                    <td class="font-bold text-navy">
                      {{ std.first_name }} {{ std.middle_name || '' }} {{ std.last_name }}
                    </td>
                    <td>
                      <span class="gender-tag" :class="std.gender?.toLowerCase()">
                        {{ std.gender || 'Not specified' }}
                      </span>
                    </td>
                    <td>
                      <span v-if="std.has_portal_access" class="portal-pill active">
                        &check; Registered
                      </span>
                      <span v-else class="portal-pill inactive">
                        Unregistered
                      </span>
                    </td>
                    <td>
                      <StatusBadge :status="std.status" variant="success" />
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Tab Content 2: Timetable Schedule -->
          <div v-if="activeDetailTab === 'timetable'" class="modal-tab-pane">
            <div v-if="classDetail.timetables.length === 0" class="empty-inline">
              No weekly class timetable slots scheduled yet for your subjects.
            </div>
            <div v-else class="table-responsive-wrapper">
              <table class="somroyal-table">
                <thead>
                  <tr>
                    <th>Day of Week</th>
                    <th>Time Interval</th>
                    <th>Subject</th>
                    <th>Classroom</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="t in classDetail.timetables" :key="t.id">
                    <td class="font-bold text-navy">{{ t.day_of_week }}</td>
                    <td class="font-mono">{{ t.start_time }} &ndash; {{ t.end_time }}</td>
                    <td>{{ t.subject_name || selectedAssignment?.subject_name }}</td>
                    <td>
                      <span class="room-pill">{{ t.room_number || t.room || 'Room TBD' }}</span>
                    </td>
                    <td>
                      <span class="status-pill active-tag">Active</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Tab Content 3: Assessments & Exams -->
          <div v-if="activeDetailTab === 'exams'" class="modal-tab-pane">
            <div v-if="classDetail.exams.length === 0" class="empty-inline">
              No examination records found for your assigned subjects in this class.
            </div>
            <div v-else class="table-responsive-wrapper">
              <table class="somroyal-table">
                <thead>
                  <tr>
                    <th>Exam Name</th>
                    <th>Subject</th>
                    <th>Max Marks</th>
                    <th>Academic Term</th>
                    <th>Exam Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="ex in classDetail.exams" :key="ex.id">
                    <td class="font-bold text-navy">{{ ex.name }}</td>
                    <td>{{ ex.subject_name || selectedAssignment?.subject_name }}</td>
                    <td>{{ ex.max_marks || 100 }} Marks</td>
                    <td>{{ ex.term || 'Term 1' }}</td>
                    <td>
                      <StatusBadge :status="ex.status" :variant="ex.status === 'ONGOING' ? 'warning' : 'info'" />
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Modal Footer Actions -->
          <div class="modal-footer">
            <button class="btn-modal-close" @click="isDetailModalOpen = false">
              Close
            </button>

            <button
              v-if="selectedAssignment"
              class="btn-modal-sec"
              @click="navigateToAttendance(selectedAssignment)"
            >
              Take Attendance
            </button>

            <button
              v-if="selectedAssignment"
              class="btn-modal-prim"
              @click="navigateToExams(selectedAssignment)"
            >
              Enter Exam Marks
            </button>
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
  max-width: 1360px;
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-refresh {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: #FFFFFF;
  color: #0A192F;
  border: 1px solid #E2E8F0;
  padding: 0.5rem 0.95rem;
  border-radius: 10px;
  font-size: 0.84rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.btn-refresh:hover:not(:disabled) {
  border-color: #10B981;
  color: #10B981;
  background: #ECFDF5;
}

.refresh-icon {
  width: 15px;
  height: 15px;
}

.spin-active {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Metric KPIs */
.summary-metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.15rem;
}

.metric-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 14px;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 6px rgba(10, 25, 47, 0.03);
  transition: all 0.2s ease;
}

.metric-card:hover {
  border-color: #CBD5E1;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(10, 25, 47, 0.06);
}

.metric-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.metric-icon-wrap svg {
  width: 22px;
  height: 22px;
}

.icon-blue { background: #EFF6FF; color: #2563EB; }
.icon-emerald { background: #ECFDF5; color: #059669; }
.icon-purple { background: #F5F3FF; color: #7C3AED; }
.icon-amber { background: #FEF3C7; color: #D97706; }

.metric-content {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.metric-label {
  font-size: 0.68rem;
  font-weight: 800;
  color: #64748B;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.metric-value {
  font-size: 1.55rem;
  font-weight: 900;
  color: #0A192F;
  line-height: 1.2;
}

.metric-sub {
  font-size: 0.72rem;
  color: #94A3B8;
}

.text-emerald { color: #059669 !important; }
.text-amber { color: #D97706 !important; }
.text-purple { color: #7C3AED !important; }
.text-navy { color: #0A192F !important; }

/* Filters Toolbar */
.filters-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  box-shadow: 0 2px 6px rgba(10, 25, 47, 0.03);
}

.toolbar-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.search-input-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #F8FAFC;
  border: 1px solid #CBD5E1;
  border-radius: 10px;
  padding: 0.45rem 0.85rem;
  flex: 1;
  min-width: 260px;
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

.reset-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: #F1F5F9;
  border: 1px solid #CBD5E1;
  color: #475569;
  padding: 0.45rem 0.85rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.reset-btn:hover {
  background: #E2E8F0;
  color: #0A192F;
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

.form-select {
  background: #F8FAFC;
  border: 1px solid #CBD5E1;
  color: #0A192F;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  font-size: 0.84rem;
  font-weight: 600;
  outline: none;
  cursor: pointer;
}

.filter-results-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 0.5rem;
  border-top: 1px solid #F1F5F9;
  font-size: 0.8rem;
  color: #64748B;
}

.active-filter-tag {
  background: #EFF6FF;
  color: #1E40AF;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  font-weight: 700;
}

/* Assignments Cards Grid */
.assignments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1.25rem;
}

.assignment-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-top-width: 4px;
  border-radius: 14px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
  box-shadow: 0 2px 6px rgba(10, 25, 47, 0.03);
  transition: all 0.2s ease;
}

.assignment-card:hover {
  border-color: #CBD5E1;
  box-shadow: 0 8px 20px rgba(10, 25, 47, 0.06);
}

.card-top-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
}

.subject-header-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 0;
}

.subject-avatar {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.35rem;
  flex-shrink: 0;
}

.theme-blue { background: #EFF6FF; }
.theme-emerald { background: #ECFDF5; }
.theme-teal { background: #CCFBF1; }
.theme-indigo { background: #EEF2FF; }
.theme-purple { background: #F5F3FF; }
.theme-amber { background: #FEF3C7; }

.subject-title-area {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 0;
}

.subject-name {
  font-size: 1.05rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.code-dept-row {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  flex-wrap: wrap;
}

.code-pill {
  font-size: 0.7rem;
  font-family: monospace;
  font-weight: 800;
  color: #2563EB;
  background: #EFF6FF;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.code-pill.muted {
  color: #94A3B8;
  background: #F1F5F9;
}

.dept-pill {
  font-size: 0.68rem;
  font-weight: 700;
  color: #475569;
  background: #F1F5F9;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.status-badge-stream {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.68rem;
  font-weight: 800;
  padding: 0.2rem 0.55rem;
  border-radius: 20px;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

.status-badge-stream.active {
  background: #ECFDF5;
  color: #065F46;
  border: 1px solid #A7F3D0;
}

.status-badge-stream.historical {
  background: #FEF3C7;
  color: #92400E;
  border: 1px solid #FDE68A;
}

.status-badge-stream.inactive {
  background: #F1F5F9;
  color: #64748B;
  border: 1px solid #E2E8F0;
}

.pulse-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.pulse-dot.green { background: #10B981; }
.pulse-dot.amber { background: #F59E0B; }
.pulse-dot.gray { background: #94A3B8; }

/* Details grid */
.card-details-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  background: #F8FAFC;
  padding: 0.85rem;
  border-radius: 10px;
  border: 1px solid #E2E8F0;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.detail-label {
  font-size: 0.65rem;
  font-weight: 700;
  color: #94A3B8;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.class-val-row, .year-val-row, .students-val-row, .teacher-val-row {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  flex-wrap: wrap;
}

.class-badge-pill {
  font-size: 0.82rem;
  font-weight: 800;
  color: #0A192F;
}

.section-tag {
  font-size: 0.7rem;
  background: #E2E8F0;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  color: #475569;
}

.class-code-tag {
  font-size: 0.7rem;
  color: #64748B;
}

.item-icon {
  width: 14px;
  height: 14px;
  color: #64748B;
}

.detail-value {
  font-size: 0.84rem;
  color: #1E293B;
}

.capacity-ratio {
  font-size: 0.72rem;
  color: #94A3B8;
}

.teacher-name-tag {
  font-size: 0.8rem;
  font-weight: 700;
  color: #1E293B;
}

.role-subtag {
  font-size: 0.68rem;
  color: #64748B;
}

/* Card Footer Actions */
.card-footer-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-top: auto;
  padding-top: 0.5rem;
  border-top: 1px solid #F1F5F9;
}

.btn-view-class {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: #0A192F;
  color: #FFFFFF;
  border: none;
  padding: 0.45rem 0.85rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-view-class:hover {
  background: #1E3A8A;
}

.btn-view-class .btn-icon {
  width: 15px;
  height: 15px;
}

.quick-nav-group {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.btn-quick-action {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  background: #FFFFFF;
  border: 1px solid #CBD5E1;
  color: #0A192F;
  padding: 0.4rem 0.65rem;
  border-radius: 8px;
  font-size: 0.76rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-quick-action:hover {
  background: #F1F5F9;
  border-color: #94A3B8;
}

.btn-quick-action .btn-icon {
  width: 14px;
  height: 14px;
}

/* Modal Styling */
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
  max-width: 900px;
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

.year-badge-pill {
  font-size: 0.72rem;
  font-weight: 700;
  background: #E2E8F0;
  color: #475569;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}

.modal-class-title {
  font-size: 1.35rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
}

.modal-subtitle {
  font-size: 0.84rem;
  color: #64748B;
  margin-top: 0.25rem;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.75rem;
  color: #94A3B8;
  cursor: pointer;
  line-height: 1;
}

.modal-close:hover {
  color: #0A192F;
}

.modal-kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  padding: 1.25rem 2rem;
  background: #FFFFFF;
  border-bottom: 1px solid #E2E8F0;
}

.modal-kpi-box {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.modal-kpi-label {
  font-size: 0.65rem;
  font-weight: 800;
  color: #64748B;
  text-transform: uppercase;
}

.modal-kpi-val {
  font-size: 1.4rem;
  font-weight: 900;
}

.modal-kpi-sub {
  font-size: 0.72rem;
  color: #94A3B8;
}

.modal-tabs {
  display: flex;
  gap: 0.5rem;
  padding: 0.75rem 2rem 0;
  border-bottom: 2px solid #E2E8F0;
  background: #F8FAFC;
}

.modal-tab-btn {
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  padding: 0.65rem 1rem;
  font-size: 0.86rem;
  font-weight: 700;
  color: #64748B;
  cursor: pointer;
  margin-bottom: -2px;
  transition: all 0.2s ease;
}

.modal-tab-btn.active {
  color: #0A192F;
  border-bottom-color: #10B981;
}

.modal-tab-pane {
  padding: 1.5rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.modal-toolbar-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.modal-search-box {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: #F8FAFC;
  border: 1px solid #CBD5E1;
  border-radius: 8px;
  padding: 0.4rem 0.75rem;
  flex: 1;
  max-width: 400px;
}

.modal-search-input {
  background: transparent;
  border: none;
  font-size: 0.84rem;
  color: #0A192F;
  width: 100%;
  outline: none;
}

.roster-count-text {
  font-size: 0.78rem;
  color: #64748B;
  font-weight: 600;
}

.adm-code {
  font-family: monospace;
  font-weight: 700;
  color: #2563EB;
  background: #EFF6FF;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.gender-tag {
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border-radius: 12px;
  background: #F1F5F9;
  color: #475569;
}

.portal-pill {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.portal-pill.active {
  background: #ECFDF5;
  color: #059669;
}

.portal-pill.inactive {
  background: #F1F5F9;
  color: #94A3B8;
}

.modal-footer {
  padding: 1rem 2rem;
  background: #F8FAFC;
  border-top: 1px solid #E2E8F0;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-modal-close {
  background: #FFFFFF;
  border: 1px solid #CBD5E1;
  color: #475569;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.84rem;
  font-weight: 700;
  cursor: pointer;
}

.btn-modal-sec {
  background: #ECFDF5;
  border: 1px solid #A7F3D0;
  color: #065F46;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.84rem;
  font-weight: 700;
  cursor: pointer;
}

.btn-modal-prim {
  background: #0A192F;
  border: none;
  color: #FFFFFF;
  padding: 0.5rem 1.15rem;
  border-radius: 8px;
  font-size: 0.84rem;
  font-weight: 700;
  cursor: pointer;
}

.btn-modal-prim:hover {
  background: #1E3A8A;
}

/* Common State Styles */
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
  max-width: 500px;
  line-height: 1.5;
  margin: 0;
}

.btn-reset-filters {
  background: #0A192F;
  color: #FFFFFF;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.84rem;
  font-weight: 700;
  cursor: pointer;
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

.error-icon-box svg {
  width: 20px;
  height: 20px;
}

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

.empty-inline {
  padding: 2rem 1rem;
  text-align: center;
  font-size: 0.86rem;
  color: #64748B;
  background: #F8FAFC;
  border-radius: 10px;
  border: 1px dashed #CBD5E1;
}

.table-responsive-wrapper {
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
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #F1F5F9;
  color: #1E293B;
  vertical-align: middle;
}

.somroyal-table tbody tr:hover {
  background: #F8FAFC;
}

.room-pill {
  font-size: 0.74rem;
  font-weight: 700;
  background: #F1F5F9;
  color: #475569;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
}

.status-pill.active-tag {
  background: #ECFDF5;
  color: #059669;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 20px;
}

/* Responsive Rules */
@media (max-width: 1024px) {
  .summary-metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .filters-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .modal-kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }
  .btn-refresh {
    width: 100%;
    justify-content: center;
  }
  .summary-metrics-grid {
    grid-template-columns: 1fr;
  }
  .filters-grid {
    grid-template-columns: 1fr;
  }
  .assignments-grid {
    grid-template-columns: 1fr;
  }
  .card-footer-actions {
    flex-direction: column;
    align-items: stretch;
  }
  .quick-nav-group {
    width: 100%;
  }
  .btn-quick-action, .btn-view-class {
    flex: 1;
    justify-content: center;
  }
  .modal-card {
    border-radius: 14px;
    padding: 0;
  }
  .modal-header, .modal-kpi-grid, .modal-tabs, .modal-tab-pane, .modal-footer {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  .modal-kpi-grid {
    grid-template-columns: 1fr;
  }
}
</style>
