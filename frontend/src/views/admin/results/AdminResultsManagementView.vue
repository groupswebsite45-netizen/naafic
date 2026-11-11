<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { resultWorkflowService } from '../../../services/resultWorkflowService';
import type {
  ClassResultSummaryItem,
  TeacherSubmissionItem,
  SubmissionReviewDetail,
  ResultFilterOptions,
  DashboardStatistics,
  ClassResultSheetResponse,
  ClassRankingResponse,
  StudentResultReportResponse,
  SubjectPerformanceItem,
  AbsentStudentItem,
} from '../../../types/resultWorkflow';

// =============================================================================
// MAIN NAVIGATION TABS
// =============================================================================
type MainTabType =
  | 'overview'
  | 'submissions'
  | 'class_sheets'
  | 'rankings'
  | 'subject_performance'
  | 'student_reports'
  | 'absent_students';

const activeMainTab = ref<MainTabType>('overview');

// =============================================================================
// GLOBAL FILTERS STATE
// =============================================================================
const filterOptions = ref<ResultFilterOptions>({
  academic_years: ['2026/2027', '2025/2026'],
  selected_academic_year: '2026/2027',
  exam_names: [],
  teachers: [],
  classes: [],
  subjects: [],
});

const selectedAcademicYear = ref<string>('2026/2027');
const selectedEducationLevel = ref<'ALL' | 'PRIMARY' | 'SECONDARY'>('ALL');
const selectedClassId = ref<number | 'ALL'>('ALL');
const selectedExamName = ref<string>('ALL');
const selectedExamType = ref<string>('ALL');
const selectedSubjectId = ref<number | 'ALL'>('ALL');
const selectedTeacherId = ref<number | 'ALL'>('ALL');
const selectedStatus = ref<string>('ALL');

// Notification & Feedback
const error = ref<string | null>(null);
const successMessage = ref<string | null>(null);

// Loading Flags
const loading = ref<boolean>(false);
const dashboardLoading = ref<boolean>(false);
const submissionsLoading = ref<boolean>(false);
const classSheetLoading = ref<boolean>(false);
const rankingsLoading = ref<boolean>(false);
const subjectPerformanceLoading = ref<boolean>(false);
const studentReportLoading = ref<boolean>(false);
const absentStudentsLoading = ref<boolean>(false);

// Download Progress Flags
const downloadingClassPdf = ref<boolean>(false);
const downloadingRankingsPdf = ref<boolean>(false);
const downloadingRankingsExcel = ref<boolean>(false);
const downloadingStudentPdf = ref<boolean>(false);

// =============================================================================
// 1. DASHBOARD 10 REAL-TIME KPIS
// =============================================================================
const dashboardStats = ref<DashboardStatistics>({
  academic_year: '2026/2027',
  exam_name: 'ALL',
  division: 'ALL',
  total_classes_with_students: 0,
  total_eligible_students: 0,
  total_submitted_sheets: 0,
  completed_subjects: 0,
  pending_teacher_submissions: 0,
  students_sat_exam: 0,
  absent_students: 0,
  awaiting_admin_review: 0,
  approved_results: 0,
  published_results: 0,
});

const classesSummary = ref<ClassResultSummaryItem[]>([]);

// =============================================================================
// 2. SUBMISSIONS WORKFLOW STATE
// =============================================================================
const teacherSubmissions = ref<TeacherSubmissionItem[]>([]);
const submissionsSearch = ref<string>('');
const selectedSubmissionsStatusTab = ref<'ALL' | 'SUBMITTED' | 'APPROVED' | 'RELEASED' | 'RETURNED' | 'AWAITING'>('ALL');

// Modals
const showReviewModal = ref<boolean>(false);
const reviewLoading = ref<boolean>(false);
const currentSubmission = ref<SubmissionReviewDetail | null>(null);
const approveLoading = ref<boolean>(false);

// Review Modal Sorting / Filtering
const studentSearch = ref<string>('');
const performanceFilter = ref<string>('ALL');
const sortField = ref<'name' | 'admission' | 'marks' | 'grade'>('name');
const sortOrder = ref<'asc' | 'desc'>('asc');

// Return for Correction Modal
const showReturnModal = ref<boolean>(false);
const returnReason = ref<string>('');
const returnLoading = ref<boolean>(false);
const returnError = ref<string | null>(null);

// Single Release Modal
const showReleaseConfirmModal = ref<boolean>(false);
const releaseLoading = ref<boolean>(false);
const targetSubmissionToRelease = ref<TeacherSubmissionItem | SubmissionReviewDetail | null>(null);

// =============================================================================
// 3. CLASS RESULT SHEETS STATE
// =============================================================================
const selectedSheetClassId = ref<number | null>(null);
const classSheetData = ref<ClassResultSheetResponse | null>(null);
const classSheetSearch = ref<string>('');

// =============================================================================
// 4. CLASS RANKINGS & MERIT LIST STATE
// =============================================================================
const selectedRankingClassId = ref<number | 'ALL'>('ALL');
const classRankingsData = ref<ClassRankingResponse | null>(null);
const rankingSearch = ref<string>('');

// =============================================================================
// 5. SUBJECT PERFORMANCE STATE
// =============================================================================
const subjectPerformanceData = ref<SubjectPerformanceItem[]>([]);
const subjectPerformanceSearch = ref<string>('');

// =============================================================================
// 6. STUDENT RESULT REPORTS STATE
// =============================================================================
const selectedStudentId = ref<number | null>(null);
const studentReportData = ref<StudentResultReportResponse | null>(null);

// =============================================================================
// 7. ABSENT STUDENTS STATE
// =============================================================================
const absentStudentsData = ref<AbsentStudentItem[]>([]);
const absentStudentsSearch = ref<string>('');

// =============================================================================
// COMPUTED FILTERED LISTS
// =============================================================================
const availableFilteredClasses = computed(() => {
  const list = filterOptions.value.classes || [];
  if (selectedEducationLevel.value === 'ALL') return list;
  return list.filter((c: any) => (c.division || '').toUpperCase() === selectedEducationLevel.value);
});

// Watch education level to keep selectedClassId valid
watch(selectedEducationLevel, () => {
  if (selectedClassId.value !== 'ALL') {
    const valid = availableFilteredClasses.value.some((c) => c.id === selectedClassId.value);
    if (!valid) selectedClassId.value = 'ALL';
  }
});

// Filtered Classes Summary for Overview
const filteredClassesSummary = computed(() => {
  let list = classesSummary.value;
  if (selectedEducationLevel.value !== 'ALL') {
    const validIds = new Set(availableFilteredClasses.value.map((c) => c.id));
    list = list.filter((c) => validIds.has(c.class_id));
  }
  if (selectedClassId.value !== 'ALL') {
    list = list.filter((c) => c.class_id === selectedClassId.value);
  }
  return list;
});

// Filtered Teacher Submissions
const filteredSubmissions = computed(() => {
  let list = teacherSubmissions.value;

  // Status Tab Filter
  if (selectedSubmissionsStatusTab.value !== 'ALL') {
    if (selectedSubmissionsStatusTab.value === 'SUBMITTED') {
      list = list.filter((s) => ['SUBMITTED', 'UNDER_REVIEW'].includes(s.status));
    } else if (selectedSubmissionsStatusTab.value === 'APPROVED') {
      list = list.filter((s) => s.status === 'APPROVED');
    } else if (selectedSubmissionsStatusTab.value === 'RELEASED') {
      list = list.filter((s) => s.status === 'RELEASED');
    } else if (selectedSubmissionsStatusTab.value === 'RETURNED') {
      list = list.filter((s) => s.status === 'RETURNED');
    } else if (selectedSubmissionsStatusTab.value === 'AWAITING') {
      list = list.filter((s) => ['DRAFT', 'PARTIAL', 'NOT_STARTED'].includes(s.status));
    }
  }

  // Text Search
  if (submissionsSearch.value.trim()) {
    const q = submissionsSearch.value.trim().toLowerCase();
    list = list.filter(
      (s) =>
        s.teacher_name.toLowerCase().includes(q) ||
        s.class_name.toLowerCase().includes(q) ||
        s.subject_name.toLowerCase().includes(q) ||
        s.exam_name.toLowerCase().includes(q)
    );
  }

  return list;
});

// Submissions Quick Count Badges
const submissionsMetrics = computed(() => {
  const all = teacherSubmissions.value;
  return {
    total: all.length,
    submitted: all.filter((s) => ['SUBMITTED', 'UNDER_REVIEW'].includes(s.status)).length,
    approved: all.filter((s) => s.status === 'APPROVED').length,
    published: all.filter((s) => s.status === 'RELEASED').length,
    returned: all.filter((s) => s.status === 'RETURNED').length,
    awaiting: all.filter((s) => ['DRAFT', 'PARTIAL', 'NOT_STARTED'].includes(s.status)).length,
  };
});

// Filtered Students in Class Result Sheet Tab
const filteredClassSheetStudents = computed(() => {
  if (!classSheetData.value || !classSheetData.value.students) return [];
  let list = classSheetData.value.students;
  if (classSheetSearch.value.trim()) {
    const q = classSheetSearch.value.trim().toLowerCase();
    list = list.filter(
      (st) =>
        st.student_name.toLowerCase().includes(q) ||
        st.admission_number.toLowerCase().includes(q)
    );
  }
  return list;
});

// Filtered Rankings in Merit List Tab
const filteredRankings = computed(() => {
  if (!classRankingsData.value || !classRankingsData.value.rankings) return [];
  let list = classRankingsData.value.rankings;
  if (rankingSearch.value.trim()) {
    const q = rankingSearch.value.trim().toLowerCase();
    list = list.filter(
      (r) =>
        r.student_name.toLowerCase().includes(q) ||
        r.admission_number.toLowerCase().includes(q) ||
        r.class_name.toLowerCase().includes(q)
    );
  }
  return list;
});

// Filtered Subject Performance
const filteredSubjectPerformance = computed(() => {
  let list = subjectPerformanceData.value;
  if (subjectPerformanceSearch.value.trim()) {
    const q = subjectPerformanceSearch.value.trim().toLowerCase();
    list = list.filter(
      (item) =>
        item.subject_name.toLowerCase().includes(q) ||
        item.class_name.toLowerCase().includes(q) ||
        item.teacher_name.toLowerCase().includes(q)
    );
  }
  return list;
});

// Filtered Absent Students
const filteredAbsentStudents = computed(() => {
  let list = absentStudentsData.value;
  if (absentStudentsSearch.value.trim()) {
    const q = absentStudentsSearch.value.trim().toLowerCase();
    list = list.filter(
      (item) =>
        item.student_name.toLowerCase().includes(q) ||
        item.admission_number.toLowerCase().includes(q) ||
        item.class_name.toLowerCase().includes(q) ||
        item.subject_name.toLowerCase().includes(q)
    );
  }
  return list;
});

