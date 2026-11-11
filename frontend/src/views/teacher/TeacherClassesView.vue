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
  // Sum of student_count for distinct classes in current year or total
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
    return { icon: '📘', badgeClass: 'theme-blue', color: '#0284c7' };
  }
  if (name.includes('physic') || name.includes('chem') || name.includes('bio') || dept.includes('science')) {
    return { icon: '🔬', badgeClass: 'theme-emerald', color: '#059669' };
  }
  if (name.includes('social') || name.includes('geograph') || name.includes('history')) {
    return { icon: '🌍', badgeClass: 'theme-teal', color: '#0d9488' };
  }
  if (name.includes('ict') || name.includes('comput') || name.includes('tech')) {
    return { icon: '💻', badgeClass: 'theme-indigo', color: '#4f46e5' };
  }
  if (name.includes('somali') || name.includes('english') || name.includes('arabic') || name.includes('islam') || dept.includes('language')) {
    return { icon: '📖', badgeClass: 'theme-purple', color: '#7c3aed' };
  }
  return { icon: '📚', badgeClass: 'theme-amber', color: '#d97706' };
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
        <div class="badge-row">
          <span class="role-chip">Teacher Portal</span>
          <span class="auth-chip">
            <svg class="chip-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            Admin Assigned • Read-Only
          </span>
        </div>
        <h1 class="page-title">My Classes & Subjects</h1>
        <p class="page-subtitle">
          Curriculum courses, student rosters, and schedules strictly assigned to your faculty account by School Administration.
        </p>
      </div>

      <div class="header-actions">
        <button class="btn btn-outline btn-refresh" :disabled="isLoading" @click="loadData">
          <svg class="btn-icon" :class="{ 'spin-active': isLoading }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>{{ isLoading ? 'Refreshing...' : 'Refresh Assignments' }}</span>
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
          <span class="metric-label">Assigned Streams</span>
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
          <span class="metric-label">Assigned Classes</span>
          <span class="metric-value">{{ totalUniqueClasses }}</span>
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
          <span class="metric-label">Teaching Subjects</span>
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
          <span class="metric-label">Total Enrolled Students</span>
          <span class="metric-value">{{ totalStudentsEnrolled }}</span>
          <span class="metric-sub">Under Your Instruction</span>
        </div>
      </div>
    </div>

    <!-- Filters & Search Toolbar -->
    <div class="filters-card card">
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
          <button class="btn btn-sm btn-ghost reset-btn" @click="resetFilters">
            <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            Clear All Filters
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
    <div v-if="errorMessage" class="alert-box error card">
      <div class="alert-content">
        <svg class="alert-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <div>
          <h4 class="alert-title">Unable to Load Assigned Classes</h4>
          <p class="alert-desc">{{ errorMessage }}</p>
        </div>
      </div>
      <button class="btn btn-sm btn-outline-danger" @click="loadData">
        Retry Request
      </button>
    </div>

    <!-- Loading Skeleton State -->
    <div v-if="isLoading" class="skeleton-grid">
      <div v-for="i in 6" :key="i" class="card skeleton-card">
        <div class="skeleton-header">
          <div class="skeleton-box skeleton-icon" />
          <div class="skeleton-text-group">
            <div class="skeleton-box skeleton-line lg" />
            <div class="skeleton-box skeleton-line sm" />
          </div>
        </div>
        <div class="skeleton-body">
          <div class="skeleton-box skeleton-line md" />
          <div class="skeleton-box skeleton-line md" />
          <div class="skeleton-box skeleton-line sm" />
        </div>
        <div class="skeleton-footer">
          <div class="skeleton-box skeleton-btn" />
          <div class="skeleton-box skeleton-btn sm" />
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredAssignments.length === 0" class="card empty-state-box">
      <div class="empty-icon-circle">
        <svg class="empty-svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      </div>
      <h3 class="empty-heading">
        {{ assignments.length === 0 ? 'No Classes or Subjects Assigned Yet' : 'No Matching Assignments Found' }}
      </h3>
      <p class="empty-text">
        {{
          assignments.length === 0
            ? 'No curriculum classes or subjects have been assigned to your faculty account yet. Please contact the School Administrator.'
            : 'No assigned courses match your current search query and filter selections.'
        }}
      </p>
      <button v-if="assignments.length > 0" class="btn btn-primary btn-sm" @click="resetFilters">
        Reset Filter Criteria
      </button>
    </div>

    <!-- Assignments Cards Grid -->
    <div v-else class="assignments-grid">
      <div
        v-for="a in filteredAssignments"
        :key="a.id"
        class="assignment-card card"
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
              class="status-badge active"
              title="Active teaching stream for current academic year"
            >
              <span class="status-dot green" />
              ACTIVE
            </span>
            <span
              v-else-if="a.display_status === 'HISTORICAL' || (!a.is_current_academic_year && a.status === 'ACTIVE')"
              class="status-badge historical"
              title="Historical assignment from previous academic year (Read-Only)"
            >
              <span class="status-dot amber" />
              HISTORICAL
            </span>
            <span v-else class="status-badge inactive" title="Assignment deactivated by administrator">
              <span class="status-dot gray" />
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
                {{ a.section || a.school_class?.section }}
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
              <span class="detail-value font-bold text-primary">
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
            class="btn btn-primary btn-action-main"
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
              class="btn btn-outline btn-action-sub"
              title="Record or review student attendance for this assignment"
              @click="navigateToAttendance(a)"
            >
              <svg class="btn-icon text-emerald" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
              <span>Attendance</span>
            </button>

            <button
              class="btn btn-outline btn-action-sub"
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

    <!-- =================================================================== -->
    <!-- CLASS DETAIL MODAL                                                  -->
    <!-- =================================================================== -->
    <div v-if="isDetailModalOpen" class="modal-backdrop" @click="isDetailModalOpen = false">
      <div class="modal-card card large" @click.stop>
        <!-- Modal Loading State -->
        <div v-if="isLoadingDetail" class="modal-loading-box">
          <div class="spinner" />
          <span>Retrieving class roster and schedule from PostgreSQL...</span>
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
                {{ selectedAssignment?.subject_name || selectedAssignment?.subject?.name || 'Class' }} — {{ classDetail.name }}
              </h2>
              <p class="modal-subtitle">
                Assigned to: <strong>{{ selectedAssignment?.teacher_name || 'Faculty Account' }}</strong> •
                Academic Year: <strong>{{ classDetail.academic_year }}</strong>
              </p>
            </div>
            <button class="modal-close" title="Close modal" @click="isDetailModalOpen = false">&times;</button>
          </div>

          <!-- Class Stats KPI Strip -->
          <div class="modal-kpi-grid">
            <div class="modal-kpi-box">
              <span class="modal-kpi-label">Enrolled Students</span>
              <span class="modal-kpi-val text-primary">{{ classDetail.enrolled_students_count }}</span>
              <span class="modal-kpi-sub">Capacity: {{ classDetail.capacity }}</span>
            </div>

            <div class="modal-kpi-box">
              <span class="modal-kpi-label">Class Attendance</span>
              <span class="modal-kpi-val text-emerald">{{ classDetail.attendance_rate }}%</span>
              <span class="modal-kpi-sub">Overall Average</span>
            </div>

            <div class="modal-kpi-box">
              <span class="modal-kpi-label">Assigned Subjects</span>
              <span class="modal-kpi-val text-purple">{{ classDetail.my_subjects.length }}</span>
              <span class="modal-kpi-sub">Taught By You</span>
            </div>

            <div class="modal-kpi-box">
              <span class="modal-kpi-label">Weekly Periods</span>
              <span class="modal-kpi-val text-amber">{{ classDetail.timetables.length }}</span>
              <span class="modal-kpi-sub">Scheduled Slots</span>
            </div>
          </div>

          <!-- Modal Navigation Tabs -->
          <div class="modal-tabs">
            <button
              class="modal-tab-btn"
              :class="{ active: activeDetailTab === 'students' }"
              @click="activeDetailTab = 'students'"
            >
              Enrolled Students ({{ classDetail.students.length }})
            </button>
            <button
              class="modal-tab-btn"
              :class="{ active: activeDetailTab === 'timetable' }"
              @click="activeDetailTab = 'timetable'"
            >
              Class Timetable ({{ classDetail.timetables.length }})
            </button>
            <button
              class="modal-tab-btn"
              :class="{ active: activeDetailTab === 'exams' }"
              @click="activeDetailTab = 'exams'"
            >
              Assessments & Exams ({{ classDetail.exams.length }})
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

            <div v-else class="table-responsive modal-table-wrap">
              <table class="portal-table">
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
                    <td class="font-bold student-name-cell">
                      {{ std.first_name }} {{ std.middle_name || '' }} {{ std.last_name }}
                    </td>
                    <td>
                      <span class="gender-tag" :class="std.gender?.toLowerCase()">
                        {{ std.gender || 'Not specified' }}
                      </span>
                    </td>
                    <td>
                      <span v-if="std.has_portal_access" class="portal-pill active">
                        ✓ Registered
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
            <div v-else class="table-responsive modal-table-wrap">
              <table class="portal-table">
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
                    <td class="font-bold text-primary">{{ t.day_of_week }}</td>
                    <td class="font-mono">{{ t.start_time }} — {{ t.end_time }}</td>
                    <td>{{ t.subject_name || selectedAssignment?.subject_name }}</td>
                    <td>
                      <span class="room-pill">{{ t.room_number || t.room || 'Room TBD' }}</span>
                    </td>
                    <td>
                      <span class="status-badge active sm">Active</span>
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
            <div v-else class="table-responsive modal-table-wrap">
              <table class="portal-table">
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
                    <td class="font-bold">{{ ex.name }}</td>
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
            <button class="btn btn-outline" @click="isDetailModalOpen = false">
              Close
            </button>

            <button
              v-if="selectedAssignment"
              class="btn btn-outline"
              @click="navigateToAttendance(selectedAssignment)"
            >
              Take Attendance
            </button>

            <button
              v-if="selectedAssignment"
              class="btn btn-primary"
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
  padding: 0.5rem;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1.25rem;
  flex-wrap: wrap;
}
.header-left { display: flex; flex-direction: column; gap: 0.35rem; }
.badge-row { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.2rem; }
.role-chip {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: #e0e7ff;
  color: #4338ca;
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
}
.auth-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.72rem;
  font-weight: 700;
  background: #f0fdf4;
  color: #15803d;
  border: 1px solid #bbf7d0;
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
}
.chip-icon { width: 14px; height: 14px; }
.page-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
  letter-spacing: -0.02em;
}
.page-subtitle {
  font-size: 0.9rem;
  color: var(--text-muted);
  margin: 0;
  max-width: 780px;
  line-height: 1.45;
}