// Processed Students in Admin Review Modal
const processedStudentList = computed(() => {
  if (!currentSubmission.value || !currentSubmission.value.students) return [];
  let list = [...currentSubmission.value.students];
  const passMark = Number(currentSubmission.value.pass_marks || 50);

  if (studentSearch.value.trim()) {
    const q = studentSearch.value.trim().toLowerCase();
    list = list.filter(
      (st) =>
        st.student_name.toLowerCase().includes(q) ||
        st.admission_number.toLowerCase().includes(q) ||
        (st.roll_number && st.roll_number.toLowerCase().includes(q))
    );
  }

  if (performanceFilter.value !== 'ALL') {
    switch (performanceFilter.value) {
      case 'PASSED':
        list = list.filter(
          (st) =>
            st.attendance_status === 'PRESENT' &&
            st.marks_obtained !== null &&
            st.marks_obtained !== undefined &&
            Number(st.marks_obtained) >= passMark
        );
        break;
      case 'FAILED':
        list = list.filter(
          (st) =>
            st.attendance_status !== 'PRESENT' ||
            (st.marks_obtained !== null &&
              st.marks_obtained !== undefined &&
              Number(st.marks_obtained) < passMark)
        );
        break;
      case 'BELOW_PASS':
        list = list.filter(
          (st) =>
            st.attendance_status === 'PRESENT' &&
            st.marks_obtained !== null &&
            st.marks_obtained !== undefined &&
            Number(st.marks_obtained) < passMark
        );
        break;
      case 'HIGHEST':
        list.sort((a, b) => Number(b.marks_obtained ?? -1) - Number(a.marks_obtained ?? -1));
        return list;
      case 'LOWEST':
        list.sort((a, b) => Number(a.marks_obtained ?? 999) - Number(b.marks_obtained ?? 999));
        return list;
    }
  }

  list.sort((a, b) => {
    let comp = 0;
    if (sortField.value === 'name') {
      comp = a.student_name.localeCompare(b.student_name);
    } else if (sortField.value === 'admission') {
      comp = a.admission_number.localeCompare(b.admission_number);
    } else if (sortField.value === 'marks') {
      const mA = a.marks_obtained !== null && a.marks_obtained !== undefined ? Number(a.marks_obtained) : -1;
      const mB = b.marks_obtained !== null && b.marks_obtained !== undefined ? Number(b.marks_obtained) : -1;
      comp = mA - mB;
    } else if (sortField.value === 'grade') {
      comp = (a.grade || '').localeCompare(b.grade || '');
    }
    return sortOrder.value === 'asc' ? comp : -comp;
  });

  return list;
});

// =============================================================================
// API DATA LOADERS
// =============================================================================

async function loadFilterOptions() {
  try {
    const opts = await resultWorkflowService.getFilterOptions(selectedAcademicYear.value);
    filterOptions.value = opts;
    if (opts.academic_years && opts.academic_years.length > 0 && !selectedAcademicYear.value) {
      selectedAcademicYear.value = opts.academic_years[0];
    }
    if (opts.exam_names && opts.exam_names.length > 0) {
      if (!selectedExamName.value) {
        selectedExamName.value = 'ALL';
      }
    }
    // Set default class for Class Sheet if not selected
    if (!selectedSheetClassId.value && opts.classes && opts.classes.length > 0) {
      selectedSheetClassId.value = opts.classes[0].id;
    }
  } catch (err) {
    console.error('Failed to load filter options:', err);
  }
}

async function fetchDashboardStats() {
  dashboardLoading.value = true;
  try {
    const examNameParam = selectedExamName.value || 'ALL';
    const stats = await resultWorkflowService.getDashboardStatistics(
      selectedAcademicYear.value,
      examNameParam,
      selectedEducationLevel.value !== 'ALL' ? selectedEducationLevel.value : undefined
    );
    dashboardStats.value = stats;
  } catch (err) {
    console.error('Failed to load dashboard KPIs:', err);
  } finally {
    dashboardLoading.value = false;
  }
}

async function fetchClassesSummary() {
  try {
    const examNameParam = selectedExamName.value || 'ALL';
    const summaries = await resultWorkflowService.getClassesResultSummary(
      selectedAcademicYear.value,
      examNameParam
    );
    classesSummary.value = summaries;
  } catch (err) {
    console.error('Failed to load classes summary:', err);
  }
}

async function fetchTeacherSubmissions() {
  submissionsLoading.value = true;
  try {
    const params: any = {
      academic_year: selectedAcademicYear.value,
    };
    if (selectedExamName.value !== 'ALL') params.exam_name = selectedExamName.value;
    if (selectedExamType.value !== 'ALL') params.exam_type = selectedExamType.value;
    if (selectedClassId.value !== 'ALL') params.class_id = Number(selectedClassId.value);
    if (selectedSubjectId.value !== 'ALL') params.subject_id = Number(selectedSubjectId.value);
    if (selectedTeacherId.value !== 'ALL') params.teacher_id = Number(selectedTeacherId.value);
    if (selectedStatus.value !== 'ALL') params.status = selectedStatus.value;

    const data = await resultWorkflowService.getTeacherSubmissions(params);
    teacherSubmissions.value = data;
  } catch (err) {
    console.error('Failed to load teacher submissions:', err);
  } finally {
    submissionsLoading.value = false;
  }
}

async function fetchClassResultSheet() {
  if (!selectedSheetClassId.value) return;
  classSheetLoading.value = true;
  try {
    const examNameParam = selectedExamName.value || 'ALL';
    const data = await resultWorkflowService.getClassResultSheet(
      selectedSheetClassId.value,
      selectedAcademicYear.value,
      examNameParam
    );
    classSheetData.value = data;
  } catch (err: any) {
    console.error('Failed to load class result sheet:', err);
  } finally {
    classSheetLoading.value = false;
  }
}

async function fetchClassRankings() {
  rankingsLoading.value = true;
  try {
    const examNameParam = selectedExamName.value || 'ALL';
    const targetClassId = selectedRankingClassId.value !== 'ALL' ? Number(selectedRankingClassId.value) : 0;
    const data = await resultWorkflowService.getClassRankings(
      targetClassId,
      selectedAcademicYear.value,
      examNameParam,
      selectedEducationLevel.value !== 'ALL' ? selectedEducationLevel.value : undefined
    );
    classRankingsData.value = data;
  } catch (err: any) {
    console.error('Failed to load rankings:', err);
  } finally {
    rankingsLoading.value = false;
  }
}

async function fetchSubjectPerformance() {
  subjectPerformanceLoading.value = true;
  try {
    const examNameParam = selectedExamName.value || 'ALL';
    const params: any = {
      academic_year: selectedAcademicYear.value,
      exam_name: examNameParam,
    };
    if (selectedClassId.value !== 'ALL') params.class_id = Number(selectedClassId.value);
    if (selectedSubjectId.value !== 'ALL') params.subject_id = Number(selectedSubjectId.value);
    if (selectedEducationLevel.value !== 'ALL') params.division = selectedEducationLevel.value;

    const data = await resultWorkflowService.getSubjectPerformanceList(params);
    subjectPerformanceData.value = data;
  } catch (err) {
    console.error('Failed to load subject performance:', err);
  } finally {
    subjectPerformanceLoading.value = false;
  }
}

async function fetchStudentReport() {
  if (!selectedStudentId.value) return;
  studentReportLoading.value = true;
  try {
    const examNameParam = selectedExamName.value !== 'ALL' ? selectedExamName.value : undefined;
    const data = await resultWorkflowService.getStudentResultReport(
      selectedStudentId.value,
      selectedAcademicYear.value,
      examNameParam
    );
    studentReportData.value = data;
  } catch (err) {
    console.error('Failed to load student report:', err);
  } finally {
    studentReportLoading.value = false;
  }
}

async function fetchAbsentStudents() {
  absentStudentsLoading.value = true;
  try {
    const examNameParam = selectedExamName.value || 'ALL';
    const params: any = {
      academic_year: selectedAcademicYear.value,
      exam_name: examNameParam,
    };
    if (selectedClassId.value !== 'ALL') params.class_id = Number(selectedClassId.value);
    if (selectedSubjectId.value !== 'ALL') params.subject_id = Number(selectedSubjectId.value);
    if (selectedEducationLevel.value !== 'ALL') params.division = selectedEducationLevel.value;

    const data = await resultWorkflowService.getAbsentStudentsList(params);
    absentStudentsData.value = data;
  } catch (err) {
    console.error('Failed to load absent students list:', err);
  } finally {
    absentStudentsLoading.value = false;
  }
}

// Master Load Data
async function loadData() {
  loading.value = true;
  try {
    await Promise.all([
      fetchDashboardStats(),
      fetchClassesSummary(),
      fetchTeacherSubmissions(),
    ]);

    // Active tab specific fetch
    if (activeMainTab.value === 'class_sheets') {
      await fetchClassResultSheet();
    } else if (activeMainTab.value === 'rankings') {
      await fetchClassRankings();
    } else if (activeMainTab.value === 'subject_performance') {
      await fetchSubjectPerformance();
    } else if (activeMainTab.value === 'absent_students') {
      await fetchAbsentStudents();
    } else if (activeMainTab.value === 'student_reports' && selectedStudentId.value) {
      await fetchStudentReport();
    }
  } finally {
    loading.value = false;
  }
}

// Watch tab change to trigger data load
watch(activeMainTab, async (newTab) => {
  if (newTab === 'class_sheets') {
    if (!selectedSheetClassId.value && filterOptions.value.classes?.length) {
      selectedSheetClassId.value = filterOptions.value.classes[0].id;
    }
    await fetchClassResultSheet();
  } else if (newTab === 'rankings') {
    await fetchClassRankings();
  } else if (newTab === 'subject_performance') {
    await fetchSubjectPerformance();
  } else if (newTab === 'absent_students') {
    await fetchAbsentStudents();
  } else if (newTab === 'student_reports') {
    // If no student selected yet, pick first student from class sheet if available
    if (!selectedStudentId.value && classSheetData.value?.students?.length) {
      selectedStudentId.value = classSheetData.value.students[0].student_id;
    }
    if (selectedStudentId.value) {
      await fetchStudentReport();
    }
  }
});

// =============================================================================
// PDF & EXCEL DOWNLOAD ACTIONS
// =============================================================================

async function handleDownloadClassPdf() {
  if (!selectedSheetClassId.value) return;
  downloadingClassPdf.value = true;
  try {
    const examNameParam = selectedExamName.value || 'ALL';
    await resultWorkflowService.downloadClassResultSheetPdf(
      selectedSheetClassId.value,
      selectedAcademicYear.value,
      examNameParam
    );
    showToast('Class Results PDF downloaded successfully.');
  } catch (err: any) {
    alert(err?.response?.data?.detail || 'Failed to generate Class Result PDF.');
  } finally {
    downloadingClassPdf.value = false;
  }
}

async function handleDownloadRankingsPdf() {
  downloadingRankingsPdf.value = true;
  try {
    const examNameParam = selectedExamName.value || 'ALL';
    const targetClassId = selectedRankingClassId.value !== 'ALL' ? Number(selectedRankingClassId.value) : 0;
    await resultWorkflowService.downloadClassRankingsPdf(
      targetClassId,
      selectedAcademicYear.value,
      examNameParam,
      selectedEducationLevel.value !== 'ALL' ? selectedEducationLevel.value : undefined
    );
    showToast('Class Rankings PDF downloaded successfully.');
  } catch (err: any) {
    alert(err?.response?.data?.detail || 'Failed to download Rankings PDF.');
  } finally {
    downloadingRankingsPdf.value = false;
  }
}

async function handleDownloadRankingsExcel() {
  downloadingRankingsExcel.value = true;
  try {
    const examNameParam = selectedExamName.value || 'ALL';
    const targetClassId = selectedRankingClassId.value !== 'ALL' ? Number(selectedRankingClassId.value) : 0;
    await resultWorkflowService.downloadClassRankingsExcel(
      targetClassId,
      selectedAcademicYear.value,
      examNameParam,
      selectedEducationLevel.value !== 'ALL' ? selectedEducationLevel.value : undefined
    );
    showToast('Class Rankings Excel spreadsheet downloaded successfully.');
  } catch (err: any) {
    alert(err?.response?.data?.detail || 'Failed to export Rankings to Excel.');
  } finally {
    downloadingRankingsExcel.value = false;
  }
}

async function handleDownloadStudentPdf() {
  if (!selectedStudentId.value) return;
  downloadingStudentPdf.value = true;
  try {
    const examNameParam = selectedExamName.value !== 'ALL' ? selectedExamName.value : undefined;
    await resultWorkflowService.downloadStudentReportCardPdf(
      selectedStudentId.value,
      selectedAcademicYear.value,
      examNameParam
    );
    showToast('Student Report Card PDF downloaded successfully.');
  } catch (err: any) {
    alert(err?.response?.data?.detail || 'Failed to download Student Report PDF.');
  } finally {
    downloadingStudentPdf.value = false;
  }
}

// Navigation Helper: Jump directly to student report card
function jumpToStudentReport(studentId: number) {
  selectedStudentId.value = studentId;
  activeMainTab.value = 'student_reports';
  fetchStudentReport();
}

// Navigation Helper: Jump directly to class sheet
function jumpToClassSheet(classId: number) {
  selectedSheetClassId.value = classId;
  activeMainTab.value = 'class_sheets';
  fetchClassResultSheet();
}

// Navigation Helper: Jump directly to class rankings
function jumpToClassRankings(classId: number) {
  selectedRankingClassId.value = classId;
  activeMainTab.value = 'rankings';
  fetchClassRankings();
}

// =============================================================================
// SUBMISSION REVIEW & WORKFLOW ACTIONS (READ-ONLY FOR MARKS)
// =============================================================================

async function openViewResults(submission: TeacherSubmissionItem) {
  reviewLoading.value = true;
  showReviewModal.value = true;
  studentSearch.value = '';
  performanceFilter.value = 'ALL';
  sortField.value = 'name';
  sortOrder.value = 'asc';

  try {
    const detail = await resultWorkflowService.getSubmissionDetail(submission.id);
    currentSubmission.value = detail;
  } catch (err: any) {
    error.value = err?.response?.data?.detail || 'Failed to load student results.';
    showReviewModal.value = false;
  } finally {
    reviewLoading.value = false;
  }
}

async function approveCurrentSubmission() {
  if (!currentSubmission.value) return;
  approveLoading.value = true;
  try {
    const res = await resultWorkflowService.approveSubmission(currentSubmission.value.id);
    currentSubmission.value.status = 'APPROVED';
    showToast(res.message || 'Result sheet approved successfully.');
    await loadData();
  } catch (err: any) {
    alert(err?.response?.data?.detail || 'Failed to approve results.');
  } finally {
    approveLoading.value = false;
  }
}

function openReturnModal() {
  returnReason.value = '';
  returnError.value = null;
  showReturnModal.value = true;
}

async function confirmReturnToTeacher() {
  if (!returnReason.value || returnReason.value.trim().length < 5) {
    returnError.value = 'Please provide a descriptive reason for correction (at least 5 characters).';
    return;
  }
  if (!currentSubmission.value) return;

  returnLoading.value = true;
  returnError.value = null;
  try {
    await resultWorkflowService.returnSubmission(currentSubmission.value.id, returnReason.value.trim());
    showReturnModal.value = false;
    showReviewModal.value = false;
    showToast('Results returned to teacher for correction.');
    await loadData();
  } catch (err: any) {
    returnError.value = err?.response?.data?.detail || 'Failed to return results.';
  } finally {
    returnLoading.value = false;
  }
}

function promptReleaseResults(sub: TeacherSubmissionItem | SubmissionReviewDetail) {
  targetSubmissionToRelease.value = sub;
  showReleaseConfirmModal.value = true;
}

async function confirmReleaseResults() {
  if (!targetSubmissionToRelease.value) return;
  releaseLoading.value = true;
  try {
    const res = await resultWorkflowService.releaseSubmission(targetSubmissionToRelease.value.id);
    showReleaseConfirmModal.value = false;
    if (showReviewModal.value && currentSubmission.value && currentSubmission.value.id === targetSubmissionToRelease.value.id) {
      currentSubmission.value.status = 'RELEASED';
    }
    showToast(res.message || 'Results successfully published to Student Portal.');
    await loadData();
  } catch (err: any) {
    alert(err?.response?.data?.detail || 'Failed to release results.');
  } finally {
    releaseLoading.value = false;
  }
}

// Helpers
function showToast(msg: string) {
  successMessage.value = msg;
  setTimeout(() => {
    successMessage.value = null;
  }, 5000);
}

function resetFilters() {
  selectedClassId.value = 'ALL';
  selectedEducationLevel.value = 'ALL';
  selectedExamType.value = 'ALL';
  selectedTeacherId.value = 'ALL';
  selectedSubjectId.value = 'ALL';
  selectedStatus.value = 'ALL';
  submissionsSearch.value = '';
  selectedExamName.value = 'ALL';
}

function getStatusBadgeClass(statusStr: string) {
  switch ((statusStr || '').toUpperCase()) {
    case 'RELEASED':
    case 'PUBLISHED':
      return 'badge-released';
    case 'APPROVED':
    case 'COMPLETE':
      return 'badge-approved';
    case 'SUBMITTED':
    case 'UNDER_REVIEW':
      return 'badge-submitted';
    case 'RETURNED':
      return 'badge-returned';
    case 'INCOMPLETE':
    case 'PARTIAL':
      return 'badge-incomplete';
    case 'PENDING':
    case 'DRAFT':
    case 'AWAITING':
    default:
      return 'badge-pending';
  }
}

function formatStatus(statusStr: string) {
  switch ((statusStr || '').toUpperCase()) {
    case 'RELEASED':
    case 'PUBLISHED':
      return 'PUBLISHED';
    case 'APPROVED':
      return 'APPROVED';
    case 'SUBMITTED':
    case 'UNDER_REVIEW':
      return 'SUBMITTED FOR REVIEW';
    case 'RETURNED':
      return 'RETURNED FOR CORRECTION';
    case 'DRAFT':
    case 'PARTIAL':
    case 'NOT_STARTED':
      return 'PENDING TEACHER SUBMISSION';
    default:
      return statusStr;
  }
}

// Watchers
watch(selectedAcademicYear, async () => {
  await loadFilterOptions();
  await loadData();
});

watch([selectedExamName, selectedClassId], async () => {
  await loadData();
});

watch([selectedExamType, selectedTeacherId, selectedSubjectId, selectedStatus], async () => {
  await fetchTeacherSubmissions();
});

onMounted(async () => {
  await loadFilterOptions();
  await loadData();
});
</script>