.header-actions { display: flex; align-items: center; gap: 0.75rem; }
.btn-refresh {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 0.95rem;
  font-size: 0.85rem;
}
.spin-active { animation: spin 0.8s linear infinite; }

/* Metric KPIs */
.summary-metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}
.metric-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-medium);
  border-radius: 10px;
  padding: 1.15rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  transition: transform 0.15s, box-shadow 0.15s;
}
.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.07);
}
.metric-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.metric-icon-wrap svg { width: 24px; height: 24px; }
.icon-blue { background: #e0f2fe; color: #0284c7; }
.icon-emerald { background: #dcfce7; color: #059669; }
.icon-purple { background: #f3e8ff; color: #7c3aed; }
.icon-amber { background: #fef3c7; color: #d97706; }

.metric-content { display: flex; flex-direction: column; gap: 0.15rem; }
.metric-label { font-size: 0.74rem; font-weight: 700; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.04em; }
.metric-value { font-size: 1.6rem; font-weight: 800; color: var(--text-primary); line-height: 1.1; }
.metric-sub { font-size: 0.72rem; color: var(--text-muted); }

/* Filters Toolbar */
.filters-card {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.toolbar-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}
.search-input-wrap {
  position: relative;
  flex: 1;
  min-width: 260px;
}
.search-icon {
  position: absolute;
  left: 0.85rem;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: var(--text-muted);
}
.search-input {
  width: 100%;
  padding: 0.65rem 2.25rem 0.65rem 2.5rem;
  border: 1px solid var(--border-medium);
  border-radius: 8px;
  background: var(--bg-surface);
  font-size: 0.88rem;
  color: var(--text-primary);
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.search-input:focus {
  border-color: #0284c7;
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.12);
}
.clear-search-btn {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 1.2rem;
  cursor: pointer;
}
.reset-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  color: #dc2626;
  font-weight: 600;
  font-size: 0.82rem;
  padding: 0.4rem 0.75rem;
  border-radius: 6px;
  background: #fef2f2;
}
.reset-btn:hover { background: #fee2e2; }

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 0.85rem;
}
.form-group { display: flex; flex-direction: column; gap: 0.35rem; }
.form-label { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.03em; }
.form-select {
  padding: 0.6rem 0.75rem;
  border: 1px solid var(--border-medium);
  border-radius: 6px;
  background: var(--bg-surface);
  font-size: 0.88rem;
  color: var(--text-primary);
  outline: none;
}
.form-select:focus {
  border-color: #0284c7;
}

.filter-results-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 0.65rem;
  border-top: 1px solid var(--border-subtle);
  font-size: 0.82rem;
  color: var(--text-muted);
}
.active-filter-tag {
  background: #e0f2fe;
  color: #0369a1;
  padding: 0.15rem 0.55rem;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.75rem;
}

/* Assignments Cards Grid */
.assignments-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
}

.assignment-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-medium);
  border-top-width: 4px;
  border-radius: 10px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 1.15rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
  transition: transform 0.2s, box-shadow 0.2s;
}
.assignment-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
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
  gap: 0.85rem;
  flex: 1;
}
.subject-avatar {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  flex-shrink: 0;
}
.theme-blue { background: #e0f2fe; }
.theme-emerald { background: #dcfce7; }
.theme-teal { background: #ccfbf1; }
.theme-indigo { background: #e0e7ff; }
.theme-purple { background: #f3e8ff; }
.theme-amber { background: #fef3c7; }

.subject-title-area { display: flex; flex-direction: column; gap: 0.25rem; }
.subject-name {
  font-size: 1.18rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.25;
}
.code-dept-row { display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap; }
.code-pill {
  font-family: monospace;
  font-size: 0.75rem;
  font-weight: 700;
  background: #f1f5f9;
  color: #334155;
  padding: 0.12rem 0.45rem;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
}
.code-pill.muted { color: #94a3b8; font-style: italic; }
.dept-pill {
  font-size: 0.7rem;
  background: #f8fafc;
  color: #64748b;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}

/* Status Badges */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  padding: 0.2rem 0.55rem;
  border-radius: 9999px;
  flex-shrink: 0;
}
.status-badge.active { background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; }
.status-badge.historical { background: #fffbeb; color: #b45309; border: 1px solid #fde68a; }
.status-badge.inactive { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }
.status-badge.sm { font-size: 0.68rem; padding: 0.15rem 0.45rem; }

.status-dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; }
.status-dot.green { background: #10b981; box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2); }
.status-dot.amber { background: #f59e0b; }
.status-dot.gray { background: #94a3b8; }

/* Card Details Key-Values */
.card-details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.85rem;
  background: var(--bg-surface-secondary);
  padding: 0.95rem;
  border-radius: 8px;
  border: 1px solid var(--border-subtle);
}
.detail-item { display: flex; flex-direction: column; gap: 0.2rem; }
.detail-label {
  font-size: 0.68rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
}
.class-val-row { display: flex; align-items: center; gap: 0.35rem; flex-wrap: wrap; }
.class-badge-pill {
  font-size: 0.88rem;
  font-weight: 800;
  color: #0369a1;
  background: #e0f2fe;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}
.section-tag { font-size: 0.72rem; color: #475569; background: #f1f5f9; padding: 0.1rem 0.35rem; border-radius: 3px; }
.class-code-tag { font-size: 0.7rem; font-family: monospace; color: #64748b; }

.year-val-row, .students-val-row { display: flex; align-items: center; gap: 0.35rem; }
.item-icon { width: 15px; height: 15px; color: var(--text-muted); flex-shrink: 0; }
.detail-value { font-size: 0.88rem; color: var(--text-primary); }
.capacity-ratio { font-size: 0.72rem; color: var(--text-muted); }

.teacher-val-row { display: flex; flex-direction: column; gap: 0.1rem; }
.teacher-name-tag { font-size: 0.82rem; font-weight: 700; color: var(--text-primary); }
.role-subtag { font-size: 0.7rem; color: var(--text-muted); }

/* Card Actions */
.card-footer-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-subtle);
  flex-wrap: wrap;
}
.btn-action-main {
  flex: 1;
  min-width: 110px;
}
.quick-nav-group { display: flex; gap: 0.4rem; }
.btn-action-sub {
  padding: 0.45rem 0.65rem;
  font-size: 0.78rem;
}

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}
.modal-card.large {
  width: 100%;
  max-width: 860px;
  max-height: 90vh;
  overflow-y: auto;
  background: var(--bg-surface);
  border-radius: 12px;
  padding: 1.75rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}
.modal-loading-box {
  padding: 3.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  color: var(--text-muted);
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-medium);
}
.modal-badge-line { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.35rem; flex-wrap: wrap; }
.year-badge-pill {
  font-size: 0.75rem;
  font-weight: 700;
  background: #f1f5f9;
  color: #475569;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}
.modal-class-title {
  font-size: 1.45rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}
.modal-subtitle { font-size: 0.85rem; color: var(--text-muted); margin: 0.2rem 0 0 0; }
.modal-close {
  background: none;
  border: none;
  font-size: 1.8rem;
  line-height: 1;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 6px;
}
.modal-close:hover { color: var(--text-primary); background: #f1f5f9; }

.modal-kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}
.modal-kpi-box {
  background: var(--bg-surface-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  padding: 0.85rem 0.75rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}
.modal-kpi-label { font-size: 0.68rem; font-weight: 800; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.04em; }
.modal-kpi-val { font-size: 1.4rem; font-weight: 800; margin: 0.15rem 0; line-height: 1.1; }
.modal-kpi-sub { font-size: 0.68rem; color: var(--text-muted); }

.modal-tabs {
  display: flex;
  border-bottom: 1px solid var(--border-medium);
  margin-bottom: 1.15rem;
  gap: 0.5rem;
}
.modal-tab-btn {
  padding: 0.65rem 1rem;
  font-size: 0.85rem;
  font-weight: 700;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}
.modal-tab-btn:hover { color: var(--text-primary); }
.modal-tab-btn.active {
  color: #0284c7;
  border-bottom-color: #0284c7;
}

.modal-toolbar-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.85rem;
  flex-wrap: wrap;
}
.modal-search-box {
  position: relative;
  flex: 1;
  min-width: 220px;
}
.search-icon.sm { width: 15px; height: 15px; }
.modal-search-input {
  width: 100%;
  padding: 0.45rem 0.75rem 0.45rem 2.2rem;
  border: 1px solid var(--border-medium);
  border-radius: 6px;
  font-size: 0.82rem;
  background: var(--bg-surface);
  color: var(--text-primary);
  outline: none;
}
.roster-count-text { font-size: 0.78rem; font-weight: 600; color: var(--text-muted); }

.modal-table-wrap {
  max-height: 360px;
  overflow-y: auto;
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
}
.portal-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.85rem;
}
.portal-table th {
  background: var(--bg-surface-secondary);
  padding: 0.75rem 0.95rem;
  font-weight: 700;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-medium);
  position: sticky;
  top: 0;
  z-index: 2;
}
.portal-table td {
  padding: 0.7rem 0.95rem;
  border-bottom: 1px solid var(--border-subtle);
  color: var(--text-primary);
}
.adm-code {
  font-family: monospace;
  font-size: 0.78rem;
  background: #f1f5f9;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}
.gender-tag {
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}
.gender-tag.male { background: #e0f2fe; color: #0369a1; }
.gender-tag.female { background: #fce7f3; color: #be185d; }

.portal-pill {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.1rem 0.45rem;
  border-radius: 4px;
}
.portal-pill.active { background: #dcfce7; color: #15803d; }
.portal-pill.inactive { background: #f1f5f9; color: #64748b; }

.room-pill {
  background: #f1f5f9;
  color: #334155;
  font-weight: 700;
  font-size: 0.75rem;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-subtle);
  flex-wrap: wrap;
}

/* Skeleton loader */
.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
}
.skeleton-card {
  padding: 1.25rem;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.skeleton-box {
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 6px;
}
.skeleton-icon { width: 44px; height: 44px; border-radius: 10px; }
.skeleton-header { display: flex; gap: 0.75rem; align-items: center; }
.skeleton-text-group { display: flex; flex-direction: column; gap: 0.35rem; flex: 1; }
.skeleton-line.lg { height: 16px; width: 70%; }
.skeleton-line.md { height: 12px; width: 90%; }
.skeleton-line.sm { height: 10px; width: 50%; }
.skeleton-body { display: flex; flex-direction: column; gap: 0.5rem; }
.skeleton-footer { display: flex; justify-content: space-between; gap: 0.5rem; }
.skeleton-btn { height: 32px; width: 45%; }
.skeleton-btn.sm { width: 25%; }

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* Empty State */
.empty-state-box {
  padding: 3.5rem 1.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.85rem;
}
.empty-icon-circle {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
}
.empty-svg { width: 32px; height: 32px; }
.empty-heading { font-size: 1.2rem; font-weight: 800; color: var(--text-primary); margin: 0; }
.empty-text { font-size: 0.88rem; color: var(--text-muted); max-width: 500px; margin: 0; line-height: 1.45; }
.empty-inline { padding: 2rem; text-align: center; color: var(--text-muted); font-style: italic; font-size: 0.88rem; }

/* Alert Box */
.alert-box.error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  padding: 1.25rem;
  border-radius: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}
.alert-content { display: flex; align-items: center; gap: 0.85rem; }
.alert-icon { width: 28px; height: 28px; color: #dc2626; flex-shrink: 0; }
.alert-title { font-size: 0.95rem; font-weight: 800; margin: 0; color: #991b1b; }
.alert-desc { font-size: 0.82rem; margin: 0.15rem 0 0 0; color: #b91c1c; }
.btn-outline-danger {
  background: #fff;
  border: 1px solid #f87171;
  color: #dc2626;
  font-weight: 600;
}
.btn-outline-danger:hover { background: #fee2e2; }

/* General Buttons & Typography */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.5rem 0.85rem;
  border-radius: 7px;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.15s ease-in-out;
}
.btn-primary { background: #0284c7; color: #fff; }
.btn-primary:hover { background: #0369a1; }
.btn-outline { background: var(--bg-surface); border-color: var(--border-medium); color: var(--text-primary); }
.btn-outline:hover { background: var(--bg-surface-secondary); border-color: var(--border-strong); }
.btn-ghost { background: transparent; border: none; }
.btn-sm { padding: 0.4rem 0.75rem; font-size: 0.8rem; }
.btn-icon { width: 16px; height: 16px; flex-shrink: 0; }

.font-bold { font-weight: 700; }
.font-semibold { font-weight: 600; }
.font-mono { font-family: monospace; }
.text-primary { color: #0284c7; }
.text-emerald { color: #059669; }
.text-purple { color: #7c3aed; }
.text-amber { color: #d97706; }
.text-muted { color: var(--text-muted); }

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-subtle);
  border-top-color: #0284c7;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* =================================================================== */
/* RESPONSIVE MEDIA QUERIES (320px to 1920px)                          */
/* =================================================================== */
@media (max-width: 1100px) {
  .assignments-grid, .skeleton-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .assignments-grid, .skeleton-grid {
    grid-template-columns: 1fr;
  }
  .summary-metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .modal-kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }
  .header-actions {
    justify-content: flex-start;
  }
  .card-details-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .summary-metrics-grid {
    grid-template-columns: 1fr;
  }
  .modal-kpi-grid {
    grid-template-columns: 1fr;
  }
  .card-footer-actions {
    flex-direction: column;
    align-items: stretch;
  }
  .quick-nav-group {
    display: grid;
    grid-template-columns: 1fr 1fr;
  }
  .btn-action-main {
    width: 100%;
  }
}
</style>