<template>
  <div class="results-management-page">
    <!-- SUCCESS TOAST -->
    <transition name="fade">
      <div v-if="successMessage" class="toast-notification" role="status" aria-live="polite">
        <svg class="toast-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        <span>{{ successMessage }}</span>
      </div>
    </transition>

    <!-- PAGE HEADER -->
    <header class="page-header">
      <div class="header-content">
        <div class="header-titles">
          <div class="badge-pill">
            <svg class="pill-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
            </svg>
            <span>Somroyal EMS • Results Management Center</span>
          </div>
          <h1 class="page-title">Results Management</h1>
          <p class="page-subtitle">Inspect comprehensive results, verify submissions, generate official PDF reports, and publish student scores.</p>
        </div>
        <div class="header-actions">
          <button type="button" class="btn-primary-orange" @click="loadData">
            <svg class="btn-icon" :class="{ 'spin': loading }" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>Refresh Results</span>
          </button>
        </div>
      </div>
    </header>

    <!-- GLOBAL FILTER BAR -->
    <section class="filters-card" aria-label="Global Results Filters">
      <div class="filters-grid">
        <!-- Academic Year -->
        <div class="filter-group">
          <label for="filter-academic-year" class="filter-label">Academic Year</label>
          <select id="filter-academic-year" v-model="selectedAcademicYear" class="filter-select">
            <option v-for="yr in filterOptions.academic_years" :key="yr" :value="yr">
              {{ yr }}
            </option>
          </select>
        </div>

        <!-- Education Level -->
        <div class="filter-group">
          <label for="filter-education-level" class="filter-label">Education Level</label>
          <select id="filter-education-level" v-model="selectedEducationLevel" class="filter-select">
            <option value="ALL">All Levels</option>
            <option value="PRIMARY">Primary (Grade 1 - 8)</option>
            <option value="SECONDARY">Secondary (Form 1 - 4)</option>
          </select>
        </div>

        <!-- Examination -->
        <div class="filter-group">
          <label for="filter-exam" class="filter-label">Examination</label>
          <select id="filter-exam" v-model="selectedExamName" class="filter-select">
            <option value="ALL">All Examinations (Overall)</option>
            <option v-for="ex in filterOptions.exam_names" :key="ex" :value="ex">
              {{ ex }}
            </option>
          </select>
        </div>

        <!-- Class Filter -->
        <div class="filter-group">
          <label for="filter-class" class="filter-label">Class</label>
          <select id="filter-class" v-model="selectedClassId" class="filter-select">
            <option :value="'ALL'">All Classes</option>
            <option v-for="c in availableFilteredClasses" :key="c.id" :value="c.id">
              {{ c.name }}
            </option>
          </select>
        </div>

        <!-- Subject Filter -->
        <div class="filter-group">
          <label for="filter-subject" class="filter-label">Subject</label>
          <select id="filter-subject" v-model="selectedSubjectId" class="filter-select">
            <option :value="'ALL'">All Subjects</option>
            <option v-for="s in filterOptions.subjects" :key="s.id" :value="s.id">
              {{ s.name }}
            </option>
          </select>
        </div>

        <!-- Teacher Filter -->
        <div class="filter-group">
          <label for="filter-teacher" class="filter-label">Teacher</label>
          <select id="filter-teacher" v-model="selectedTeacherId" class="filter-select">
            <option :value="'ALL'">All Teachers</option>
            <option v-for="t in filterOptions.teachers" :key="t.id" :value="t.id">
              {{ t.name }}
            </option>
          </select>
        </div>

        <!-- Reset Button -->
        <div class="filter-group filter-actions">
          <button type="button" class="btn-reset-filters" @click="resetFilters">
            <svg class="btn-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>Reset</span>
          </button>
        </div>
      </div>
    </section>

    <!-- SECTION 2: 10 REAL-TIME POSTGRESQL KPI DASHBOARD CARDS -->
    <section class="kpi-dashboard-grid" aria-label="10 Results Management Statistics">
      <!-- 1. Total Classes with Students -->
      <div class="kpi-box box-classes">
        <div class="kpi-icon-container">
          <svg class="kpi-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
        </div>
        <div class="kpi-details">
          <span class="kpi-title">Classes With Students</span>
          <span class="kpi-number">{{ dashboardStats.total_classes_with_students }}</span>
          <span class="kpi-subtext">Active enrolled streams</span>
        </div>
      </div>

      <!-- 2. Total Eligible Students -->
      <div class="kpi-box box-students">
        <div class="kpi-icon-container">
          <svg class="kpi-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        </div>
        <div class="kpi-details">
          <span class="kpi-title">Eligible Students</span>
          <span class="kpi-number">{{ dashboardStats.total_eligible_students }}</span>
          <span class="kpi-subtext">Registered for assessment</span>
        </div>
      </div>

      <!-- 3. Total Submitted Sheets -->
      <div class="kpi-box box-submitted">
        <div class="kpi-icon-container">
          <svg class="kpi-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div class="kpi-details">
          <span class="kpi-title">Submitted Sheets</span>
          <span class="kpi-number">{{ dashboardStats.total_submitted_sheets }}</span>
          <span class="kpi-subtext">Received from teachers</span>
        </div>
      </div>

      <!-- 4. Completed Subjects -->
      <div class="kpi-box box-completed">
        <div class="kpi-icon-container">
          <svg class="kpi-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div class="kpi-details">
          <span class="kpi-title">Completed Subjects</span>
          <span class="kpi-number">{{ dashboardStats.completed_subjects }}</span>
          <span class="kpi-subtext">Fully evaluated & finalized</span>
        </div>
      </div>

      <!-- 5. Pending Teacher Submissions -->
      <div class="kpi-box box-pending">
        <div class="kpi-icon-container">
          <svg class="kpi-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div class="kpi-details">
          <span class="kpi-title">Pending Submissions</span>
          <span class="kpi-number">{{ dashboardStats.pending_teacher_submissions }}</span>
          <span class="kpi-subtext">Awaiting teacher entry</span>
        </div>
      </div>

      <!-- 6. Students Sat Exam -->
      <div class="kpi-box box-sat">
        <div class="kpi-icon-container">
          <svg class="kpi-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </div>
        <div class="kpi-details">
          <span class="kpi-title">Students Sat Exam</span>
          <span class="kpi-number">{{ dashboardStats.students_sat_exam }}</span>
          <span class="kpi-subtext">Present with marks</span>
        </div>
      </div>

      <!-- 7. Absent Students -->
      <div class="kpi-box box-absent">
        <div class="kpi-icon-container">
          <svg class="kpi-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div class="kpi-details">
          <span class="kpi-title">Absent Students</span>
          <span class="kpi-number">{{ dashboardStats.absent_students }}</span>
          <span class="kpi-subtext">Officially excused/absent</span>
        </div>
      </div>

      <!-- 8. Results Awaiting Admin Review -->
      <div class="kpi-box box-review">
        <div class="kpi-icon-container">
          <svg class="kpi-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
        </div>
        <div class="kpi-details">
          <span class="kpi-title">Awaiting Review</span>
          <span class="kpi-number">{{ dashboardStats.awaiting_admin_review }}</span>
          <span class="kpi-subtext">In admin queue</span>
        </div>
      </div>

      <!-- 9. Approved Results -->
      <div class="kpi-box box-approved">
        <div class="kpi-icon-container">
          <svg class="kpi-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <div class="kpi-details">
          <span class="kpi-title">Approved Results</span>
          <span class="kpi-number">{{ dashboardStats.approved_results }}</span>
          <span class="kpi-subtext">Ready for publication</span>
        </div>
      </div>

      <!-- 10. Published Results -->
      <div class="kpi-box box-published">
        <div class="kpi-icon-container">
          <svg class="kpi-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
        </div>
        <div class="kpi-details">
          <span class="kpi-title">Published Results</span>
          <span class="kpi-number">{{ dashboardStats.published_results }}</span>
          <span class="kpi-subtext">Live on Student Portal</span>
        </div>
      </div>
    </section>

    <!-- SECTION 13: NAVIGATION TABS BAR -->
    <nav class="results-tab-bar" aria-label="Results Management Navigation">
      <button
        type="button"
        class="tab-link"
        :class="{ active: activeMainTab === 'overview' }"
        @click="activeMainTab = 'overview'"
      >
        <svg class="tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
        </svg>
        <span>Overview</span>
      </button>

      <button
        type="button"
        class="tab-link"
        :class="{ active: activeMainTab === 'submissions' }"
        @click="activeMainTab = 'submissions'"
      >
        <svg class="tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <span>All Submissions</span>
        <span class="tab-badge badge-navy">{{ teacherSubmissions.length }}</span>
      </button>

      <button
        type="button"
        class="tab-link"
        :class="{ active: activeMainTab === 'class_sheets' }"
        @click="activeMainTab = 'class_sheets'"
      >
        <svg class="tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <span>Class Result Sheets</span>
      </button>

      <button
        type="button"
        class="tab-link"
        :class="{ active: activeMainTab === 'rankings' }"
        @click="activeMainTab = 'rankings'"
      >
        <svg class="tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
        </svg>
        <span>Class Rankings & Merit List</span>
      </button>

      <button
        type="button"
        class="tab-link"
        :class="{ active: activeMainTab === 'subject_performance' }"
        @click="activeMainTab = 'subject_performance'"
      >
        <svg class="tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <span>Subject Performance</span>
      </button>

      <button
        type="button"
        class="tab-link"
        :class="{ active: activeMainTab === 'student_reports' }"
        @click="activeMainTab = 'student_reports'"
      >
        <svg class="tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
        <span>Student Reports</span>
      </button>

      <button
        type="button"
        class="tab-link"
        :class="{ active: activeMainTab === 'absent_students' }"
        @click="activeMainTab = 'absent_students'"
      >
        <svg class="tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
        </svg>
        <span>Absent Students</span>
        <span v-if="dashboardStats.absent_students > 0" class="tab-badge badge-orange">{{ dashboardStats.absent_students }}</span>
      </button>
    </nav>

    <!-- ========================================================================= -->
    <!-- TAB 1: OVERVIEW SECTION -->
    <!-- ========================================================================= -->
    <section v-if="activeMainTab === 'overview'" class="tab-content overview-tab">
      <div class="content-card">
        <div class="card-header-flex">
          <div>
            <h2 class="card-heading">Class Completion & Publication Progress</h2>
            <p class="card-subheading">Track evaluation status, completion ratios, and result availability across school classes.</p>
          </div>
        </div>

        <div v-if="filteredClassesSummary.length === 0" class="empty-state">
          <svg class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
          <p class="empty-title">No class result records found for the selected filter.</p>
          <p class="empty-desc">Try selecting another academic year, examination, or education level.</p>
        </div>

        <div v-else class="classes-grid">
          <div v-for="c in filteredClassesSummary" :key="c.class_id" class="class-card">
            <div class="class-card-header">
              <div>
                <h3 class="class-card-title">{{ c.class_name }}</h3>
                <span class="class-card-code">{{ c.class_code }}</span>
              </div>
              <span class="status-badge" :class="getStatusBadgeClass(c.status)">
                {{ formatStatus(c.status) }}
              </span>
            </div>

            <div class="progress-bar-container">
              <div class="progress-bar-fill" :style="{ width: `${c.progress_percent || 0}%` }" />
            </div>
            <div class="progress-label-row">
              <span>Evaluation Progress</span>
              <strong>{{ c.progress_percent || 0 }}%</strong>
            </div>

            <div class="class-stats-grid">
              <div class="c-stat">
                <span class="c-stat-lbl">Students</span>
                <span class="c-stat-val">{{ c.students_count }}</span>
              </div>
              <div class="c-stat">
                <span class="c-stat-lbl">Subjects</span>
                <span class="c-stat-val">{{ c.subjects_count }}</span>
              </div>
              <div class="c-stat">
                <span class="c-stat-lbl">Complete</span>
                <span class="c-stat-val text-success">{{ c.complete_subjects_count || 0 }}</span>
              </div>
              <div class="c-stat">
                <span class="c-stat-lbl">Pending</span>
                <span class="c-stat-val text-orange">{{ c.pending_subjects_count || 0 }}</span>
              </div>
            </div>

            <div class="class-card-footer">
              <button type="button" class="btn-card-action" @click="jumpToClassSheet(c.class_id)">
                View Result Sheet
              </button>
              <button type="button" class="btn-card-action btn-card-secondary" @click="jumpToClassRankings(c.class_id)">
                Rankings
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ========================================================================= -->
    <!-- TAB 2: ALL SUBMISSIONS & TEACHER MARKS REVIEW -->
    <!-- ========================================================================= -->
    <section v-if="activeMainTab === 'submissions'" class="tab-content submissions-tab">
      <!-- Status Tabs Row -->
      <div class="submissions-subtabs">
        <button
          type="button"
          class="subtab-btn"
          :class="{ active: selectedSubmissionsStatusTab === 'ALL' }"
          @click="selectedSubmissionsStatusTab = 'ALL'"
        >
          All Sheets ({{ submissionsMetrics.total }})
        </button>
        <button
          type="button"
          class="subtab-btn"
          :class="{ active: selectedSubmissionsStatusTab === 'SUBMITTED' }"
          @click="selectedSubmissionsStatusTab = 'SUBMITTED'"
        >
          Awaiting Review ({{ submissionsMetrics.submitted }})
        </button>
        <button
          type="button"
          class="subtab-btn"
          :class="{ active: selectedSubmissionsStatusTab === 'APPROVED' }"
          @click="selectedSubmissionsStatusTab = 'APPROVED'"
        >
          Approved ({{ submissionsMetrics.approved }})
        </button>
        <button
          type="button"
          class="subtab-btn"
          :class="{ active: selectedSubmissionsStatusTab === 'RELEASED' }"
          @click="selectedSubmissionsStatusTab = 'RELEASED'"
        >
          Published ({{ submissionsMetrics.published }})
        </button>
        <button
          type="button"
          class="subtab-btn"
          :class="{ active: selectedSubmissionsStatusTab === 'RETURNED' }"
          @click="selectedSubmissionsStatusTab = 'RETURNED'"
        >
          Returned ({{ submissionsMetrics.returned }})
        </button>
        <button
          type="button"
          class="subtab-btn"
          :class="{ active: selectedSubmissionsStatusTab === 'AWAITING' }"
          @click="selectedSubmissionsStatusTab = 'AWAITING'"
        >
          Pending Teacher ({{ submissionsMetrics.awaiting }})
        </button>
      </div>

      <div class="content-card">
        <div class="table-toolbar">
          <div class="search-input-wrap">
            <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              v-model="submissionsSearch"
              type="text"
              class="toolbar-search-input"
              placeholder="Search by teacher, class, subject, or exam..."
            />
          </div>
          <span class="showing-count">Showing <strong>{{ filteredSubmissions.length }}</strong> submissions</span>
        </div>

        <div v-if="submissionsLoading" class="loading-state">
          <div class="spinner" />
          <p>Loading teacher result sheets from database...</p>
        </div>

        <div v-else-if="filteredSubmissions.length === 0" class="empty-state">
          <p class="empty-title">No submissions match the selected filter criteria.</p>
        </div>

        <div v-else class="table-responsive" tabindex="0" role="region" aria-label="Submitted exam result sheets table">
          <table class="data-table">
            <thead>
              <tr>
                <th>Status</th>
                <th>Subject</th>
                <th>Class</th>
                <th>Teacher</th>
                <th>Completion</th>
                <th>Submitted Date</th>
                <th class="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="sub in filteredSubmissions" :key="sub.id">
                <td>
                  <span class="status-badge" :class="getStatusBadgeClass(sub.status)">
                    {{ formatStatus(sub.status) }}
                  </span>
                </td>
                <td>
                  <strong>{{ sub.subject_name }}</strong>
                  <div class="small-subtext">{{ sub.exam_name }}</div>
                </td>
                <td>{{ sub.class_name }}</td>
                <td>{{ sub.teacher_name }}</td>
                <td>
                  <div class="completion-pill">
                    <strong>{{ sub.completed_students }}</strong> / {{ sub.expected_students }}
                    <span v-if="(sub.absent_students ?? 0) > 0" class="text-orange">({{ sub.absent_students }} abs)</span>
                  </div>
                </td>
                <td>
                  <span v-if="sub.submitted_at">{{ new Date(sub.submitted_at).toLocaleDateString() }}</span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td class="text-right">
                  <button
                    type="button"
                    class="btn-action-primary"
                    @click="openViewResults(sub)"
                  >
                    Review Sheet
                  </button>
                  <button
                    v-if="sub.status === 'APPROVED'"
                    type="button"
                    class="btn-action-publish"
                    @click="promptReleaseResults(sub)"
                  >
                    Publish
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ========================================================================= -->
    <!-- TAB 3: CLASS RESULT SHEETS & PDF DOWNLOAD -->
    <!-- ========================================================================= -->
    <section v-if="activeMainTab === 'class_sheets'" class="tab-content class-sheets-tab">
      <div class="content-card">
        <div class="sheet-toolbar-row">
          <div class="class-picker-group">
            <label for="sheet-class-select" class="picker-label">Select Class:</label>
            <select
              id="sheet-class-select"
              v-model="selectedSheetClassId"
              class="filter-select picker-select"
              @change="fetchClassResultSheet"
            >
              <option v-for="c in availableFilteredClasses" :key="c.id" :value="c.id">
                {{ c.name }}
              </option>
            </select>
          </div>

          <div class="sheet-actions-group">
            <div class="search-input-wrap">
              <input
                v-model="classSheetSearch"
                type="text"
                class="toolbar-search-input"
                placeholder="Filter student in sheet..."
              />
            </div>
            <button
              type="button"
              class="btn-primary-orange"
              :disabled="downloadingClassPdf || !classSheetData"
              @click="handleDownloadClassPdf"
            >
              <svg class="btn-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>{{ downloadingClassPdf ? 'Generating PDF...' : 'Download Class PDF' }}</span>
            </button>
          </div>
        </div>

        <div v-if="classSheetLoading" class="loading-state">
          <div class="spinner" />
          <p>Loading Class Result Sheet...</p>
        </div>

        <div v-else-if="!classSheetData || classSheetData.students.length === 0" class="empty-state">
          <p class="empty-title">No student result records found for this class.</p>
        </div>

        <div v-else class="sheet-container">
          <!-- Class Summary Statistics Bar -->
          <div class="sheet-summary-banner">
            <div class="summary-metric">
              <span class="metric-lbl">Registered</span>
              <strong class="metric-val">{{ classSheetData.class_summary.registered_students }}</strong>
            </div>
            <div class="summary-metric">
              <span class="metric-lbl">Sat Exam</span>
              <strong class="metric-val">{{ classSheetData.class_summary.sat_exam_students }}</strong>
            </div>
            <div class="summary-metric">
              <span class="metric-lbl">Absent</span>
              <strong class="metric-val text-orange">{{ classSheetData.class_summary.absent_students }}</strong>
            </div>
            <div class="summary-metric">
              <span class="metric-lbl">Passed</span>
              <strong class="metric-val text-success">{{ classSheetData.class_summary.passed_students }} ({{ classSheetData.class_summary.pass_percentage }}%)</strong>
            </div>
            <div class="summary-metric">
              <span class="metric-lbl">Failed</span>
              <strong class="metric-val text-danger">{{ classSheetData.class_summary.failed_students }}</strong>
            </div>
            <div class="summary-metric">
              <span class="metric-lbl">Class Average</span>
              <strong class="metric-val">{{ classSheetData.class_summary.class_average_percentage }}%</strong>
            </div>
            <div class="summary-metric">
              <span class="metric-lbl">High / Low Score</span>
              <strong class="metric-val">{{ classSheetData.class_summary.highest_total }} / {{ classSheetData.class_summary.lowest_total }}</strong>
            </div>
          </div>

          <!-- Full Student Matrix Table -->
          <div class="table-responsive matrix-table-wrap" tabindex="0" role="region" aria-label="Class result matrix table">
            <table class="data-table matrix-table">
              <thead>
                <tr>
                  <th class="sticky-col col-rank">Rank</th>
                  <th class="sticky-col col-adm">Adm No</th>
                  <th class="sticky-col col-name">Student Name</th>
                  <th class="col-gen">Gen</th>
                  <th
                    v-for="s in classSheetData.subjects"
                    :key="s.id"
                    class="col-subj"
                    :title="s.name"
                  >
                    {{ s.code || s.name.slice(0, 6) }}
                  </th>
                  <th class="col-total">Total</th>
                  <th class="col-max">Max</th>
                  <th class="col-pct">%</th>
                  <th class="col-grade">Grade</th>
                  <th class="col-status">Status</th>
                  <th class="text-right">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="std in filteredClassSheetStudents" :key="std.student_id">
                  <td class="sticky-col col-rank">
                    <span class="rank-badge" :class="{ 'top-three': std.rank <= 3 }">
                      {{ std.rank }}
                    </span>
                  </td>
                  <td class="sticky-col col-adm">{{ std.admission_number }}</td>
                  <td class="sticky-col col-name">
                    <strong>{{ std.student_name }}</strong>
                  </td>
                  <td class="col-gen text-center">{{ (std.gender || '-').charAt(0) }}</td>

                  <!-- Subject Marks -->
                  <td
                    v-for="s in classSheetData.subjects"
                    :key="s.id"
                    class="col-subj text-center"
                  >
                    <template v-if="std.subject_marks[String(s.id)]">
                      <span v-if="std.subject_marks[String(s.id)].is_absent" class="badge-absent-pill">
                        ABS
                      </span>
                      <span
                        v-else-if="std.subject_marks[String(s.id)].marks_obtained !== null && std.subject_marks[String(s.id)].marks_obtained !== undefined"
                        :class="{ 'text-danger': Number(std.subject_marks[String(s.id)].marks_obtained) < s.pass_marks }"
                      >
                        {{ std.subject_marks[String(s.id)].marks_obtained }}
                      </span>
                      <span v-else class="text-muted">—</span>
                    </template>
                    <span v-else class="text-muted">—</span>
                  </td>

                  <td class="col-total text-center">
                    <strong>{{ std.total_obtained !== null ? std.total_obtained : '—' }}</strong>
                  </td>
                  <td class="col-max text-center">{{ std.total_max }}</td>
                  <td class="col-pct text-center">
                    <strong>{{ std.percentage !== null ? `${std.percentage}%` : '—' }}</strong>
                  </td>
                  <td class="col-grade text-center">
                    <span class="grade-pill">{{ std.grade || '—' }}</span>
                  </td>
                  <td class="col-status text-center">
                    <span
                      class="decision-badge"
                      :class="(std.pass_status as string) === 'PASS' ? 'pass-badge' : ((std.pass_status as string) === 'PENDING' ? 'pending-badge' : ((std.pass_status as string) === 'ABSENT' ? 'absent-badge' : 'fail-badge'))"
                    >
                      {{ std.pass_status }}
                    </span>
                  </td>
                  <td class="text-right">
                    <button
                      type="button"
                      class="btn-row-link"
                      @click="jumpToStudentReport(std.student_id)"
                    >
                      Report
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>

    <!-- ========================================================================= -->
    <!-- TAB 4: CLASS RANKINGS & MERIT LIST (COMPETITION RANKING 1, 2, 2, 4) -->
    <!-- ========================================================================= -->
    <section v-if="activeMainTab === 'rankings'" class="tab-content rankings-tab">
      <div class="content-card">
        <div class="sheet-toolbar-row">
          <div class="class-picker-group">
            <label for="ranking-class-select" class="picker-label">Scope:</label>
            <select
              id="ranking-class-select"
              v-model="selectedRankingClassId"
              class="filter-select picker-select"
              @change="fetchClassRankings"
            >
              <option :value="'ALL'">All Classes (School-Wide)</option>
              <option v-for="c in availableFilteredClasses" :key="c.id" :value="c.id">
                {{ c.name }}
              </option>
            </select>
          </div>

          <div class="sheet-actions-group">
            <div class="search-input-wrap">
              <input
                v-model="rankingSearch"
                type="text"
                class="toolbar-search-input"
                placeholder="Search student in rankings..."
              />
            </div>

            <!-- PDF Download -->
            <button
              type="button"
              class="btn-primary-orange"
              :disabled="downloadingRankingsPdf || !classRankingsData"
              @click="handleDownloadRankingsPdf"
            >
              <svg class="btn-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>{{ downloadingRankingsPdf ? 'Generating PDF...' : 'Download PDF' }}</span>
            </button>

            <!-- Excel Export -->
            <button
              type="button"
              class="btn-success-green"
              :disabled="downloadingRankingsExcel || !classRankingsData"
              @click="handleDownloadRankingsExcel"
            >
              <svg class="btn-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              <span>{{ downloadingRankingsExcel ? 'Exporting...' : 'Export Excel' }}</span>
            </button>
          </div>
        </div>

        <div v-if="rankingsLoading" class="loading-state">
          <div class="spinner" />
          <p>Calculating Competition Merit Rankings...</p>
        </div>

        <div v-else-if="filteredRankings.length === 0" class="empty-state">
          <p class="empty-title">No ranked students found.</p>
        </div>

        <div v-else class="table-responsive" tabindex="0" role="region" aria-label="Student merit rankings table">
          <table class="data-table">
            <thead>
              <tr>
                <th style="width: 70px;">Rank</th>
                <th>Admission No</th>
                <th>Student Full Name</th>
                <th>Gender</th>
                <th>Class</th>
                <th>Completed</th>
                <th>Absent</th>
                <th>Total Marks</th>
                <th>Max Marks</th>
                <th>Percentage</th>
                <th>Grade</th>
                <th>Result Decision</th>
                <th class="text-right">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in filteredRankings" :key="r.student_id" :class="{ 'top-merit-row': r.position <= 3 }">
                <td>
                  <span v-if="r.position !== null && r.position !== undefined" class="merit-rank-badge" :class="`rank-${r.position}`">
                    #{{ r.position }}
                  </span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td>{{ r.admission_number }}</td>
                <td>
                  <strong>{{ r.student_name }}</strong>
                </td>
                <td>{{ (r.gender || '-').charAt(0) }}</td>
                <td>{{ r.class_name }}</td>
                <td>{{ r.completed_subjects }}</td>
                <td>
                  <span :class="{ 'text-orange': r.absent_subjects > 0 }">{{ r.absent_subjects }}</span>
                </td>
                <td>
                  <strong>{{ r.total_marks !== null ? r.total_marks : '—' }}</strong>
                </td>
                <td>{{ r.max_possible_marks || '—' }}</td>
                <td>
                  <strong>{{ r.percentage !== null ? `${r.percentage}%` : '—' }}</strong>
                </td>
                <td>
                  <span class="grade-pill">{{ r.grade || '—' }}</span>
                </td>
                <td>
                  <span class="decision-badge" :class="(r.pass_fail as string) === 'PASS' ? 'pass-badge' : ((r.pass_fail as string) === 'PENDING' ? 'pending-badge' : ((r.pass_fail as string) === 'ABSENT' ? 'absent-badge' : 'fail-badge'))">
                    {{ r.pass_fail }}
                  </span>
                </td>
                <td class="text-right">
                  <button
                    type="button"
                    class="btn-row-link"
                    @click="jumpToStudentReport(r.student_id)"
                  >
                    View Report
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ========================================================================= -->
    <!-- TAB 5: SUBJECT PERFORMANCE -->
    <!-- ========================================================================= -->
    <section v-if="activeMainTab === 'subject_performance'" class="tab-content subject-performance-tab">
      <div class="content-card">
        <div class="table-toolbar">
          <div class="search-input-wrap">
            <input
              v-model="subjectPerformanceSearch"
              type="text"
              class="toolbar-search-input"
              placeholder="Search subject, class, or teacher..."
            />
          </div>
          <span class="showing-count">Showing <strong>{{ filteredSubjectPerformance.length }}</strong> subjects</span>
        </div>

        <div v-if="subjectPerformanceLoading" class="loading-state">
          <div class="spinner" />
          <p>Analyzing Subject Performance...</p>
        </div>

        <div v-else-if="filteredSubjectPerformance.length === 0" class="empty-state">
          <p class="empty-title">No subject performance data available.</p>
        </div>

        <div v-else class="table-responsive" tabindex="0" role="region" aria-label="Subject performance summary table">
          <table class="data-table">
            <thead>
              <tr>
                <th>Subject & Code</th>
                <th>Class</th>
                <th>Assigned Teacher</th>
                <th>Registered</th>
                <th>Sat Exam</th>
                <th>Absent</th>
                <th>Average</th>
                <th>High / Low</th>
                <th>Pass Rate</th>
                <th>Grade Distribution</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in filteredSubjectPerformance" :key="item.exam_id">
                <td>
                  <strong>{{ item.subject_name }}</strong>
                  <div class="small-subtext">{{ item.subject_code }}</div>
                </td>
                <td>{{ item.class_name }}</td>
                <td>{{ item.teacher_name }}</td>
                <td>{{ item.total_registered }}</td>
                <td>{{ item.sat_exam }}</td>
                <td>
                  <span :class="{ 'text-orange': item.absent_count > 0 }">{{ item.absent_count }}</span>
                </td>
                <td>
                  <strong>{{ item.average_marks }} / {{ item.max_marks }}</strong>
                </td>
                <td>{{ item.highest_marks }} / {{ item.lowest_marks }}</td>
                <td>
                  <div class="pass-rate-cell">
                    <strong>{{ item.pass_rate }}%</strong>
                    <div class="mini-bar">
                      <div class="mini-bar-fill" :style="{ width: `${item.pass_rate}%` }" />
                    </div>
                  </div>
                </td>
                <td>
                  <div class="distribution-tags">
                    <span v-if="item.grade_distribution['A+']" class="dist-tag tag-aplus">A+: {{ item.grade_distribution['A+'] }}</span>
                    <span v-if="item.grade_distribution['A']" class="dist-tag tag-a">A: {{ item.grade_distribution['A'] }}</span>
                    <span v-if="item.grade_distribution['B']" class="dist-tag tag-b">B: {{ item.grade_distribution['B'] }}</span>
                    <span v-if="item.grade_distribution['C']" class="dist-tag tag-c">C: {{ item.grade_distribution['C'] }}</span>
                    <span v-if="item.grade_distribution['D']" class="dist-tag tag-d">D: {{ item.grade_distribution['D'] }}</span>
                    <span v-if="item.grade_distribution['F']" class="dist-tag tag-f">F: {{ item.grade_distribution['F'] }}</span>
                  </div>
                </td>
                <td>
                  <span class="status-badge" :class="getStatusBadgeClass(item.submission_status)">
                    {{ formatStatus(item.submission_status) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ========================================================================= -->
    <!-- TAB 6: STUDENT RESULT REPORTS -->
    <!-- ========================================================================= -->
    <section v-if="activeMainTab === 'student_reports'" class="tab-content student-reports-tab">
      <div class="content-card">
        <div class="sheet-toolbar-row">
          <div class="class-picker-group">
            <label for="student-report-select" class="picker-label">Select Student:</label>
            <select
              id="student-report-select"
              v-model="selectedStudentId"
              class="filter-select picker-select"
              @change="fetchStudentReport"
            >
              <option :value="null">-- Choose a student --</option>
              <template v-if="classSheetData">
                <option v-for="st in classSheetData.students" :key="st.student_id" :value="st.student_id">
                  {{ st.student_name }} ({{ st.admission_number }})
                </option>
              </template>
              <template v-else-if="classRankingsData">
                <option v-for="st in classRankingsData.rankings" :key="st.student_id" :value="st.student_id">
                  {{ st.student_name }} ({{ st.admission_number }})
                </option>
              </template>
            </select>
          </div>

          <div v-if="studentReportData" class="sheet-actions-group">
            <button
              type="button"
              class="btn-primary-orange"
              :disabled="downloadingStudentPdf"
              @click="handleDownloadStudentPdf"
            >
              <svg class="btn-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>{{ downloadingStudentPdf ? 'Generating PDF...' : 'Download Student PDF' }}</span>
            </button>
          </div>
        </div>

        <div v-if="studentReportLoading" class="loading-state">
          <div class="spinner" />
          <p>Generating Student Academic Report...</p>
        </div>

        <div v-else-if="!studentReportData" class="empty-state">
          <p class="empty-title">Select a student from the dropdown above to view and download their official report card.</p>
        </div>

        <div v-else class="report-card-view">
          <!-- Student Profile Card -->
          <div class="report-profile-banner">
            <div class="profile-main">
              <h3 class="profile-name">{{ studentReportData.student.student_name }}</h3>
              <div class="profile-meta">
                <span>Admission: <strong>{{ studentReportData.student.admission_number }}</strong></span>
                <span>Class: <strong>{{ studentReportData.class_info.name }}</strong></span>
                <span>Academic Year: <strong>{{ studentReportData.exam_info.academic_year }}</strong></span>
                <span>Exam: <strong>{{ studentReportData.exam_info.name }}</strong></span>
              </div>
            </div>
            <div class="profile-rank-card">
              <span class="rank-title">Class Position</span>
              <strong class="rank-value">Rank {{ studentReportData.overall.rank_in_class }}</strong>
              <span class="rank-total">of {{ studentReportData.overall.class_size }} students</span>
            </div>
          </div>

          <!-- Subject Scores Table -->
          <div class="table-responsive" tabindex="0" role="region" aria-label="Student subject scores table">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Code</th>
                  <th>Subject</th>
                  <th>Assigned Teacher</th>
                  <th>Marks</th>
                  <th>Max</th>
                  <th>Pass</th>
                  <th>%</th>
                  <th>Grade</th>
                  <th>Status</th>
                  <th>Teacher Remarks</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="subj in studentReportData.subjects" :key="subj.subject_id || subj.subject_code">
                  <td>{{ subj.subject_code }}</td>
                  <td><strong>{{ subj.subject_name }}</strong></td>
                  <td>{{ subj.teacher_name }}</td>
                  <td>
                    <span v-if="subj.attendance_status === 'ABSENT'" class="badge-absent-pill">ABS</span>
                    <strong v-else>{{ subj.marks_obtained !== null ? subj.marks_obtained : '—' }}</strong>
                  </td>
                  <td>{{ subj.max_marks }}</td>
                  <td>{{ subj.pass_marks }}</td>
                  <td>{{ subj.percentage !== null ? `${subj.percentage}%` : '—' }}</td>
                  <td><span class="grade-pill">{{ subj.grade }}</span></td>
                  <td>
                    <span class="decision-badge" :class="subj.pass_status === 'PASS' ? 'pass-badge' : 'fail-badge'">
                      {{ subj.pass_status }}
                    </span>
                  </td>
                  <td>{{ subj.remarks }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Overall Summary -->
          <div class="report-overall-grid">
            <div class="overall-stat-card">
              <span class="stat-lbl">Total Marks Obtained</span>
              <strong class="stat-val">{{ studentReportData.overall.total_obtained }} / {{ studentReportData.overall.total_max }}</strong>
            </div>
            <div class="overall-stat-card">
              <span class="stat-lbl">Overall Percentage</span>
              <strong class="stat-val">{{ studentReportData.overall.overall_percentage }}%</strong>
            </div>
            <div class="overall-stat-card">
              <span class="stat-lbl">Overall Grade</span>
              <strong class="stat-val grade-text">{{ studentReportData.overall.overall_grade }}</strong>
            </div>
            <div class="overall-stat-card">
              <span class="stat-lbl">Final Decision</span>
              <strong class="stat-val" :class="studentReportData.overall.pass_status === 'PASS' ? 'text-success' : 'text-danger'">
                {{ studentReportData.overall.pass_status }}
              </strong>
            </div>
          </div>

          <!-- Teacher Remarks & Stamp Box -->
          <div class="report-remarks-box">
            <h4>Official Evaluation Remarks</h4>
            <p>{{ studentReportData.overall.teacher_remarks }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ========================================================================= -->
    <!-- TAB 7: ABSENT STUDENTS TRACKER -->
    <!-- ========================================================================= -->
    <section v-if="activeMainTab === 'absent_students'" class="tab-content absent-students-tab">
      <div class="content-card">
        <div class="table-toolbar">
          <div class="search-input-wrap">
            <input
              v-model="absentStudentsSearch"
              type="text"
              class="toolbar-search-input"
              placeholder="Search student, class, or reason..."
            />
          </div>
          <span class="showing-count">Total Absent Records: <strong>{{ filteredAbsentStudents.length }}</strong></span>
        </div>

        <div v-if="absentStudentsLoading" class="loading-state">
          <div class="spinner" />
          <p>Loading documented absences from database...</p>
        </div>

        <div v-else-if="filteredAbsentStudents.length === 0" class="empty-state">
          <p class="empty-title">No absent students recorded for this examination.</p>
        </div>

        <div v-else class="table-responsive" tabindex="0" role="region" aria-label="Documented absent students table">
          <table class="data-table">
            <thead>
              <tr>
                <th>Admission No</th>
                <th>Student Full Name</th>
                <th>Gender</th>
                <th>Class & Section</th>
                <th>Subject</th>
                <th>Attendance Status</th>
                <th>Documented Absence Reason</th>
                <th>Grievance / Complaint</th>
                <th>Assigned Teacher</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in filteredAbsentStudents" :key="item.result_id">
                <td>{{ item.admission_number }}</td>
                <td><strong>{{ item.student_name }}</strong></td>
                <td>{{ (item.gender || '-').charAt(0) }}</td>
                <td>{{ item.class_name }} {{ item.section ? `(${item.section})` : '' }}</td>
                <td>{{ item.subject_name }}</td>
                <td>
                  <span class="badge-absent-pill">{{ item.attendance_status }}</span>
                </td>
                <td>
                  <div class="reason-cell">
                    {{ item.absence_reason }}
                  </div>
                </td>
                <td>
                  <span v-if="item.complaint" class="text-orange">{{ item.complaint }}</span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td>{{ item.teacher_name }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ========================================================================= -->
    <!-- REVIEW SINGLE SUBMISSION MODAL (READ-ONLY FOR MARKS) -->
    <!-- ========================================================================= -->
    <div v-if="showReviewModal && currentSubmission" class="modal-backdrop" @click.self="showReviewModal = false">
      <div class="review-modal-card" role="dialog" aria-labelledby="review-modal-title">
        <div class="modal-header">
          <div>
            <span class="modal-badge">TEACHER RESULT SUBMISSION</span>
            <h2 id="review-modal-title" class="modal-title">
              {{ currentSubmission.subject_name }} — {{ currentSubmission.class_name }}
            </h2>
            <p class="modal-subtitle">
              Submitted by <strong>{{ currentSubmission.teacher_name }}</strong> for <strong>{{ currentSubmission.exam_name }}</strong> ({{ currentSubmission.academic_year }})
            </p>
          </div>
          <button type="button" class="btn-close-modal" @click="showReviewModal = false">×</button>
        </div>

        <div class="modal-body">
          <div class="review-stats-bar">
            <div class="stat-item">
              <span class="lbl">Students</span>
              <strong>{{ currentSubmission.expected_students }}</strong>
            </div>
            <div class="stat-item">
              <span class="lbl">Sat Exam</span>
              <strong class="text-success">{{ currentSubmission.sat_exam_students }}</strong>
            </div>
            <div class="stat-item">
              <span class="lbl">Absent</span>
              <strong class="text-orange">{{ currentSubmission.absent_students }}</strong>
            </div>
            <div class="stat-item">
              <span class="lbl">Status</span>
              <span class="status-badge" :class="getStatusBadgeClass(currentSubmission.status)">
                {{ formatStatus(currentSubmission.status) }}
              </span>
            </div>
          </div>

          <!-- Student Roster (READ-ONLY) -->
          <div class="table-responsive" tabindex="0" role="region" aria-label="Submission student marks inspection table">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Adm No</th>
                  <th>Student Name</th>
                  <th>Attendance</th>
                  <th>Marks Obtained</th>
                  <th>Max</th>
                  <th>Grade</th>
                  <th>Teacher Remarks</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="st in processedStudentList" :key="st.student_id">
                  <td>{{ st.admission_number }}</td>
                  <td><strong>{{ st.student_name }}</strong></td>
                  <td>
                    <span v-if="st.attendance_status === 'ABSENT'" class="badge-absent-pill">ABSENT</span>
                    <span v-else class="text-success">PRESENT</span>
                  </td>
                  <td>
                    <span v-if="st.attendance_status === 'ABSENT'">—</span>
                    <strong v-else>{{ st.marks_obtained !== null ? st.marks_obtained : '—' }}</strong>
                  </td>
                  <td>{{ st.max_marks }}</td>
                  <td><span class="grade-pill">{{ st.grade || '—' }}</span></td>
                  <td>{{ st.remarks || '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn-cancel" @click="showReviewModal = false">Close</button>
          
          <!-- Return for Correction (Only if not already published) -->
          <button
            v-if="currentSubmission.status !== 'RELEASED'"
            type="button"
            class="btn-return"
            @click="openReturnModal"
          >
            Return to Teacher
          </button>

          <!-- Approve Button -->
          <button
            v-if="['SUBMITTED', 'UNDER_REVIEW'].includes(currentSubmission.status)"
            type="button"
            class="btn-approve"
            :disabled="approveLoading"
            @click="approveCurrentSubmission"
          >
            {{ approveLoading ? 'Approving...' : 'Approve Results' }}
          </button>

          <!-- Publish Button -->
          <button
            v-if="currentSubmission.status === 'APPROVED'"
            type="button"
            class="btn-publish-main"
            @click="promptReleaseResults(currentSubmission)"
          >
            Publish to Students
          </button>
        </div>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- RETURN FOR CORRECTION MODAL -->
    <!-- ========================================================================= -->
    <div v-if="showReturnModal" class="modal-backdrop-sub" @click.self="showReturnModal = false">
      <div class="confirm-dialog" role="dialog">
        <div class="dialog-header">
          <h3 class="dialog-title">Return Results for Correction</h3>
          <p class="dialog-desc">Explain clearly what the teacher needs to correct.</p>
        </div>
        <div class="dialog-body">
          <label for="return-reason" class="filter-label">Correction Reason (Required):</label>
          <textarea
            id="return-reason"
            v-model="returnReason"
            class="return-textarea"
            rows="3"
            placeholder="e.g. Missing marks for 2 students. Please verify and resubmit."
          />
          <div v-if="returnError" class="dialog-error">{{ returnError }}</div>
        </div>
        <div class="dialog-footer">
          <button type="button" class="btn-cancel" @click="showReturnModal = false">Cancel</button>
          <button
            type="button"
            class="btn-confirm-return"
            :disabled="returnLoading"
            @click="confirmReturnToTeacher"
          >
            {{ returnLoading ? 'Returning...' : 'Confirm Return' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- RELEASE CONFIRMATION MODAL -->
    <!-- ========================================================================= -->
    <div v-if="showReleaseConfirmModal" class="modal-backdrop-sub" @click.self="showReleaseConfirmModal = false">
      <div class="confirm-dialog" role="dialog">
        <div class="dialog-header">
          <h3 class="dialog-title">Publish Results to Student Portal?</h3>
          <p class="dialog-desc">Once published, results will become visible immediately to students and guardians.</p>
        </div>
        <div class="dialog-footer">
          <button type="button" class="btn-cancel" @click="showReleaseConfirmModal = false">Cancel</button>
          <button
            type="button"
            class="btn-confirm-release"
            :disabled="releaseLoading"
            @click="confirmReleaseResults"
          >
            {{ releaseLoading ? 'Publishing...' : 'Confirm Publication' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* =============================================================================
   SOMROYAL EMS BRANDING & DESIGN SYSTEM
   Dark Navy: #0f172a, #1e293b
   Somroyal Orange: #ea580c, #f97316
   Light/White: #ffffff, #f8fafc, #f1f5f9
   Borders: #e2e8f0, #cbd5e1
   ============================================================================= */

.results-management-page {
  padding: 1.5rem;
  max-width: 1600px;
  margin: 0 auto;
  min-height: 100dvh;
  box-sizing: border-box;
  font-family: inherit;
  color: #1e293b;
}

/* Header */
.page-header {
  margin-bottom: 1.5rem;
}
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1rem;
}
.header-titles {
  flex: 1;
  min-width: 0;
  max-width: 100%;
}
.badge-pill {
  display: inline-flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.375rem;
  background: #f0fdf4;
  color: #166534;
  border: 1px solid #bbf7d0;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  max-width: 100%;
  white-space: normal;
}
.pill-icon {
  width: 0.875rem;
  height: 0.875rem;
}
.page-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 0.25rem 0;
  letter-spacing: -0.02em;
}
.page-subtitle {
  font-size: 0.9375rem;
  color: #64748b;
  margin: 0;
}

/* Buttons */
.btn-primary-orange {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #ea580c;
  color: #ffffff;
  border: none;
  border-radius: 0.5rem;
  padding: 0.625rem 1.125rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  box-shadow: 0 1px 3px rgba(234, 88, 12, 0.25);
}
.btn-primary-orange:hover:not(:disabled) {
  background: #c2410c;
  box-shadow: 0 2px 6px rgba(234, 88, 12, 0.35);
}
.btn-primary-orange:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-success-green {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #16a34a;
  color: #ffffff;
  border: none;
  border-radius: 0.5rem;
  padding: 0.625rem 1.125rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}
.btn-success-green:hover:not(:disabled) {
  background: #15803d;
}

.btn-icon {
  width: 1.125rem;
  height: 1.125rem;
}
.btn-icon.spin {
  animation: spin 1s linear infinite;
}

/* Filter Card */
.filters-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1rem 1.25rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}
.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 1rem;
  align-items: flex-end;
}
.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}
.filter-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.filter-select {
  height: 2.375rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.5rem;
  padding: 0 0.75rem;
  font-size: 0.875rem;
  color: #0f172a;
  background-color: #f8fafc;
  outline: none;
  transition: border-color 0.15s;
}
.filter-select:focus {
  border-color: #ea580c;
  background-color: #ffffff;
}
.btn-reset-filters {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  height: 2.375rem;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  border-radius: 0.5rem;
  padding: 0 0.875rem;
  color: #64748b;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
}
.btn-reset-filters:hover {
  background: #f1f5f9;
  color: #0f172a;
}

/* 10 KPI Dashboard Cards Grid */
.kpi-dashboard-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 0.875rem;
  margin-bottom: 1.5rem;
}
@media (max-width: 1200px) {
  .kpi-dashboard-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
@media (max-width: 768px) {
  .kpi-dashboard-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.65rem;
  }
}
@media (max-width: 400px) {
  .kpi-dashboard-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.55rem;
  }
}
.kpi-box {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 0.875rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  min-width: 0;
}
.kpi-box:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.06);
}
.kpi-icon-container {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.625rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.kpi-svg {
  width: 1.375rem;
  height: 1.375rem;
}
.kpi-details {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.kpi-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}
.kpi-number {
  font-size: 1.375rem;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.2;
}
.kpi-subtext {
  font-size: 0.6875rem;
  color: #94a3b8;
}

/* Individual KPI Themes */
.box-classes .kpi-icon-container { background: #eff6ff; color: #1d4ed8; }
.box-students .kpi-icon-container { background: #fdf2f8; color: #db2777; }
.box-submitted .kpi-icon-container { background: #f0fdf4; color: #15803d; }
.box-completed .kpi-icon-container { background: #ecfdf5; color: #059669; }
.box-pending .kpi-icon-container { background: #fff7ed; color: #c2410c; }
.box-sat .kpi-icon-container { background: #f5f3ff; color: #7c3aed; }
.box-absent .kpi-icon-container { background: #fef2f2; color: #b91c1c; }
.box-review .kpi-icon-container { background: #fefce8; color: #a16207; }
.box-approved .kpi-icon-container { background: #f0fdfa; color: #0f766e; }
.box-published .kpi-icon-container { background: #f1f5f9; color: #0f172a; }

/* Tabs Bar */
.results-tab-bar {
  display: flex;
  gap: 0.5rem;
  border-bottom: 2px solid #e2e8f0;
  margin-bottom: 1.5rem;
  overflow-x: auto;
  padding-bottom: 0.25rem;
}
.tab-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  min-height: 44px;
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 0.5rem 0.5rem 0 0;
  position: relative;
  transition: all 0.15s ease;
  white-space: nowrap;
  flex: none;
}
.tab-link:hover {
  color: #0f172a;
  background: #f8fafc;
}
.tab-link.active {
  color: #0f172a;
  font-weight: 700;
}
.tab-link.active::after {
  content: '';
  position: absolute;
  bottom: -0.375rem;
  left: 0;
  right: 0;
  height: 3px;
  background: #ea580c;
  border-radius: 3px 3px 0 0;
}
.tab-icon {
  width: 1.125rem;
  height: 1.125rem;
}
.tab-badge {
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.6875rem;
  font-weight: 700;
}
.badge-navy { background: #0f172a; color: #ffffff; }
.badge-orange { background: #ea580c; color: #ffffff; }

/* Content Card */
.content-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 0.875rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}
.card-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}
.card-heading {
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}
.card-subheading {
  font-size: 0.8125rem;
  color: #64748b;
  margin: 0.25rem 0 0 0;
}

/* Classes Progress Grid */
.classes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(260px, 100%), 1fr));
  gap: 1rem;
}
.class-card {
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1rem;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-width: 0;
}
.class-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 0.4rem 0.5rem;
}
.class-card-header > * {
  min-width: 0;
}
.class-card-header .status-badge {
  white-space: normal;
  max-width: 100%;
  text-align: center;
}
.class-card-title {
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}
.class-card-code {
  font-size: 0.75rem;
  color: #64748b;
}
.progress-bar-container {
  height: 6px;
  background: #e2e8f0;
  border-radius: 9999px;
  overflow: hidden;
}
.progress-bar-fill {
  height: 100%;
  background: #ea580c;
  transition: width 0.3s ease;
}
.progress-label-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #64748b;
}
.class-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
  background: #ffffff;
  padding: 0.625rem;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
  text-align: center;
}
.c-stat-lbl {
  font-size: 0.6875rem;
  color: #94a3b8;
  display: block;
}
.c-stat-val {
  font-size: 0.875rem;
  font-weight: 700;
  color: #0f172a;
}
.class-card-footer {
  display: flex;
  gap: 0.5rem;
}
.btn-card-action {
  flex: 1;
  padding: 0.45rem 0.75rem;
  background: #0f172a;
  color: #ffffff;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  text-align: center;
}
.btn-card-action:hover {
  background: #1e293b;
}
.btn-card-secondary {
  background: #e2e8f0;
  color: #0f172a;
}
.btn-card-secondary:hover {
  background: #cbd5e1;
}

/* Submissions Sub-Tabs */
.submissions-subtabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  overflow-x: auto;
}
.subtab-btn {
  padding: 0.45rem 0.875rem;
  border-radius: 9999px;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
}
.subtab-btn.active {
  background: #0f172a;
  color: #ffffff;
  border-color: #0f172a;
}

/* Tables */
.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  gap: 1rem;
}
.sheet-toolbar-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.25rem;
}
.class-picker-group {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem 0.75rem;
  flex: 1 1 220px;
  min-width: 0;
}
.picker-label {
  font-size: 0.875rem;
  font-weight: 700;
  color: #0f172a;
}
.picker-select {
  min-width: 0;
  width: 100%;
  max-width: 260px;
}
.sheet-actions-group {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
}
.search-input-wrap {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1 1 200px;
  min-width: 0;
}
.toolbar-search-input {
  width: 100%;
  min-width: 0;
  height: 2.25rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.5rem;
  padding: 0 0.75rem 0 2rem;
  font-size: 0.8125rem;
  color: #0f172a;
  background: #f8fafc;
  outline: none;
}
.toolbar-search-input:focus {
  border-color: #ea580c;
  background: #ffffff;
}
.search-icon {
  position: absolute;
  left: 0.625rem;
  width: 1rem;
  height: 1rem;
  color: #94a3b8;
}
.showing-count {
  font-size: 0.8125rem;
  color: #64748b;
}

.table-responsive {
  width: 100%;
  overflow-x: auto;
}
.data-table {
  width: 100%;
  min-width: 720px;
  border-collapse: collapse;
  font-size: 0.8125rem;
  text-align: left;
}
.data-table th {
  background: #0f172a;
  color: #ffffff;
  padding: 0.625rem 0.75rem;
  font-weight: 700;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  white-space: nowrap;
}
.data-table td {
  padding: 0.625rem 0.75rem;
  border-bottom: 1px solid #e2e8f0;
  vertical-align: middle;
}
.data-table tr:hover td {
  background-color: #f8fafc;
}
.text-right { text-align: right; }
.text-center { text-align: center; }
.text-success { color: #16a34a; }
.text-orange { color: #ea580c; }
.text-danger { color: #dc2626; }
.text-muted { color: #94a3b8; }
.small-subtext { font-size: 0.6875rem; color: #64748b; }

/* Status Badges */
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.55rem;
  border-radius: 9999px;
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}
.badge-released { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
.badge-approved { background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; }
.badge-submitted { background: #fef3c7; color: #b45309; border: 1px solid #fde68a; }
.badge-returned { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }
.badge-incomplete { background: #ffedd5; color: #c2410c; border: 1px solid #fed7aa; }
.badge-pending { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }

.badge-absent-pill {
  display: inline-block;
  padding: 0.15rem 0.4rem;
  background: #fef2f2;
  color: #b91c1c;
  border: 1px solid #fca5a5;
  border-radius: 0.25rem;
  font-size: 0.6875rem;
  font-weight: 800;
}
.grade-pill {
  display: inline-block;
  padding: 0.15rem 0.4rem;
  background: #f1f5f9;
  color: #0f172a;
  border-radius: 0.25rem;
  font-weight: 800;
  font-size: 0.75rem;
}
.decision-badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.6875rem;
  font-weight: 800;
}
.pass-badge { background: #dcfce7; color: #166534; }
.fail-badge { background: #fee2e2; color: #991b1b; }
.pending-badge { background: #f1f5f9; color: #475569; }
.absent-badge { background: #ffedd5; color: #c2410c; }

/* Action Buttons inside Table */
.btn-action-primary {
  padding: 0.35rem 0.75rem;
  background: #0f172a;
  color: #ffffff;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  margin-right: 0.375rem;
}
.btn-action-primary:hover { background: #1e293b; }
.btn-action-publish {
  padding: 0.35rem 0.75rem;
  background: #16a34a;
  color: #ffffff;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
}
.btn-action-publish:hover { background: #15803d; }
.btn-row-link {
  background: transparent;
  border: none;
  color: #ea580c;
  font-weight: 700;
  font-size: 0.75rem;
  cursor: pointer;
  text-decoration: underline;
}
.btn-row-link:hover { color: #c2410c; }

/* Class Result Sheet Specifics */
.sheet-summary-banner {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 0.75rem;
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 0.625rem;
  padding: 0.875rem 1rem;
  margin-bottom: 1.25rem;
}
.summary-metric {
  display: flex;
  flex-direction: column;
}
.metric-lbl {
  font-size: 0.6875rem;
  color: #64748b;
  text-transform: uppercase;
  font-weight: 700;
}
.metric-val {
  font-size: 1.125rem;
  font-weight: 800;
  color: #0f172a;
}
.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 9999px;
  background: #e2e8f0;
  color: #0f172a;
  font-weight: 800;
  font-size: 0.75rem;
}
.rank-badge.top-three {
  background: #ea580c;
  color: #ffffff;
}

/* Merit List Specifics */
.merit-rank-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 0.375rem;
  font-weight: 800;
  font-size: 0.8125rem;
  background: #f1f5f9;
  color: #0f172a;
}
.top-merit-row {
  background-color: #fffbeb !important;
}
.rank-1 { background: #fef08a; color: #854d0e; }
.rank-2 { background: #e2e8f0; color: #334155; }
.rank-3 { background: #fed7aa; color: #9a3412; }

/* Subject Performance */
.pass-rate-cell {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.mini-bar {
  width: 60px;
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  overflow: hidden;
}
.mini-bar-fill {
  height: 100%;
  background: #16a34a;
}
.distribution-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}
.dist-tag {
  font-size: 0.625rem;
  padding: 0.1rem 0.35rem;
  border-radius: 0.25rem;
  font-weight: 700;
}
.tag-aplus { background: #dcfce7; color: #166534; }
.tag-a { background: #f0fdf4; color: #15803d; }
.tag-b { background: #e0f2fe; color: #0369a1; }
.tag-c { background: #fef3c7; color: #b45309; }
.tag-d { background: #ffedd5; color: #c2410c; }
.tag-f { background: #fee2e2; color: #b91c1c; }

/* Student Report Card View */
.report-profile-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  background: #0f172a;
  color: #ffffff;
  border-radius: 0.75rem;
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.25rem;
}
.profile-name {
  font-size: 1.375rem;
  font-weight: 800;
  margin: 0 0 0.5rem 0;
}
.profile-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1.25rem;
  font-size: 0.8125rem;
  color: #cbd5e1;
}
.profile-rank-card {
  text-align: center;
  background: rgba(255, 255, 255, 0.1);
  padding: 0.75rem 1.25rem;
  border-radius: 0.625rem;
  border: 1px solid rgba(255, 255, 255, 0.15);
}
.rank-title {
  display: block;
  font-size: 0.6875rem;
  color: #ea580c;
  text-transform: uppercase;
  font-weight: 700;
}
.rank-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 900;
  color: #ffffff;
}
.rank-total {
  font-size: 0.6875rem;
  color: #cbd5e1;
}
.report-overall-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
  margin: 1.25rem 0;
}
.overall-stat-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.625rem;
  padding: 0.875rem;
  text-align: center;
}
.stat-lbl {
  font-size: 0.75rem;
  color: #64748b;
  display: block;
  font-weight: 600;
}
.stat-val {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
  margin-top: 0.25rem;
  display: block;
}
.grade-text {
  color: #ea580c;
}
.report-remarks-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.625rem;
  padding: 1rem;
}
.report-remarks-box h4 {
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
  font-weight: 700;
  color: #0f172a;
}
.report-remarks-box p {
  margin: 0;
  font-size: 0.8125rem;
  color: #475569;
}

/* Modals */
.modal-backdrop,
.modal-backdrop-sub {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.65);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}
.review-modal-card {
  background: #ffffff;
  border-radius: 1rem;
  width: 100%;
  max-width: 950px;
  max-height: calc(100dvh - 1.5rem);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}
.modal-header {
  padding: 1.25rem 1.5rem;
  background: #0f172a;
  color: #ffffff;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.modal-badge {
  font-size: 0.6875rem;
  font-weight: 700;
  color: #ea580c;
  text-transform: uppercase;
}
.modal-title {
  margin: 0.25rem 0 0.125rem 0;
  font-size: 1.25rem;
  font-weight: 800;
}
.modal-subtitle {
  margin: 0;
  font-size: 0.8125rem;
  color: #cbd5e1;
}
.btn-close-modal {
  background: transparent;
  border: none;
  color: #ffffff;
  font-size: 1.75rem;
  cursor: pointer;
  line-height: 1;
}
.modal-body {
  padding: 1.25rem 1.5rem;
  overflow-y: auto;
  flex: 1;
}
.review-stats-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem 1.5rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
}
.review-stats-bar .stat-item {
  display: flex;
  flex-direction: column;
}
.review-stats-bar .lbl {
  font-size: 0.6875rem;
  color: #64748b;
  text-transform: uppercase;
}
.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.75rem;
  background: #f8fafc;
}

.confirm-dialog {
  background: #ffffff;
  border-radius: 0.75rem;
  max-width: 480px;
  width: 100%;
  padding: 1.5rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}
.dialog-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.125rem;
  font-weight: 800;
  color: #0f172a;
}
.dialog-desc {
  margin: 0 0 1rem 0;
  font-size: 0.8125rem;
  color: #64748b;
}
.return-textarea {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #cbd5e1;
  border-radius: 0.5rem;
  padding: 0.625rem;
  font-size: 0.875rem;
  color: #0f172a;
  outline: none;
}
.return-textarea:focus { border-color: #ea580c; }
.dialog-error {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: #dc2626;
  font-weight: 600;
}
.dialog-footer {
  margin-top: 1.25rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.625rem;
}
.btn-cancel {
  padding: 0.5rem 1rem;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  color: #475569;
}
.btn-return {
  padding: 0.5rem 1rem;
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #fecaca;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
}
.btn-approve {
  padding: 0.5rem 1.125rem;
  background: #0f172a;
  color: #ffffff;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 700;
  cursor: pointer;
}
.btn-approve:hover { background: #1e293b; }
.btn-publish-main {
  padding: 0.5rem 1.125rem;
  background: #16a34a;
  color: #ffffff;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 700;
  cursor: pointer;
}
.btn-confirm-return {
  padding: 0.5rem 1rem;
  background: #dc2626;
  color: #ffffff;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 700;
  cursor: pointer;
}
.btn-confirm-release {
  padding: 0.5rem 1rem;
  background: #16a34a;
  color: #ffffff;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 700;
  cursor: pointer;
}

/* Loading & Empty States */
.loading-state,
.empty-state {
  padding: 3rem 1.5rem;
  text-align: center;
  color: #64748b;
}
.empty-icon {
  width: 2.5rem;
  height: 2.5rem;
  color: #cbd5e1;
  margin: 0 auto 0.75rem auto;
}
.empty-title {
  font-weight: 700;
  font-size: 0.9375rem;
  color: #334155;
  margin: 0;
}
.empty-desc {
  font-size: 0.8125rem;
  margin: 0.25rem 0 0 0;
}
.spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid #e2e8f0;
  border-top-color: #ea580c;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 0.75rem auto;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Toast */
.toast-notification {
  position: fixed;
  top: 1.5rem;
  right: 1.5rem;
  background: #0f172a;
  color: #ffffff;
  padding: 0.75rem 1.25rem;
  border-radius: 0.5rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  z-index: 2000;
  font-size: 0.875rem;
  font-weight: 600;
}
.toast-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: #10b981;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .results-management-page {
    padding: 1rem 0.75rem;
  }
  .report-overall-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 480px) {
  .content-card {
    padding: 0.9rem;
  }
  .class-stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .modal-backdrop,
  .modal-backdrop-sub {
    padding: 0.5rem;
  }
  .modal-header,
  .modal-body,
  .modal-footer,
  .confirm-dialog {
    padding: 1rem;
  }
  .toast-notification {
    left: 0.75rem;
    right: 0.75rem;
    top: 0.75rem;
  }
}
</style>
