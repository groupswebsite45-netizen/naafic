<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { adminAttendanceService } from '../../../services/adminAttendanceService';
import { adminTeacherAttendanceService } from '../../../services/adminTeacherAttendanceService';
import {
  AdminAttendanceFilterOptionsResponse,
  AdminAttendanceDashboardResponse,
  AdminAttendanceRecordsListResponse,
  AdminClassAttendanceReportResponse,
  AdminAttendanceFrequentAbsenteeItem,
  AbsenceDateDetail,
  AdminClassOption,
  AdminSubjectOption,
  AdminTeacherOption,
} from '../../../types/adminAttendance';
import {
  StudentAttendanceHistoryDetailResponse,
} from '../../../types/attendance';
import {
  TeacherDailyRosterResponse,
  TeacherAttendanceDashboardResponse,
  TeacherAttendanceRecordsResponse,
  StaffAttendanceSummaryResponse,
} from '../../../types/adminTeacherAttendance';

const route = useRoute();

// Top-Level Main Section Tab: Student Attendance vs. Teacher Attendance
type MainSection = 'student' | 'teacher';
const mainSection = ref<MainSection>('student');

// =========================================================================
// 1. STUDENT ATTENDANCE STATE
// =========================================================================
type StudentTabType = 'dashboard' | 'class-report' | 'frequent-absences' | 'records';
const studentActiveTab = ref<StudentTabType>('dashboard');

// Student Filter Options & Selections
const filterOptions = ref<AdminAttendanceFilterOptionsResponse | null>(null);
const selectedAcademicYear = ref<string>('');
const selectedMonth = ref<number | ''>('');
const selectedClassId = ref<number | ''>('');
const selectedSubjectId = ref<number | ''>('');
const selectedTeacherId = ref<number | ''>('');
const selectedAttendanceDate = ref<string>('');
const selectedStatus = ref<string>('ALL');
const searchQuery = ref<string>('');
const absenceThreshold = ref<number>(3);

// Dynamic Class, Subject & Teacher Dropdown Lists
const dynamicSubjects = ref<AdminSubjectOption[]>([]);
const dynamicTeachers = ref<AdminTeacherOption[]>([]);

const availableClasses = computed<AdminClassOption[]>(() => {
  if (!filterOptions.value?.classes) return [];
  if (!selectedAcademicYear.value) return filterOptions.value.classes;
  const yr = selectedAcademicYear.value.trim();
  const yrVariants = [yr, yr.replace('/', '-'), yr.replace('-', '/')];
  return filterOptions.value.classes.filter(
    (c) => !c.academic_year || yrVariants.includes(c.academic_year.trim())
  );
});

const hasRecordsOnSelectedDate = computed<boolean>(() => {
  if (!selectedAttendanceDate.value) return true;
  if (!classReportData.value) return false;
  const sum = classReportData.value.summary;
  return (sum.present_count + sum.absent_count + sum.late_count) > 0;
});

// Student Data states
const isLoadingOptions = ref<boolean>(true);
const isLoadingDashboard = ref<boolean>(false);
const isLoadingClassReport = ref<boolean>(false);
const isLoadingFrequent = ref<boolean>(false);
const isLoadingRecords = ref<boolean>(false);

// Downloads
const isDownloadingExcel = ref<boolean>(false);
const isDownloadingPdf = ref<boolean>(false);

// Student Dashboard & Reports Data
const dashboardData = ref<AdminAttendanceDashboardResponse | null>(null);
const classReportData = ref<AdminClassAttendanceReportResponse | null>(null);
const frequentAbsentees = ref<AdminAttendanceFrequentAbsenteeItem[]>([]);
const recordsResponse = ref<AdminAttendanceRecordsListResponse | null>(null);
const recordsPage = ref<number>(1);
const recordsPageSize = ref<number>(25);

// Student Absence Detail Inspection Modal
const inspectedStudent = ref<{
  name: string;
  admission_number: string;
  class_name: string;
  absence_dates: AbsenceDateDetail[];
} | null>(null);

// Student Subject Attendance Breakdown Modal
const selectedStudentBreakdown = ref<StudentAttendanceHistoryDetailResponse | null>(null);
const isLoadingBreakdown = ref<boolean>(false);
const isBreakdownModalOpen = ref<boolean>(false);

// =========================================================================
// 2. TEACHER ATTENDANCE STATE
// =========================================================================
type TeacherTabType = 'daily' | 'dashboard' | 'summary' | 'records';
const teacherActiveTab = ref<TeacherTabType>('daily');

const selectedTeacherDate = ref<string>(getTodayDateString());
const selectedTeacherStatus = ref<string>('ALL');
const teacherSearchQuery = ref<string>('');
const dailyTeacherSearch = ref<string>('');
const selectedTeacherMonth = ref<number | ''>('');

const teacherRoster = ref<TeacherDailyRosterResponse | null>(null);

const filteredDailyTeachers = computed(() => {
  if (!teacherRoster.value?.teachers) return [];
  const q = dailyTeacherSearch.value.trim().toLowerCase();
  if (!q) return teacherRoster.value.teachers;
  return teacherRoster.value.teachers.filter((t) =>
    t.teacher_name.toLowerCase().includes(q) ||
    t.teacher_number.toLowerCase().includes(q) ||
    (t.email && t.email.toLowerCase().includes(q)) ||
    (t.phone && t.phone.toLowerCase().includes(q))
  );
});
const teacherDashboardData = ref<TeacherAttendanceDashboardResponse | null>(null);
const staffSummaryData = ref<StaffAttendanceSummaryResponse | null>(null);
const teacherRecordsResponse = ref<TeacherAttendanceRecordsResponse | null>(null);
const teacherRecordsPage = ref<number>(1);
const teacherRecordsPageSize = ref<number>(25);

const isLoadingTeacherRoster = ref<boolean>(false);
const isSavingTeacherAttendance = ref<boolean>(false);
const isLoadingTeacherDashboard = ref<boolean>(false);
const isLoadingStaffSummary = ref<boolean>(false);
const isLoadingTeacherRecords = ref<boolean>(false);

const isDownloadingTeacherExcel = ref<boolean>(false);
const isDownloadingTeacherPdf = ref<boolean>(false);

// Toast notification
const toastMessage = ref<{ type: 'success' | 'error'; text: string } | null>(null);

function showToast(text: string, type: 'success' | 'error' = 'success') {
  toastMessage.value = { text, type };
  setTimeout(() => {
    toastMessage.value = null;
  }, 4000);
}

function getTodayDateString(): string {
  const d = new Date();
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

// Formatters
function formatDate(dStr: string | null | undefined): string {
  if (!dStr) return '—';
  try {
    const parts = dStr.split('-');
    if (parts.length === 3) {
      const d = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    }
    return dStr;
  } catch {
    return dStr;
  }
}

function formatShortDate(dStr: string): string {
  if (!dStr) return '';
  const parts = dStr.split('-');
  if (parts.length === 3) {
    return `${parts[1]}/${parts[2]}`;
  }
  return dStr;
}

// =========================================================================
// INITIAL LOAD
// =========================================================================
onMounted(async () => {
  if (route.query.section === 'teacher' || route.query.tab === 'teacher') {
    mainSection.value = 'teacher';
  }
  await loadFilterOptions();
  await loadDashboard();
  // Ensure teacher daily roster is pre-loaded so teachers display immediately
  await loadTeacherDailyRoster();
});

// Watch main section switcher
watch(mainSection, async (newVal) => {
  if (newVal === 'student') {
    if (studentActiveTab.value === 'dashboard') await loadDashboard();
    else if (studentActiveTab.value === 'class-report') await loadClassReport();
    else if (studentActiveTab.value === 'frequent-absences') await loadFrequentAbsentees();
    else if (studentActiveTab.value === 'records') await loadRecords(1);
  } else {
    if (teacherActiveTab.value === 'daily') await loadTeacherDailyRoster();
    else if (teacherActiveTab.value === 'dashboard') await loadTeacherDashboard();
    else if (teacherActiveTab.value === 'summary') await loadStaffSummary();
    else if (teacherActiveTab.value === 'records') await loadTeacherRecords(1);
  }
});

// =========================================================================
// STUDENT METHODS
// =========================================================================
async function updateDynamicFilters() {
  try {
    const opts = await adminAttendanceService.getFilterOptions({
      academic_year: selectedAcademicYear.value || undefined,
      class_id: selectedClassId.value !== '' ? Number(selectedClassId.value) : undefined,
      subject_id: selectedSubjectId.value !== '' ? Number(selectedSubjectId.value) : undefined,
    });
    dynamicSubjects.value = opts.subjects;
    dynamicTeachers.value = opts.teachers;

    // Validate selectedSubjectId against dynamicSubjects
    if (selectedSubjectId.value !== '') {
      const exists = dynamicSubjects.value.some((s) => s.id === Number(selectedSubjectId.value));
      if (!exists) {
        selectedSubjectId.value = '';
      }
    }

    // Validate selectedTeacherId against dynamicTeachers
    if (selectedTeacherId.value !== '') {
      const exists = dynamicTeachers.value.some((t) => t.id === Number(selectedTeacherId.value));
      if (!exists) {
        selectedTeacherId.value = '';
      }
    }
  } catch (err: any) {
    console.error('Failed to update dynamic attendance filters:', err);
  }
}

async function loadFilterOptions() {
  isLoadingOptions.value = true;
  try {
    const opts = await adminAttendanceService.getFilterOptions();
    filterOptions.value = opts;
    if (opts.academic_years.length > 0) {
      selectedAcademicYear.value = opts.academic_years[0];
    }
    const avail = availableClasses.value;
    if (avail.length > 0) {
      selectedClassId.value = avail[0].id;
    }
    await updateDynamicFilters();
  } catch (err: any) {
    showToast(err?.response?.data?.detail || 'Failed to load attendance filter options', 'error');
  } finally {
    isLoadingOptions.value = false;
  }
}

async function loadDashboard() {
  isLoadingDashboard.value = true;
  try {
    const data = await adminAttendanceService.getDashboard({
      academic_year: selectedAcademicYear.value || undefined,
      month: selectedMonth.value !== '' ? Number(selectedMonth.value) : undefined,
      class_id: selectedClassId.value !== '' ? Number(selectedClassId.value) : undefined,
      subject_id: selectedSubjectId.value !== '' ? Number(selectedSubjectId.value) : undefined,
      teacher_id: selectedTeacherId.value !== '' ? Number(selectedTeacherId.value) : undefined,
      date: selectedAttendanceDate.value || undefined,
      threshold: absenceThreshold.value,
    });
    dashboardData.value = data;
    frequentAbsentees.value = data.frequent_absentees;
  } catch (err: any) {
    showToast(err?.response?.data?.detail || 'Failed to load attendance dashboard', 'error');
  } finally {
    isLoadingDashboard.value = false;
  }
}

async function loadClassReport() {
  if (!selectedClassId.value) return;
  isLoadingClassReport.value = true;
  try {
    const data = await adminAttendanceService.getClassReport(Number(selectedClassId.value), {
      academic_year: selectedAcademicYear.value || undefined,
      month: selectedMonth.value !== '' ? Number(selectedMonth.value) : undefined,
      subject_id: selectedSubjectId.value !== '' ? Number(selectedSubjectId.value) : undefined,
      teacher_id: selectedTeacherId.value !== '' ? Number(selectedTeacherId.value) : undefined,
      date: selectedAttendanceDate.value || undefined,
    });
    classReportData.value = data;
  } catch (err: any) {
    showToast(err?.response?.data?.detail || 'Failed to load class attendance report', 'error');
  } finally {
    isLoadingClassReport.value = false;
  }
}

async function loadFrequentAbsentees() {
  isLoadingFrequent.value = true;
  try {
    const data = await adminAttendanceService.getFrequentAbsences({
      academic_year: selectedAcademicYear.value || undefined,
      month: selectedMonth.value !== '' ? Number(selectedMonth.value) : undefined,
      class_id: selectedClassId.value !== '' ? Number(selectedClassId.value) : undefined,
      subject_id: selectedSubjectId.value !== '' ? Number(selectedSubjectId.value) : undefined,
      teacher_id: selectedTeacherId.value !== '' ? Number(selectedTeacherId.value) : undefined,
      threshold: absenceThreshold.value,
    });
    frequentAbsentees.value = data;
  } catch (err: any) {
    showToast(err?.response?.data?.detail || 'Failed to detect frequent absentees', 'error');
  } finally {
    isLoadingFrequent.value = false;
  }
}

async function loadRecords(page: number = 1) {
  isLoadingRecords.value = true;
  recordsPage.value = page;
  try {
    const data = await adminAttendanceService.getRecords({
      academic_year: selectedAcademicYear.value || undefined,
      month: selectedMonth.value !== '' ? Number(selectedMonth.value) : undefined,
      class_id: selectedClassId.value !== '' ? Number(selectedClassId.value) : undefined,
      subject_id: selectedSubjectId.value !== '' ? Number(selectedSubjectId.value) : undefined,
      teacher_id: selectedTeacherId.value !== '' ? Number(selectedTeacherId.value) : undefined,
      date: selectedAttendanceDate.value || undefined,
      status: selectedStatus.value !== 'ALL' ? selectedStatus.value : undefined,
      search: searchQuery.value.trim() || undefined,
      page: page,
      page_size: recordsPageSize.value,
    });
    recordsResponse.value = data;
  } catch (err: any) {
    showToast(err?.response?.data?.detail || 'Failed to load historical attendance records', 'error');
  } finally {
    isLoadingRecords.value = false;
  }
}

watch(studentActiveTab, async (newTab) => {
  if (newTab === 'dashboard') await loadDashboard();
  else if (newTab === 'class-report') await loadClassReport();
  else if (newTab === 'frequent-absences') await loadFrequentAbsentees();
  else if (newTab === 'records') await loadRecords(1);
});

async function refreshActiveTabData() {
  if (mainSection.value === 'student') {
    if (studentActiveTab.value === 'dashboard') await loadDashboard();
    else if (studentActiveTab.value === 'class-report') await loadClassReport();
    else if (studentActiveTab.value === 'frequent-absences') await loadFrequentAbsentees();
    else if (studentActiveTab.value === 'records') await loadRecords(1);
  } else {
    if (teacherActiveTab.value === 'daily') await loadTeacherDailyRoster();
    else if (teacherActiveTab.value === 'dashboard') await loadTeacherDashboard();
    else if (teacherActiveTab.value === 'summary') await loadStaffSummary();
    else if (teacherActiveTab.value === 'records') await loadTeacherRecords(1);
  }
}

watch(selectedAcademicYear, async (newYear, oldYear) => {
  if (newYear !== oldYear) {
    const valid = availableClasses.value.some((c) => c.id === selectedClassId.value);
    if (!valid) {
      selectedClassId.value = availableClasses.value.length > 0 ? availableClasses.value[0].id : '';
    }
    selectedSubjectId.value = '';
    selectedTeacherId.value = '';
    await updateDynamicFilters();
    await refreshActiveTabData();
  }
});

watch(selectedClassId, async (newClassId, oldClassId) => {
  if (newClassId !== oldClassId) {
    selectedSubjectId.value = '';
    selectedTeacherId.value = '';
    await updateDynamicFilters();
    await refreshActiveTabData();
  }
});

watch(selectedSubjectId, async (newSubjectId, oldSubjectId) => {
  if (newSubjectId !== oldSubjectId) {
    await updateDynamicFilters();
    await refreshActiveTabData();
  }
});

watch([selectedTeacherId, selectedMonth, selectedAttendanceDate], async () => {
  await refreshActiveTabData();
});

watch(absenceThreshold, async () => {
  if (studentActiveTab.value === 'frequent-absences' || studentActiveTab.value === 'dashboard') {
    await loadFrequentAbsentees();
  }
});

async function handleExportExcel(type: 'class_report' | 'frequent_absentees') {
  if (type === 'class_report' && !selectedClassId.value) {
    showToast('Please select a class to export its attendance report.', 'error');
    return;
  }
  isDownloadingExcel.value = true;
  try {
    await adminAttendanceService.downloadExcel({
      report_type: type,
      class_id: selectedClassId.value !== '' ? Number(selectedClassId.value) : undefined,
      subject_id: selectedSubjectId.value !== '' ? Number(selectedSubjectId.value) : undefined,
      teacher_id: selectedTeacherId.value !== '' ? Number(selectedTeacherId.value) : undefined,
      academic_year: selectedAcademicYear.value || undefined,
      month: selectedMonth.value !== '' ? Number(selectedMonth.value) : undefined,
      threshold: absenceThreshold.value,
    });
    showToast('Excel report generated and downloaded successfully.');
  } catch (err: any) {
    showToast(err?.response?.data?.detail || 'Failed to export Excel report.', 'error');
  } finally {
    isDownloadingExcel.value = false;
  }
}

async function handleExportPdf(type: 'class_report' | 'frequent_absentees') {
  if (type === 'class_report' && !selectedClassId.value) {
    showToast('Please select a class to export its attendance report.', 'error');
    return;
  }
  isDownloadingPdf.value = true;
  try {
    await adminAttendanceService.downloadPdf({
      report_type: type,
      class_id: selectedClassId.value !== '' ? Number(selectedClassId.value) : undefined,
      subject_id: selectedSubjectId.value !== '' ? Number(selectedSubjectId.value) : undefined,
      teacher_id: selectedTeacherId.value !== '' ? Number(selectedTeacherId.value) : undefined,
      academic_year: selectedAcademicYear.value || undefined,
      month: selectedMonth.value !== '' ? Number(selectedMonth.value) : undefined,
      threshold: absenceThreshold.value,
    });
    showToast('PDF report generated and downloaded successfully.');
  } catch (err: any) {
    showToast(err?.response?.data?.detail || 'Failed to download PDF report.', 'error');
  } finally {
    isDownloadingPdf.value = false;
  }
}

async function openStudentBreakdownModal(studentId: number) {
  isBreakdownModalOpen.value = true;
  isLoadingBreakdown.value = true;
  try {
    const data = await adminAttendanceService.getStudentBreakdown(
      studentId,
      selectedAcademicYear.value || undefined
    );
    selectedStudentBreakdown.value = data;
  } catch (err: any) {
    showToast(err?.response?.data?.detail || 'Failed to load student attendance breakdown', 'error');
    selectedStudentBreakdown.value = null;
  } finally {
    isLoadingBreakdown.value = false;
  }
}

function closeBreakdownModal() {
  isBreakdownModalOpen.value = false;
  selectedStudentBreakdown.value = null;
}

function inspectStudentAbsences(st: {
  student_name: string;
  admission_number: string;
  class_name?: string;
  absence_dates: AbsenceDateDetail[];
}) {
  inspectedStudent.value = {
    name: st.student_name,
    admission_number: st.admission_number,
    class_name: st.class_name || (classReportData.value?.class_info.name ?? 'Assigned Class'),
    absence_dates: st.absence_dates,
  };
}

function closeInspectModal() {
  inspectedStudent.value = null;
}

// =========================================================================
// TEACHER ATTENDANCE METHODS
// =========================================================================
async function loadTeacherDailyRoster() {
  if (selectedTeacherDate.value > getTodayDateString()) {
    showToast('Future dates are blocked. Please select today or a past date.', 'error');
    selectedTeacherDate.value = getTodayDateString();
  }

  isLoadingTeacherRoster.value = true;
  try {
    const data = await adminTeacherAttendanceService.getDailyRoster(
      selectedTeacherDate.value,
      selectedAcademicYear.value || undefined
    );
    teacherRoster.value = data;
  } catch (err: any) {
    showToast(err?.response?.data?.detail || 'Failed to load teacher attendance roster', 'error');
  } finally {
    isLoadingTeacherRoster.value = false;
  }
}

function setAllTeachersPresent() {
  if (!teacherRoster.value) return;
  teacherRoster.value.teachers.forEach((t) => {
    t.status = 'PRESENT';
    t.reason = null;
  });
  updateTeacherRosterCounts();
}

function updateTeacherRosterCounts() {
  if (!teacherRoster.value) return;
  let p = 0, a = 0, l = 0, lv = 0;
  for (const t of teacherRoster.value.teachers) {
    if (t.status === 'PRESENT') p++;
    else if (t.status === 'LATE') l++;
    else if (t.status === 'ON_LEAVE') lv++;
    else a++;
  }
  teacherRoster.value.present_count = p;
  teacherRoster.value.absent_count = a;
  teacherRoster.value.late_count = l;
  teacherRoster.value.on_leave_count = lv;
}

async function handleSaveTeacherAttendance() {
  if (!teacherRoster.value) return;
  if (selectedTeacherDate.value > getTodayDateString()) {
    showToast('Cannot save attendance for future dates.', 'error');
    return;
  }

  isSavingTeacherAttendance.value = true;
  try {
    const payload = {
      date: selectedTeacherDate.value,
      academic_year: teacherRoster.value.academic_year || selectedAcademicYear.value || '2026/2027',
      entries: teacherRoster.value.teachers.map((t) => ({
        teacher_id: t.teacher_id,
        status: t.status,
        reason: t.reason?.trim() || null,
      })),
    };
    const res = await adminTeacherAttendanceService.saveAttendance(payload);
    showToast(`Staff Attendance saved: ${res.present_count} Present, ${res.absent_count} Absent, ${res.late_count} Late, ${res.on_leave_count} On Leave.`);
    await loadTeacherDailyRoster();
  } catch (err: any) {
    showToast(err?.response?.data?.detail || 'Failed to save staff attendance.', 'error');
  } finally {
    isSavingTeacherAttendance.value = false;
  }
}

async function loadTeacherDashboard() {
  isLoadingTeacherDashboard.value = true;
  try {
    const data = await adminTeacherAttendanceService.getDashboard({
      academic_year: selectedAcademicYear.value || undefined,
      month: selectedTeacherMonth.value !== '' ? Number(selectedTeacherMonth.value) : undefined,
    });
    teacherDashboardData.value = data;
  } catch (err: any) {
    showToast(err?.response?.data?.detail || 'Failed to load staff attendance dashboard', 'error');
  } finally {
    isLoadingTeacherDashboard.value = false;
  }
}

async function loadStaffSummary() {
  isLoadingStaffSummary.value = true;
  try {
    const data = await adminTeacherAttendanceService.getStaffSummary({
      academic_year: selectedAcademicYear.value || undefined,
      month: selectedTeacherMonth.value !== '' ? Number(selectedTeacherMonth.value) : undefined,
    });
    staffSummaryData.value = data;
  } catch (err: any) {
    showToast(err?.response?.data?.detail || 'Failed to load staff attendance summary', 'error');
  } finally {
    isLoadingStaffSummary.value = false;
  }
}

async function loadTeacherRecords(page: number = 1) {
  isLoadingTeacherRecords.value = true;
  teacherRecordsPage.value = page;
  try {
    const data = await adminTeacherAttendanceService.getRecords({
      academic_year: selectedAcademicYear.value || undefined,
      month: selectedTeacherMonth.value !== '' ? Number(selectedTeacherMonth.value) : undefined,
      status: selectedTeacherStatus.value !== 'ALL' ? selectedTeacherStatus.value : undefined,
      search: teacherSearchQuery.value.trim() || undefined,
      page: page,
      page_size: teacherRecordsPageSize.value,
    });
    teacherRecordsResponse.value = data;
  } catch (err: any) {
    showToast(err?.response?.data?.detail || 'Failed to load staff attendance audit logs', 'error');
  } finally {
    isLoadingTeacherRecords.value = false;
  }
}

watch(teacherActiveTab, async (newTab) => {
  if (newTab === 'daily') await loadTeacherDailyRoster();
  else if (newTab === 'dashboard') await loadTeacherDashboard();
  else if (newTab === 'summary') await loadStaffSummary();
  else if (newTab === 'records') await loadTeacherRecords(1);
});

watch(selectedTeacherDate, async () => {
  if (mainSection.value === 'teacher' && teacherActiveTab.value === 'daily') {
    await loadTeacherDailyRoster();
  }
});

watch(selectedTeacherMonth, async () => {
  if (mainSection.value === 'teacher') {
    if (teacherActiveTab.value === 'dashboard') await loadTeacherDashboard();
    else if (teacherActiveTab.value === 'summary') await loadStaffSummary();
    else if (teacherActiveTab.value === 'records') await loadTeacherRecords(1);
  }
});

async function handleTeacherExportExcel(type: 'daily' | 'staff_summary') {
  isDownloadingTeacherExcel.value = true;
  try {
    await adminTeacherAttendanceService.downloadExcel({
      report_type: type,
      date: type === 'daily' ? selectedTeacherDate.value : undefined,
      academic_year: selectedAcademicYear.value || undefined,
      month: selectedTeacherMonth.value !== '' ? Number(selectedTeacherMonth.value) : undefined,
    });
    showToast('Teacher attendance Excel report downloaded.');
  } catch (err: any) {
    showToast(err?.response?.data?.detail || 'Failed to export teacher Excel report.', 'error');
  } finally {
    isDownloadingTeacherExcel.value = false;
  }
}

async function handleTeacherExportPdf(type: 'daily' | 'staff_summary') {
  isDownloadingTeacherPdf.value = true;
  try {
    await adminTeacherAttendanceService.downloadPdf({
      report_type: type,
      date: type === 'daily' ? selectedTeacherDate.value : undefined,
      academic_year: selectedAcademicYear.value || undefined,
      month: selectedTeacherMonth.value !== '' ? Number(selectedTeacherMonth.value) : undefined,
    });
    showToast('Teacher attendance PDF report downloaded.');
  } catch (err: any) {
    showToast(err?.response?.data?.detail || 'Failed to download teacher PDF report.', 'error');
  } finally {
    isDownloadingTeacherPdf.value = false;
  }
}
</script>

<template>
  <div class="attendance-admin-container">
    <!-- TOAST NOTIFICATION -->
    <transition name="fade">
      <div v-if="toastMessage" class="toast-alert" :class="toastMessage.type">
        <span>{{ toastMessage.text }}</span>
      </div>
    </transition>

    <!-- PAGE HEADER -->
    <header class="page-header">
      <div class="header-left">
        <div class="header-icon-box" :class="{ 'teacher-theme': mainSection === 'teacher' }">
          <svg v-if="mainSection === 'student'" class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
          <svg v-else class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>
        <div>
          <h1 class="page-title">
            {{ mainSection === 'student' ? 'Student Attendance Monitoring & Reports' : 'Teacher Attendance Management & Staff Records' }}
          </h1>
          <p class="page-subtitle">
            {{ mainSection === 'student'
              ? 'Real-time school-wide attendance intelligence, historical records, frequent absence intervention & downloadable class reports'
              : 'Record daily faculty attendance, manage leaves, track staff turnout, and generate official staff attendance reports' }}
          </p>
        </div>
      </div>

      <!-- Quick Action Buttons for Teacher or Student -->
      <div v-if="mainSection === 'student'" class="header-actions">
        <button
          type="button"
          class="btn-outline"
          :disabled="isDownloadingExcel"
          @click="handleExportExcel(studentActiveTab === 'class-report' ? 'class_report' : 'frequent_absentees')"
        >
          <svg class="btn-icon text-emerald-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>{{ isDownloadingExcel ? 'Exporting...' : 'Export Excel' }}</span>
        </button>

        <button
          type="button"
          class="btn-primary-orange"
          :disabled="isDownloadingPdf"
          @click="handleExportPdf(studentActiveTab === 'class-report' ? 'class_report' : 'frequent_absentees')"
        >
          <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>{{ isDownloadingPdf ? 'Generating PDF...' : 'Download PDF' }}</span>
        </button>
      </div>

      <div v-else class="header-actions">
        <button
          type="button"
          class="btn-outline"
          :disabled="isDownloadingTeacherExcel"
          @click="handleTeacherExportExcel(teacherActiveTab === 'daily' ? 'daily' : 'staff_summary')"
        >
          <svg class="btn-icon text-emerald-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>{{ isDownloadingTeacherExcel ? 'Exporting...' : 'Export Staff Excel' }}</span>
        </button>

        <button
          type="button"
          class="btn-primary-blue"
          :disabled="isDownloadingTeacherPdf"
          @click="handleTeacherExportPdf(teacherActiveTab === 'daily' ? 'daily' : 'staff_summary')"
        >
          <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>{{ isDownloadingTeacherPdf ? 'Generating PDF...' : 'Download Staff PDF' }}</span>
        </button>
      </div>
    </header>

    <!-- ========================================================================= -->
    <!-- TOP-LEVEL SECTION TABS: STUDENT ATTENDANCE VS. TEACHER ATTENDANCE -->
    <!-- ========================================================================= -->
    <div class="main-section-switcher">
      <button
        type="button"
        class="main-switch-btn"
        :class="{ 'active': mainSection === 'student' }"
        @click="mainSection = 'student'"
      >
        <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 14l9-5-9-5-9 5 9 5z" />
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
        </svg>
        <span>Student Attendance Monitoring</span>
      </button>

      <button
        type="button"
        class="main-switch-btn teacher-tab"
        :class="{ 'active': mainSection === 'teacher' }"
        @click="mainSection = 'teacher'"
      >
        <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        <span>Teacher Attendance Management</span>
        <span class="badge-role">Staff</span>
      </button>
    </div>

    <!-- ##################################################################### -->
    <!-- SECTION 1: STUDENT ATTENDANCE MONITORING -->
    <!-- ##################################################################### -->
    <div v-if="mainSection === 'student'" class="student-section-wrap">
      <!-- GLOBAL FILTER BAR (STUDENTS) -->
      <div class="filter-card">
        <div class="filter-grid">
          <!-- Academic Year -->
          <div class="filter-group">
            <label class="filter-label">Academic Year</label>
            <select v-model="selectedAcademicYear" class="filter-select">
              <option v-for="yr in filterOptions?.academic_years" :key="yr" :value="yr">
                {{ yr }}
              </option>
            </select>
          </div>

          <!-- Month Filter -->
          <div class="filter-group">
            <label class="filter-label">Month</label>
            <select v-model="selectedMonth" class="filter-select">
              <option value="">All Months</option>
              <option v-for="m in filterOptions?.months" :key="m.value" :value="m.value">
                {{ m.name }}
              </option>
            </select>
          </div>

          <!-- Class Filter -->
          <div class="filter-group">
            <label class="filter-label">Class & Stream</label>
            <select v-model="selectedClassId" class="filter-select">
              <option value="">All School Classes</option>
              <option v-for="cls in availableClasses" :key="cls.id" :value="cls.id">
                {{ cls.name }} ({{ cls.academic_year }})
              </option>
            </select>
          </div>

          <!-- Subject Filter -->
          <div class="filter-group">
            <label class="filter-label">Subject</label>
            <select v-model="selectedSubjectId" class="filter-select">
              <option value="">All Subjects</option>
              <option v-for="sub in dynamicSubjects" :key="sub.id" :value="sub.id">
                {{ sub.name }} ({{ sub.code }})
              </option>
            </select>
          </div>

          <!-- Teacher Filter -->
          <div class="filter-group">
            <label class="filter-label">Teacher</label>
            <select v-model="selectedTeacherId" class="filter-select">
              <option value="">All Teachers</option>
              <option v-for="t in dynamicTeachers" :key="t.id" :value="t.id">
                {{ t.name }}
              </option>
            </select>
          </div>

          <!-- Specific Attendance Date Filter -->
          <div class="filter-group">
            <label class="filter-label">Attendance Date</label>
            <input
              v-model="selectedAttendanceDate"
              type="date"
              class="filter-select"
              :max="getTodayDateString()"
            />
          </div>

          <!-- Absence Threshold Slider / Input -->
          <div class="filter-group threshold-group">
            <label class="filter-label">
              Absence Alert Threshold: <strong>&ge; {{ absenceThreshold }} days</strong>
            </label>
            <div class="threshold-input-wrap">
              <input
                v-model.number="absenceThreshold"
                type="range"
                min="1"
                max="15"
                step="1"
                class="threshold-range"
              />
              <span class="threshold-badge">{{ absenceThreshold }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- STUDENT NAVIGATION TABS -->
      <nav class="nav-tabs-wrapper">
        <div class="nav-tabs-list">
          <button
            type="button"
            class="tab-btn"
            :class="{ 'active': studentActiveTab === 'dashboard' }"
            @click="studentActiveTab = 'dashboard'"
          >
            <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            <span>Dashboard & Trends</span>
          </button>

          <button
            type="button"
            class="tab-btn"
            :class="{ 'active': studentActiveTab === 'class-report' }"
            @click="studentActiveTab = 'class-report'"
          >
            <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
            <span>Class-Based Reports</span>
          </button>

          <button
            type="button"
            class="tab-btn"
            :class="{ 'active': studentActiveTab === 'frequent-absences' }"
            @click="studentActiveTab = 'frequent-absences'"
          >
            <svg class="tab-icon text-red-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span>Frequent Absences</span>
            <span v-if="frequentAbsentees.length > 0" class="badge-alert">{{ frequentAbsentees.length }}</span>
          </button>

          <button
            type="button"
            class="tab-btn"
            :class="{ 'active': studentActiveTab === 'records' }"
            @click="studentActiveTab = 'records'"
          >
            <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
            </svg>
            <span>Historical Logs</span>
          </button>
        </div>
      </nav>

      <!-- TAB 1: STUDENT DASHBOARD & TRENDS -->
      <section v-if="studentActiveTab === 'dashboard'" class="tab-content">
        <div class="kpi-grid">
          <div class="kpi-card">
            <div class="kpi-header">
              <span class="kpi-title">Total Enrolled</span>
              <div class="kpi-icon-wrap bg-slate-100 text-slate-700">
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
            </div>
            <div class="kpi-value">{{ dashboardData?.kpis.total_students ?? '—' }}</div>
            <div class="kpi-footer text-slate-500">Active student body</div>
          </div>

          <div class="kpi-card">
            <div class="kpi-header">
              <span class="kpi-title">Present Today</span>
              <div class="kpi-icon-wrap bg-emerald-100 text-emerald-700">
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>
            <div class="kpi-value text-emerald-600">{{ dashboardData?.kpis.today_present ?? 0 }}</div>
            <div class="kpi-footer text-emerald-600">
              {{ dashboardData?.kpis.today_attendance_percentage }}% daily turnout
            </div>
          </div>

          <div class="kpi-card">
            <div class="kpi-header">
              <span class="kpi-title">Absent Today</span>
              <div class="kpi-icon-wrap bg-red-100 text-red-700">
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
            </div>
            <div class="kpi-value text-red-600">{{ dashboardData?.kpis.today_absent ?? 0 }}</div>
            <div class="kpi-footer text-red-500">Unexcused / Reported</div>
          </div>

          <div class="kpi-card">
            <div class="kpi-header">
              <span class="kpi-title">Late Today</span>
              <div class="kpi-icon-wrap bg-amber-100 text-amber-700">
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10" />
                  <polyline points="12 6 12 12 16 14" />
                </svg>
              </div>
            </div>
            <div class="kpi-value text-amber-600">{{ dashboardData?.kpis.today_late ?? 0 }}</div>
            <div class="kpi-footer text-amber-600">Arrived after bell</div>
          </div>

          <div class="kpi-card">
            <div class="kpi-header">
              <span class="kpi-title">Overall Rate</span>
              <div class="kpi-icon-wrap bg-blue-100 text-blue-700">
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
            </div>
            <div class="kpi-value text-blue-600">{{ dashboardData?.kpis.overall_attendance_percentage }}%</div>
            <div class="kpi-footer text-slate-500">Period average</div>
          </div>

          <div class="kpi-card cursor-pointer" @click="studentActiveTab = 'frequent-absences'">
            <div class="kpi-header">
              <span class="kpi-title">Frequent Absentees</span>
              <div class="kpi-icon-wrap bg-rose-100 text-rose-700">
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
            </div>
            <div class="kpi-value text-rose-600">{{ dashboardData?.kpis.frequent_absentees_count ?? 0 }}</div>
            <div class="kpi-footer text-rose-500 font-medium">Click to review &rarr;</div>
          </div>
        </div>

        <div class="dashboard-split-grid">
          <div class="content-panel">
            <div class="panel-header">
              <h2 class="panel-title">Daily Attendance Trends</h2>
              <span class="panel-sub">Recent 14 active recorded school days</span>
            </div>

            <div v-if="dashboardData?.daily_summary && dashboardData.daily_summary.length > 0" class="daily-chart-list">
              <div v-for="d in dashboardData.daily_summary" :key="d.date" class="daily-bar-row">
                <div class="date-col">
                  <span class="day-label">{{ d.day_name }}</span>
                  <span class="date-sub">{{ formatShortDate(d.date) }}</span>
                </div>
                <div class="bar-track">
                  <div class="bar-present" :style="{ width: `${d.attendance_percentage}%` }" />
                  <div class="bar-absent" :style="{ width: `${100 - d.attendance_percentage}%` }" />
                </div>
                <div class="stat-col">
                  <span class="stat-pct" :class="{ 'low': d.attendance_percentage < 80 }">{{ d.attendance_percentage }}%</span>
                  <span class="stat-counts">
                    <span class="text-emerald-600 font-medium">{{ d.present_count }}P</span> /
                    <span class="text-red-500 font-medium">{{ d.absent_count }}A</span>
                  </span>
                </div>
              </div>
            </div>
            <div v-else class="empty-state-box"><p>No daily attendance logs found.</p></div>
          </div>

          <div class="content-panel">
            <div class="panel-header">
              <h2 class="panel-title">Recent Teacher Submissions</h2>
              <span class="panel-sub">Real-time attendance recordings submitted by faculty</span>
            </div>

            <div v-if="dashboardData?.recent_sessions && dashboardData.recent_sessions.length > 0" class="session-feed">
              <div v-for="(sess, idx) in dashboardData.recent_sessions" :key="idx" class="session-card">
                <div class="sess-header">
                  <span class="sess-class">{{ sess.class_name }}</span>
                  <span class="sess-date">{{ formatDate(sess.date) }}</span>
                </div>
                <div class="sess-sub-line">
                  <span class="sess-subject">{{ sess.subject_name }}</span>
                  <span v-if="sess.period" class="sess-period">&bull; {{ sess.period }}</span>
                </div>
                <div class="sess-meta-footer">
                  <span class="sess-teacher">By: {{ sess.teacher_name || 'Faculty Member' }}</span>
                  <span class="sess-badge" :class="sess.attendance_percentage >= 85 ? 'good' : 'alert'">
                    {{ sess.present_count }} / {{ sess.total_students }} ({{ sess.attendance_percentage }}%)
                  </span>
                </div>
              </div>
            </div>
            <div v-else class="empty-state-box"><p>No recent teacher sessions found.</p></div>
          </div>
        </div>

        <div class="content-panel">
          <div class="panel-header">
            <h2 class="panel-title">Monthly Attendance Summary</h2>
            <span class="panel-sub">Historical monthly comparison across the academic year</span>
          </div>
          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Month</th>
                  <th class="text-center">Year</th>
                  <th class="text-center">Days Present</th>
                  <th class="text-center">Days Absent</th>
                  <th class="text-center">Total Turnout</th>
                  <th class="text-center">Attendance Rate</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="m in dashboardData?.monthly_summary" :key="m.month_name">
                  <td class="font-medium text-slate-800">{{ m.month_name }}</td>
                  <td class="text-center">{{ m.year }}</td>
                  <td class="text-center text-emerald-600 font-semibold">{{ m.present_count }}</td>
                  <td class="text-center text-red-600 font-semibold">{{ m.absent_count }}</td>
                  <td class="text-center">{{ m.present_count + m.absent_count }}</td>
                  <td class="text-center font-bold">
                    <span :class="m.attendance_percentage >= 85 ? 'text-emerald-600' : 'text-amber-600'">
                      {{ m.attendance_percentage }}%
                    </span>
                  </td>
                  <td>
                    <span class="status-pill" :class="m.attendance_percentage >= 85 ? 'pill-good' : 'pill-warn'">
                      {{ m.attendance_percentage >= 85 ? 'High Attendance' : 'Needs Attention' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- TAB 2: CLASS REPORT -->
      <section v-if="studentActiveTab === 'class-report'" class="tab-content">
        <div v-if="!selectedClassId" class="select-prompt-card">
          <h3 class="prompt-title">Select a Class & Stream</h3>
          <p class="prompt-sub">Please select a class from the filter bar above.</p>
        </div>

        <div v-else-if="selectedAttendanceDate && !hasRecordsOnSelectedDate" class="select-prompt-card text-center py-16">
          <div class="empty-icon-circle mx-auto mb-3">
            <svg class="w-10 h-10 text-slate-400 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <h3 class="text-lg font-bold text-slate-800">No attendance records found for this date.</h3>
          <p class="text-sm text-slate-500 mt-1 max-w-md mx-auto">
            No attendance roll call was recorded on {{ formatDate(selectedAttendanceDate) }} for {{ classReportData?.class_info.name || 'this class' }}.
          </p>
        </div>

        <div v-else>
          <div class="class-summary-card">
            <div class="cls-title-box">
              <h2 class="cls-name">{{ classReportData?.class_info.name }}</h2>
              <div class="cls-meta-chips">
                <span class="chip">Code: {{ classReportData?.class_info.code }}</span>
                <span class="chip">Year: {{ classReportData?.academic_year }}</span>
                <span class="chip">Period: {{ classReportData?.period_label }}</span>
              </div>
            </div>

            <div class="cls-stats-row">
              <div class="stat-tile">
                <span class="tile-val">{{ classReportData?.class_info.total_enrolled ?? 0 }}</span>
                <span class="tile-lbl">Enrolled Students</span>
              </div>
              <div class="stat-tile">
                <span class="tile-val text-emerald-600">{{ classReportData?.summary.present_count ?? 0 }}</span>
                <span class="tile-lbl">Days Present</span>
              </div>
              <div class="stat-tile">
                <span class="tile-val text-red-600">{{ classReportData?.summary.absent_count ?? 0 }}</span>
                <span class="tile-lbl">Days Absent</span>
              </div>
              <div class="stat-tile">
                <span class="tile-val text-amber-600">{{ classReportData?.summary.late_count ?? 0 }}</span>
                <span class="tile-lbl">Late Arrivals</span>
              </div>
              <div class="stat-tile highlight">
                <span class="tile-val text-blue-600">{{ classReportData?.summary.attendance_percentage }}%</span>
                <span class="tile-lbl">Overall Attendance</span>
              </div>
            </div>
          </div>

          <div class="content-panel">
            <div class="panel-header">
              <div>
                <h3 class="panel-title">Student Attendance Register</h3>
                <span class="panel-sub">Individual records, percentages, and absence dates</span>
              </div>
              <div class="action-buttons-wrap">
                <button type="button" class="btn-sm btn-outline" :disabled="isDownloadingExcel" @click="handleExportExcel('class_report')">
                  Export Class Excel
                </button>
                <button type="button" class="btn-sm btn-primary-orange" :disabled="isDownloadingPdf" @click="handleExportPdf('class_report')">
                  Download Class PDF
                </button>
              </div>
            </div>

            <div class="table-responsive">
              <table class="data-table">
                <thead>
                  <tr>
                    <th class="w-12">#</th>
                    <th>Admission No</th>
                    <th>Student Name</th>
                    <th class="text-center">Gender</th>
                    <th class="text-center">Total Sessions</th>
                    <th class="text-center text-emerald-700">Present</th>
                    <th class="text-center text-red-700">Absent</th>
                    <th class="text-center text-amber-700">Late</th>
                    <th class="text-center">Attendance %</th>
                    <th>Absence Dates</th>
                    <th class="text-center">Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(st, idx) in classReportData?.students" :key="st.student_id" :class="{ 'high-absent-row': st.days_absent >= absenceThreshold }">
                    <td class="text-slate-400 text-center">{{ idx + 1 }}</td>
                    <td class="font-mono text-slate-800 font-semibold">{{ st.admission_number }}</td>
                    <td class="font-medium text-slate-900">{{ st.student_name }}</td>
                    <td class="text-center text-slate-500">{{ st.gender || '—' }}</td>
                    <td class="text-center font-medium">{{ st.total_sessions }}</td>
                    <td class="text-center text-emerald-600 font-semibold">{{ st.days_present }}</td>
                    <td class="text-center font-semibold" :class="st.days_absent > 0 ? 'text-red-600' : 'text-slate-400'">{{ st.days_absent }}</td>
                    <td class="text-center text-amber-600">{{ st.days_late }}</td>
                    <td class="text-center">
                      <span class="pct-pill" :class="st.attendance_percentage >= 85 ? 'pct-good' : (st.attendance_percentage >= 70 ? 'pct-warn' : 'pct-danger')">
                        {{ st.attendance_percentage }}%
                      </span>
                    </td>
                    <td>
                      <div v-if="st.absence_dates.length > 0" class="absence-chips-container">
                        <span v-for="(d, dIdx) in st.absence_dates.slice(0, 3)" :key="dIdx" class="absence-badge">
                          {{ formatShortDate(d.date) }}
                        </span>
                        <span v-if="st.absence_dates.length > 3" class="more-badge" @click="inspectStudentAbsences(st)">
                          +{{ st.absence_dates.length - 3 }} more
                        </span>
                      </div>
                      <span v-else class="text-xs text-slate-400">Full Attendance</span>
                    </td>
                    <td class="text-center">
                      <div class="flex items-center justify-center gap-1.5">
                        <button type="button" class="btn-inspect btn-breakdown" @click="openStudentBreakdownModal(st.student_id)">
                          Breakdown
                        </button>
                        <button v-if="st.absence_dates.length > 0" type="button" class="btn-inspect" @click="inspectStudentAbsences(st)">
                          Dates
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      <!-- TAB 3: FREQUENT ABSENCES -->
      <section v-if="studentActiveTab === 'frequent-absences'" class="tab-content">
        <div class="content-panel">
          <div class="panel-header">
            <div>
              <h2 class="panel-title text-red-600">Frequent Absence Detection & Intervention</h2>
              <span class="panel-sub">Students ranked by total absences exceeding threshold of &ge; {{ absenceThreshold }} absences</span>
            </div>
            <div class="action-buttons-wrap">
              <button type="button" class="btn-sm btn-outline" :disabled="isDownloadingExcel" @click="handleExportExcel('frequent_absentees')">
                Export Absentees Excel
              </button>
              <button type="button" class="btn-sm btn-primary-orange" :disabled="isDownloadingPdf" @click="handleExportPdf('frequent_absentees')">
                Download Absentees PDF
              </button>
            </div>
          </div>

          <div v-if="frequentAbsentees.length > 0" class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th class="w-12">Rank</th>
                  <th>Admission No</th>
                  <th>Student Name</th>
                  <th>Class</th>
                  <th class="text-center text-red-700">Total Absences</th>
                  <th class="text-center">Attendance %</th>
                  <th>Last Absent Date</th>
                  <th>Guardian Contact</th>
                  <th>Absence Dates</th>
                  <th class="text-center">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(st, idx) in frequentAbsentees" :key="st.student_id">
                  <td class="text-center font-bold text-slate-700">
                    <span class="rank-circle" :class="{ 'top-rank': idx < 3 }">{{ idx + 1 }}</span>
                  </td>
                  <td class="font-mono text-slate-900 font-semibold">{{ st.admission_number }}</td>
                  <td class="font-medium text-slate-900">
                    {{ st.student_name }}
                    <span v-if="st.absent_count >= 5" class="badge-critical">Critical</span>
                    <span v-else class="badge-warning">Flagged</span>
                  </td>
                  <td class="text-slate-700">{{ st.class_name }}</td>
                  <td class="text-center text-red-600 font-bold text-base">{{ st.absent_count }}</td>
                  <td class="text-center">
                    <span class="pct-pill pct-danger">{{ st.attendance_percentage }}%</span>
                  </td>
                  <td class="text-slate-600 text-sm">{{ formatDate(st.last_absent_date) }}</td>
                  <td>
                    <div class="guardian-contact-cell">
                      <span class="g-name">{{ st.guardian_name || 'Guardian' }}</span>
                      <a v-if="st.guardian_phone" :href="`tel:${st.guardian_phone}`" class="g-phone">{{ st.guardian_phone }}</a>
                    </div>
                  </td>
                  <td>
                    <div class="absence-chips-container">
                      <span v-for="(d, dIdx) in st.absence_dates.slice(0, 4)" :key="dIdx" class="absence-badge">
                        {{ formatShortDate(d.date) }} ({{ d.subject_name?.slice(0, 8) || 'Subj' }})
                      </span>
                    </div>
                  </td>
                  <td class="text-center">
                    <div class="flex items-center justify-center gap-1.5">
                      <button type="button" class="btn-inspect btn-breakdown" @click="openStudentBreakdownModal(st.student_id)">
                        Breakdown
                      </button>
                      <button type="button" class="btn-inspect" @click="inspectStudentAbsences(st)">
                        Dates
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="empty-state-box">
            <h4 class="font-bold text-slate-800">No Frequent Absentees Detected</h4>
          </div>
        </div>
      </section>

      <!-- TAB 4: HISTORICAL LOGS -->
      <section v-if="studentActiveTab === 'records'" class="tab-content">
        <div class="content-panel">
          <div class="panel-header">
            <div>
              <h2 class="panel-title">Individual Attendance Records & Audit Log</h2>
              <span class="panel-sub">Total {{ recordsResponse?.total ?? 0 }} real records recorded in database</span>
            </div>
            <div class="inline-filters-row">
              <div class="search-box">
                <input v-model="searchQuery" type="text" placeholder="Search student or adm no..." class="search-input" @keyup.enter="loadRecords(1)" />
                <button type="button" class="search-btn" @click="loadRecords(1)">Search</button>
              </div>
              <select v-model="selectedStatus" class="filter-select-sm" @change="loadRecords(1)">
                <option value="ALL">All Statuses</option>
                <option value="PRESENT">Present</option>
                <option value="ABSENT">Absent</option>
                <option value="LATE">Late</option>
                <option value="EXCUSED">Excused</option>
              </select>
            </div>
          </div>

          <div v-if="recordsResponse && recordsResponse.items.length === 0" class="select-prompt-card text-center py-16">
            <div class="empty-icon-circle mx-auto mb-3">
              <svg class="w-10 h-10 text-slate-400 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 class="text-lg font-bold text-slate-800">
              {{ selectedAttendanceDate ? 'No attendance records found for this date.' : 'No Attendance Records Found' }}
            </h3>
            <p class="text-sm text-slate-500 mt-1 max-w-md mx-auto">
              {{ selectedAttendanceDate ? 'No attendance records were found matching ' + formatDate(selectedAttendanceDate) + '.' : 'No attendance records match your filter criteria.' }}
            </p>
          </div>

          <div v-else class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Period</th>
                  <th>Admission No</th>
                  <th>Student Name</th>
                  <th>Class</th>
                  <th>Subject</th>
                  <th>Teacher</th>
                  <th class="text-center">Status</th>
                  <th>Remarks</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in recordsResponse?.items" :key="r.id">
                  <td class="font-mono text-slate-800">{{ formatDate(r.date) }}</td>
                  <td class="text-xs text-slate-500">{{ r.period || '—' }}</td>
                  <td class="font-mono font-semibold text-slate-700">{{ r.admission_number }}</td>
                  <td class="font-medium text-slate-900">
                    <button type="button" class="btn-student-link" title="View Student Subject Attendance Breakdown" @click="openStudentBreakdownModal(r.student_id)">
                      {{ r.student_name }}
                    </button>
                  </td>
                  <td>{{ r.class_name }}</td>
                  <td>{{ r.subject_name }}</td>
                  <td class="text-slate-600 text-sm">{{ r.teacher_name || 'Faculty' }}</td>
                  <td class="text-center">
                    <span class="status-pill" :class="r.status === 'PRESENT' ? 'pill-present' : (r.status === 'LATE' ? 'pill-late' : 'pill-absent')">
                      {{ r.status }}
                    </span>
                  </td>
                  <td class="text-xs text-slate-500">{{ r.remarks || '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="recordsResponse && recordsResponse.total_pages > 1" class="pagination-bar">
            <button type="button" class="pg-btn" :disabled="recordsPage <= 1" @click="loadRecords(recordsPage - 1)">&larr; Previous</button>
            <span class="pg-info">Page {{ recordsPage }} of {{ recordsResponse.total_pages }}</span>
            <button type="button" class="pg-btn" :disabled="recordsPage >= recordsResponse.total_pages" @click="loadRecords(recordsPage + 1)">Next &rarr;</button>
          </div>
        </div>
      </section>
    </div>

    <!-- ##################################################################### -->
    <!-- SECTION 2: TEACHER ATTENDANCE MANAGEMENT -->
    <!-- ##################################################################### -->
    <div v-else class="teacher-section-wrap">
      <!-- TEACHER NAVIGATION TABS -->
      <nav class="nav-tabs-wrapper">
        <div class="nav-tabs-list">
          <button
            type="button"
            class="tab-btn"
            :class="{ 'active': teacherActiveTab === 'daily' }"
            @click="teacherActiveTab = 'daily'"
          >
            <svg class="tab-icon text-orange-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
            <span>Mark Daily Attendance</span>
          </button>

          <button
            type="button"
            class="tab-btn"
            :class="{ 'active': teacherActiveTab === 'dashboard' }"
            @click="teacherActiveTab = 'dashboard'"
          >
            <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            <span>Staff Dashboard</span>
          </button>

          <button
            type="button"
            class="tab-btn"
            :class="{ 'active': teacherActiveTab === 'summary' }"
            @click="teacherActiveTab = 'summary'"
          >
            <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span>Teacher Summaries & Reports</span>
          </button>

          <button
            type="button"
            class="tab-btn"
            :class="{ 'active': teacherActiveTab === 'records' }"
            @click="teacherActiveTab = 'records'"
          >
            <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
            </svg>
            <span>Staff Attendance Logs</span>
          </button>
        </div>
      </nav>

      <!-- SUB-TAB 1: MARK DAILY ATTENDANCE -->
      <section v-if="teacherActiveTab === 'daily'" class="tab-content">
        <!-- Date Selector & Quick Turnout Counter Bar -->
        <div class="daily-marker-bar">
          <div class="date-picker-wrap">
            <label class="font-bold text-slate-800 text-sm">Attendance Date:</label>
            <input
              v-model="selectedTeacherDate"
              type="date"
              class="form-input-date"
              :max="getTodayDateString()"
            />
            <span v-if="selectedTeacherDate === getTodayDateString()" class="pill-today">Today</span>
            <span v-else-if="selectedTeacherDate > getTodayDateString()" class="pill-future-blocked">Future Date Blocked</span>
          </div>

          <!-- Roster Counts for Selected Date -->
          <div class="roster-metrics-strip">
            <div class="strip-item">
              <span class="strip-label">Total Staff</span>
              <span class="strip-num">{{ teacherRoster?.total_teachers ?? 0 }}</span>
            </div>
            <div class="strip-item text-emerald-600">
              <span class="strip-label">Present</span>
              <span class="strip-num">{{ teacherRoster?.present_count ?? 0 }}</span>
            </div>
            <div class="strip-item text-red-600">
              <span class="strip-label">Absent</span>
              <span class="strip-num">{{ teacherRoster?.absent_count ?? 0 }}</span>
            </div>
            <div class="strip-item text-amber-600">
              <span class="strip-label">Late</span>
              <span class="strip-num">{{ teacherRoster?.late_count ?? 0 }}</span>
            </div>
            <div class="strip-item text-blue-600">
              <span class="strip-label">On Leave</span>
              <span class="strip-num">{{ teacherRoster?.on_leave_count ?? 0 }}</span>
            </div>
            <div class="strip-item highlight">
              <span class="strip-label">Daily Turnout</span>
              <span class="strip-num">
                {{ teacherRoster && teacherRoster.total_teachers > 0
                  ? Math.round(((teacherRoster.present_count + teacherRoster.late_count) / teacherRoster.total_teachers) * 100)
                  : 0 }}%
              </span>
            </div>
          </div>

          <!-- Quick Action Buttons -->
          <div class="marker-actions">
            <button type="button" class="btn-outline btn-sm" @click="setAllTeachersPresent">
              Mark All Present
            </button>
            <button
              type="button"
              class="btn-primary-orange btn-sm"
              :disabled="isSavingTeacherAttendance || selectedTeacherDate > getTodayDateString()"
              @click="handleSaveTeacherAttendance"
            >
              {{ isSavingTeacherAttendance ? 'Saving...' : 'Save Daily Attendance' }}
            </button>
          </div>
        </div>

        <!-- Teachers Table for Marking Attendance -->
        <div class="content-panel">
          <div class="panel-header">
            <div>
              <h3 class="panel-title">Daily Staff Attendance Register</h3>
              <span class="panel-sub">
                Mark status and optional reasons for all registered faculty members for {{ formatDate(selectedTeacherDate) }}
              </span>
            </div>
            <div class="flex items-center gap-3">
              <input
                v-model="dailyTeacherSearch"
                type="text"
                placeholder="Search teacher by name, ID or phone..."
                class="filter-search-input"
              />
              <span v-if="teacherRoster?.is_recorded" class="status-pill pill-good">
                Already Saved in Database (Editing Allowed)
              </span>
              <span v-else class="status-pill pill-warn">
                Not Yet Saved For This Date
              </span>
            </div>
          </div>

          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th class="w-12">#</th>
                  <th>Staff ID</th>
                  <th>Teacher Name</th>
                  <th>Contact Info</th>
                  <th>Attendance Status</th>
                  <th>Absence / Lateness / Leave Reason</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="isLoadingTeacherRoster">
                  <td colspan="6" class="text-center py-10 text-slate-500">
                    <div class="inline-flex items-center gap-2">
                      <svg class="animate-spin h-5 w-5 text-orange-500" viewBox="0 0 24 24" fill="none">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                      </svg>
                      <span class="font-medium">Loading registered faculty members...</span>
                    </div>
                  </td>
                </tr>

                <tr
                  v-else
                  v-for="(t, idx) in filteredDailyTeachers"
                  :key="t.teacher_id"
                  :class="{
                    'bg-red-50/50': t.status === 'ABSENT',
                    'bg-amber-50/50': t.status === 'LATE',
                    'bg-blue-50/50': t.status === 'ON_LEAVE'
                  }"
                >
                  <td class="text-center text-slate-400">{{ idx + 1 }}</td>
                  <td class="font-mono text-slate-900 font-semibold">{{ t.teacher_number }}</td>
                  <td>
                    <div class="font-medium text-slate-900 flex items-center gap-1.5">
                      <span>{{ t.teacher_name }}</span>
                      <span
                        v-if="t.employment_status && t.employment_status !== 'ACTIVE'"
                        class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200"
                      >
                        {{ t.employment_status }}
                      </span>
                    </div>
                    <div v-if="t.qualification" class="text-xs text-slate-400">{{ t.qualification }}</div>
                  </td>
                  <td>
                    <div class="text-xs text-slate-700">{{ t.phone || 'No phone' }}</div>
                    <div class="text-xs text-slate-400">{{ t.email || '—' }}</div>
                  </td>
                  <td>
                    <!-- Interactive Status Pill Buttons -->
                    <div class="status-radio-group">
                      <button
                        type="button"
                        class="status-choice-btn present"
                        :class="{ 'selected': t.status === 'PRESENT' }"
                        @click="t.status = 'PRESENT'; t.reason = null; updateTeacherRosterCounts()"
                      >
                        Present
                      </button>

                      <button
                        type="button"
                        class="status-choice-btn absent"
                        :class="{ 'selected': t.status === 'ABSENT' }"
                        @click="t.status = 'ABSENT'; updateTeacherRosterCounts()"
                      >
                        Absent
                      </button>

                      <button
                        type="button"
                        class="status-choice-btn late"
                        :class="{ 'selected': t.status === 'LATE' }"
                        @click="t.status = 'LATE'; updateTeacherRosterCounts()"
                      >
                        Late
                      </button>

                      <button
                        type="button"
                        class="status-choice-btn on-leave"
                        :class="{ 'selected': t.status === 'ON_LEAVE' }"
                        @click="t.status = 'ON_LEAVE'; updateTeacherRosterCounts()"
                      >
                        On Leave
                      </button>
                    </div>
                  </td>
                  <td>
                    <input
                      v-model="t.reason"
                      type="text"
                      placeholder="Optional reason (e.g. Sick, Family Emergency, Official Duty)..."
                      class="reason-input"
                    />
                  </td>
                </tr>

                <tr v-if="!isLoadingTeacherRoster && (!filteredDailyTeachers || filteredDailyTeachers.length === 0)">
                  <td colspan="6" class="text-center py-10 text-slate-400">
                    <span v-if="dailyTeacherSearch">No faculty members matching "{{ dailyTeacherSearch }}".</span>
                    <span v-else>No registered faculty members found in database.</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- SUB-TAB 2: STAFF ATTENDANCE DASHBOARD -->
      <section v-if="teacherActiveTab === 'dashboard'" class="tab-content">
        <div class="kpi-grid">
          <div class="kpi-card">
            <div class="kpi-header">
              <span class="kpi-title">Total Staff</span>
              <div class="kpi-icon-wrap bg-slate-100 text-slate-700">
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
            </div>
            <div class="kpi-value">{{ teacherDashboardData?.kpis.total_teachers ?? 0 }}</div>
            <div class="kpi-footer text-slate-500">Registered Faculty Members</div>
          </div>

          <div class="kpi-card">
            <div class="kpi-header">
              <span class="kpi-title">Present Today</span>
              <div class="kpi-icon-wrap bg-emerald-100 text-emerald-700">
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>
            <div class="kpi-value text-emerald-600">{{ teacherDashboardData?.kpis.today_present ?? 0 }}</div>
            <div class="kpi-footer text-emerald-600">{{ teacherDashboardData?.kpis.today_attendance_percentage }}% staff turnout</div>
          </div>

          <div class="kpi-card">
            <div class="kpi-header">
              <span class="kpi-title">Absent Today</span>
              <div class="kpi-icon-wrap bg-red-100 text-red-700">
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
            </div>
            <div class="kpi-value text-red-600">{{ teacherDashboardData?.kpis.today_absent ?? 0 }}</div>
            <div class="kpi-footer text-red-500">Unexcused faculty</div>
          </div>

          <div class="kpi-card">
            <div class="kpi-header">
              <span class="kpi-title">Late Today</span>
              <div class="kpi-icon-wrap bg-amber-100 text-amber-700">
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10" />
                  <polyline points="12 6 12 12 16 14" />
                </svg>
              </div>
            </div>
            <div class="kpi-value text-amber-600">{{ teacherDashboardData?.kpis.today_late ?? 0 }}</div>
            <div class="kpi-footer text-amber-600">Arrived late</div>
          </div>

          <div class="kpi-card">
            <div class="kpi-header">
              <span class="kpi-title">On Leave Today</span>
              <div class="kpi-icon-wrap bg-blue-100 text-blue-700">
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
            <div class="kpi-value text-blue-600">{{ teacherDashboardData?.kpis.today_on_leave ?? 0 }}</div>
            <div class="kpi-footer text-blue-500">Approved Leave</div>
          </div>

          <div class="kpi-card">
            <div class="kpi-header">
              <span class="kpi-title">Overall Turnout</span>
              <div class="kpi-icon-wrap bg-indigo-100 text-indigo-700">
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
            </div>
            <div class="kpi-value text-indigo-600">{{ teacherDashboardData?.kpis.overall_attendance_percentage }}%</div>
            <div class="kpi-footer text-slate-500">Historical staff turnout</div>
          </div>
        </div>

        <div class="dashboard-split-grid">
          <!-- Daily Staff Turnout Trend -->
          <div class="content-panel">
            <div class="panel-header">
              <h2 class="panel-title">Staff Turnout Trend (Last 14 Recorded Days)</h2>
            </div>
            <div v-if="teacherDashboardData?.daily_summary && teacherDashboardData.daily_summary.length > 0" class="daily-chart-list">
              <div v-for="d in teacherDashboardData.daily_summary" :key="d.date" class="daily-bar-row">
                <div class="date-col">
                  <span class="day-label">{{ d.day_name }}</span>
                  <span class="date-sub">{{ formatShortDate(d.date) }}</span>
                </div>
                <div class="bar-track">
                  <div class="bar-present" :style="{ width: `${d.attendance_percentage}%` }" />
                  <div class="bar-absent" :style="{ width: `${100 - d.attendance_percentage}%` }" />
                </div>
                <div class="stat-col">
                  <span class="stat-pct" :class="{ 'low': d.attendance_percentage < 85 }">{{ d.attendance_percentage }}%</span>
                  <span class="stat-counts">
                    <span class="text-emerald-600 font-medium">{{ d.present_count }}P</span> /
                    <span class="text-red-500 font-medium">{{ d.absent_count }}A</span> /
                    <span class="text-blue-500 font-medium">{{ d.on_leave_count }}L</span>
                  </span>
                </div>
              </div>
            </div>
            <div v-else class="empty-state-box"><p>No daily staff attendance records found.</p></div>
          </div>

          <!-- Monthly Staff Comparison Table -->
          <div class="content-panel">
            <div class="panel-header">
              <h2 class="panel-title">Monthly Staff Attendance Summary</h2>
            </div>
            <div class="table-responsive">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Month</th>
                    <th class="text-center">Present</th>
                    <th class="text-center">Absent</th>
                    <th class="text-center">Late</th>
                    <th class="text-center">Leave</th>
                    <th class="text-center">Turnout</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="m in teacherDashboardData?.monthly_summary" :key="m.month_name">
                    <td class="font-medium text-slate-800">{{ m.month_name }}</td>
                    <td class="text-center text-emerald-600 font-semibold">{{ m.present_count }}</td>
                    <td class="text-center text-red-600 font-semibold">{{ m.absent_count }}</td>
                    <td class="text-center text-amber-600">{{ m.late_count }}</td>
                    <td class="text-center text-blue-600">{{ m.on_leave_count }}</td>
                    <td class="text-center font-bold">
                      <span :class="m.attendance_percentage >= 85 ? 'text-emerald-600' : 'text-amber-600'">
                        {{ m.attendance_percentage }}%
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      <!-- SUB-TAB 3: TEACHER-BY-TEACHER SUMMARY & REPORTS -->
      <section v-if="teacherActiveTab === 'summary'" class="tab-content">
        <div class="content-panel">
          <div class="panel-header">
            <div>
              <h2 class="panel-title">Faculty Attendance Performance & Totals</h2>
              <span class="panel-sub">
                Cumulative staff turnout, days present, absent, late, and on leave
              </span>
            </div>
            <div class="action-buttons-wrap">
              <button
                type="button"
                class="btn-sm btn-outline"
                :disabled="isDownloadingTeacherExcel"
                @click="handleTeacherExportExcel('staff_summary')"
              >
                Export Summary Excel
              </button>
              <button
                type="button"
                class="btn-sm btn-primary-blue"
                :disabled="isDownloadingTeacherPdf"
                @click="handleTeacherExportPdf('staff_summary')"
              >
                Download Summary PDF
              </button>
            </div>
          </div>

          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th class="w-12">#</th>
                  <th>Staff ID</th>
                  <th>Teacher Name</th>
                  <th>Contact</th>
                  <th class="text-center">Total Marked</th>
                  <th class="text-center text-emerald-700">Present</th>
                  <th class="text-center text-red-700">Absent</th>
                  <th class="text-center text-amber-700">Late</th>
                  <th class="text-center text-blue-700">On Leave</th>
                  <th class="text-center">Turnout Rate</th>
                  <th>Last Recorded</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(t, idx) in staffSummaryData?.teachers" :key="t.teacher_id">
                  <td class="text-center text-slate-400">{{ idx + 1 }}</td>
                  <td class="font-mono text-slate-900 font-semibold">{{ t.teacher_number }}</td>
                  <td class="font-medium text-slate-900">{{ t.teacher_name }}</td>
                  <td class="text-xs text-slate-600">{{ t.phone || t.email || '—' }}</td>
                  <td class="text-center font-medium">{{ t.total_days }}</td>
                  <td class="text-center text-emerald-600 font-semibold">{{ t.days_present }}</td>
                  <td class="text-center font-semibold" :class="t.days_absent > 0 ? 'text-red-600' : 'text-slate-400'">
                    {{ t.days_absent }}
                  </td>
                  <td class="text-center text-amber-600">{{ t.days_late }}</td>
                  <td class="text-center text-blue-600">{{ t.days_on_leave }}</td>
                  <td class="text-center">
                    <span
                      class="pct-pill"
                      :class="t.attendance_percentage >= 85 ? 'pct-good' : (t.attendance_percentage >= 70 ? 'pct-warn' : 'pct-danger')"
                    >
                      {{ t.attendance_percentage }}%
                    </span>
                  </td>
                  <td class="text-xs text-slate-500">
                    <span v-if="t.last_attendance_date">{{ formatDate(t.last_attendance_date) }} ({{ t.last_status }})</span>
                    <span v-else>—</span>
                  </td>
                </tr>

                <tr v-if="!staffSummaryData?.teachers || staffSummaryData.teachers.length === 0">
                  <td colspan="11" class="text-center py-8 text-slate-400">
                    No teacher attendance records found.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- SUB-TAB 4: STAFF ATTENDANCE LOGS -->
      <section v-if="teacherActiveTab === 'records'" class="tab-content">
        <div class="content-panel">
          <div class="panel-header">
            <div>
              <h2 class="panel-title">Staff Attendance Audit Log</h2>
              <span class="panel-sub">
                Total {{ teacherRecordsResponse?.total ?? 0 }} real faculty records in database
              </span>
            </div>

            <div class="inline-filters-row">
              <div class="search-box">
                <input
                  v-model="teacherSearchQuery"
                  type="text"
                  placeholder="Search teacher or staff ID..."
                  class="search-input"
                  @keyup.enter="loadTeacherRecords(1)"
                />
                <button type="button" class="search-btn" @click="loadTeacherRecords(1)">Search</button>
              </div>

              <select v-model="selectedTeacherStatus" class="filter-select-sm" @change="loadTeacherRecords(1)">
                <option value="ALL">All Statuses</option>
                <option value="PRESENT">Present</option>
                <option value="ABSENT">Absent</option>
                <option value="LATE">Late</option>
                <option value="ON_LEAVE">On Leave</option>
              </select>
            </div>
          </div>

          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Staff ID</th>
                  <th>Teacher Name</th>
                  <th>Contact</th>
                  <th class="text-center">Status</th>
                  <th>Reason / Remarks</th>
                  <th>Recorded By</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in teacherRecordsResponse?.items" :key="r.id">
                  <td class="font-mono text-slate-800">{{ formatDate(r.date) }}</td>
                  <td class="font-mono text-slate-900 font-semibold">{{ r.teacher_number }}</td>
                  <td class="font-medium text-slate-900">{{ r.teacher_name }}</td>
                  <td class="text-xs text-slate-600">{{ r.phone || r.email || '—' }}</td>
                  <td class="text-center">
                    <span
                      class="status-pill"
                      :class="{
                        'pill-present': r.status === 'PRESENT',
                        'pill-absent': r.status === 'ABSENT',
                        'pill-late': r.status === 'LATE',
                        'pill-leave': r.status === 'ON_LEAVE'
                      }"
                    >
                      {{ r.status }}
                    </span>
                  </td>
                  <td class="text-xs text-slate-700 italic">{{ r.reason || '—' }}</td>
                  <td class="text-xs text-slate-500">{{ r.recorded_by_name || 'Admin' }}</td>
                  <td class="text-xs text-slate-400">{{ r.recorded_at ? new Date(r.recorded_at).toLocaleTimeString() : '—' }}</td>
                </tr>

                <tr v-if="!teacherRecordsResponse?.items || teacherRecordsResponse.items.length === 0">
                  <td colspan="8" class="text-center py-8 text-slate-400">
                    No historical staff attendance records match the selected filters.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="teacherRecordsResponse && teacherRecordsResponse.total_pages > 1" class="pagination-bar">
            <button
              type="button"
              class="pg-btn"
              :disabled="teacherRecordsPage <= 1"
              @click="loadTeacherRecords(teacherRecordsPage - 1)"
            >
              &larr; Previous
            </button>
            <span class="pg-info">Page {{ teacherRecordsPage }} of {{ teacherRecordsResponse.total_pages }}</span>
            <button
              type="button"
              class="pg-btn"
              :disabled="teacherRecordsPage >= teacherRecordsResponse.total_pages"
              @click="loadTeacherRecords(teacherRecordsPage + 1)"
            >
              Next &rarr;
            </button>
          </div>
        </div>
      </section>
    </div>

    <!-- ========================================================================= -->
    <!-- STUDENT ABSENCE DATES INSPECTION MODAL -->
    <!-- ========================================================================= -->
    <div v-if="inspectedStudent" class="modal-backdrop" @click="closeInspectModal">
      <div class="modal-dialog" @click.stop>
        <div class="modal-header">
          <div>
            <h3 class="modal-title">{{ inspectedStudent.name }}</h3>
            <p class="modal-sub">
              {{ inspectedStudent.admission_number }} &bull; {{ inspectedStudent.class_name }} &bull;
              Total Absences: <strong>{{ inspectedStudent.absence_dates.length }}</strong>
            </p>
          </div>
          <button type="button" class="modal-close-btn" @click="closeInspectModal">&times;</button>
        </div>

        <div class="modal-body">
          <div v-if="inspectedStudent.absence_dates.length > 0" class="absence-log-list">
            <div
              v-for="(abs, aIdx) in inspectedStudent.absence_dates"
              :key="aIdx"
              class="absence-log-item"
            >
              <div class="abs-log-date">
                <span class="text-sm font-bold text-slate-800">{{ formatDate(abs.date) }}</span>
                <span v-if="abs.period" class="text-xs text-slate-500">{{ abs.period }}</span>
              </div>
              <div class="abs-log-detail">
                <span class="font-medium text-slate-800">{{ abs.subject_name || 'Subject' }}</span>
                <span v-if="abs.remarks" class="text-xs text-slate-500 italic">"{{ abs.remarks }}"</span>
              </div>
              <div class="abs-log-status">
                <span class="status-pill pill-absent">{{ abs.status }}</span>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-4 text-slate-400">
            No absences recorded for this student.
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn-outline" @click="closeInspectModal">Close</button>
        </div>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- STUDENT SUBJECT ATTENDANCE BREAKDOWN MODAL -->
    <!-- ========================================================================= -->
    <div v-if="isBreakdownModalOpen" class="modal-backdrop" @click="closeBreakdownModal">
      <div class="modal-dialog modal-lg" @click.stop>
        <div class="modal-header">
          <div>
            <div class="flex items-center gap-2 mb-1">
              <span class="badge-role">{{ selectedStudentBreakdown?.class_name || 'Class' }}</span>
              <code class="text-xs font-mono font-bold text-slate-700">{{ selectedStudentBreakdown?.admission_number }}</code>
            </div>
            <h3 class="modal-title">{{ selectedStudentBreakdown?.student_name || 'Student Attendance' }}</h3>
            <p class="modal-sub">
              Academic Year: <strong>{{ selectedStudentBreakdown?.academic_year }}</strong> &bull;
              Overall Attendance Rate: <strong class="text-blue-600">{{ selectedStudentBreakdown?.overall_percentage }}%</strong>
            </p>
          </div>
          <button type="button" class="modal-close-btn" @click="closeBreakdownModal">&times;</button>
        </div>

        <div class="modal-body">
          <div v-if="isLoadingBreakdown" class="py-12 text-center text-slate-500">
            <div class="spinner-ring mx-auto mb-2" />
            <p class="text-sm font-semibold">Loading student subject breakdown from database...</p>
          </div>

          <div v-else-if="selectedStudentBreakdown">
            <!-- Summary KPI Strip -->
            <div class="kpi-grid mb-5">
              <div class="kpi-card">
                <span class="kpi-title">Total Sessions</span>
                <span class="kpi-value text-slate-800">{{ selectedStudentBreakdown.total_sessions }}</span>
              </div>
              <div class="kpi-card">
                <span class="kpi-title">Present</span>
                <span class="kpi-value text-emerald-600">{{ selectedStudentBreakdown.total_present }}</span>
              </div>
              <div class="kpi-card">
                <span class="kpi-title">Late</span>
                <span class="kpi-value text-amber-600">{{ selectedStudentBreakdown.total_late }}</span>
              </div>
              <div class="kpi-card">
                <span class="kpi-title">Absent</span>
                <span class="kpi-value text-red-600">{{ selectedStudentBreakdown.total_absent }}</span>
              </div>
              <div class="kpi-card">
                <span class="kpi-title">Overall Rate</span>
                <span class="kpi-value text-blue-600">{{ selectedStudentBreakdown.overall_percentage }}%</span>
              </div>
            </div>

            <!-- Subject Breakdown Table (Exact Requested Format) -->
            <div class="content-panel mb-5">
              <div class="panel-header">
                <div>
                  <h4 class="font-bold text-slate-900 text-base">Subject Attendance Breakdown</h4>
                  <span class="text-xs text-slate-500">Actual database records for each enrolled subject</span>
                </div>
              </div>

              <div class="table-responsive">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>Subject</th>
                      <th class="text-center text-emerald-700">Present</th>
                      <th class="text-center text-red-700">Absent</th>
                      <th class="text-center text-amber-700">Late</th>
                      <th class="text-center">Attendance Rate</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="sub in selectedStudentBreakdown.by_subject" :key="sub.subject_id">
                      <td class="font-semibold text-slate-900">
                        {{ sub.subject_name }}
                        <span v-if="sub.subject_code" class="text-xs text-slate-400 font-normal">({{ sub.subject_code }})</span>
                      </td>
                      <td class="text-center font-bold text-emerald-600">{{ sub.present_count }}</td>
                      <td class="text-center font-bold text-red-600">{{ sub.absent_count }}</td>
                      <td class="text-center font-bold text-amber-600">{{ sub.late_count }}</td>
                      <td class="text-center">
                        <span class="pct-pill" :class="sub.attendance_percentage >= 85 ? 'pct-good' : (sub.attendance_percentage >= 70 ? 'pct-warn' : 'pct-danger')">
                          {{ sub.attendance_percentage }}%
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Audit Trail Records -->
            <div v-if="selectedStudentBreakdown.records && selectedStudentBreakdown.records.length > 0" class="content-panel">
              <div class="panel-header">
                <div>
                  <h4 class="font-bold text-slate-900 text-base">Complete Session Audit Log</h4>
                  <span class="text-xs text-slate-500">Date-by-date attendance roll call records</span>
                </div>
              </div>

              <div class="table-responsive">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Subject</th>
                      <th>Period</th>
                      <th>Teacher</th>
                      <th class="text-center">Status</th>
                      <th>Remarks</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="rec in selectedStudentBreakdown.records" :key="rec.id">
                      <td class="font-mono text-slate-800 text-xs">{{ formatDate(rec.date) }}</td>
                      <td class="font-medium text-slate-800">{{ rec.subject_name }}</td>
                      <td class="text-xs text-slate-500">{{ rec.period || '—' }}</td>
                      <td class="text-xs text-slate-600">{{ rec.teacher_name || 'Faculty' }}</td>
                      <td class="text-center">
                        <span
                          class="status-pill"
                          :class="rec.status === 'PRESENT' ? 'pill-present' : (rec.status === 'LATE' ? 'pill-late' : 'pill-absent')"
                        >
                          {{ rec.status }}
                        </span>
                      </td>
                      <td class="text-xs text-slate-500">{{ rec.remarks || '—' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn-outline" @click="closeBreakdownModal">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.attendance-admin-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
}

/* Toast */
.toast-alert {
  position: fixed;
  top: 1.5rem;
  right: 1.5rem;
  z-index: 9999;
  padding: 0.85rem 1.25rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}
.toast-alert.success {
  background-color: #ecfdf5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}
.toast-alert.error {
  background-color: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.header-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #ea580c, #c2410c);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 6px -1px rgba(234, 88, 12, 0.25);
  transition: all 0.3s ease;
}
.header-icon-box.teacher-theme {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  box-shadow: 0 4px 6px -1px rgba(2, 132, 199, 0.25);
}
.page-title {
  font-size: 1.375rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
  line-height: 1.25;
}
.page-subtitle {
  font-size: 0.8125rem;
  color: #64748b;
  margin: 0.25rem 0 0 0;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

/* Main Section Switcher */
.main-section-switcher {
  display: flex;
  gap: 0.75rem;
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 0.4rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}
.main-switch-btn {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  padding: 0.75rem 1.25rem;
  font-size: 0.9375rem;
  font-weight: 700;
  color: #64748b;
  border: none;
  background: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.main-switch-btn:hover {
  color: #0f172a;
  background-color: #f8fafc;
}
.main-switch-btn.active {
  background-color: #ea580c;
  color: #ffffff;
  box-shadow: 0 2px 4px rgba(234, 88, 12, 0.2);
}
.main-switch-btn.teacher-tab.active {
  background-color: #0284c7;
  color: #ffffff;
  box-shadow: 0 2px 4px rgba(2, 132, 199, 0.2);
}
.badge-role {
  background-color: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 0.15rem 0.45rem;
  border-radius: 9999px;
}

/* Buttons */
.btn-primary-orange {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #ea580c;
  color: #ffffff;
  font-size: 0.8125rem;
  font-weight: 600;
  padding: 0.55rem 1rem;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-primary-orange:hover:not(:disabled) {
  background-color: #c2410c;
}
.btn-primary-orange:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary-blue {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #0284c7;
  color: #ffffff;
  font-size: 0.8125rem;
  font-weight: 600;
  padding: 0.55rem 1rem;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-primary-blue:hover:not(:disabled) {
  background-color: #0369a1;
}
.btn-primary-blue:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-outline {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #ffffff;
  color: #334155;
  border: 1px solid #cbd5e1;
  font-size: 0.8125rem;
  font-weight: 600;
  padding: 0.55rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-outline:hover:not(:disabled) {
  background-color: #f8fafc;
  border-color: #94a3b8;
}
.btn-outline:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-sm {
  padding: 0.4rem 0.75rem;
  font-size: 0.75rem;
}

.btn-icon {
  width: 16px;
  height: 16px;
}

/* Daily Marker Bar */
.daily-marker-bar {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1rem 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}
.date-picker-wrap {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}
.form-input-date {
  padding: 0.45rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.8125rem;
  color: #0f172a;
  background-color: #ffffff;
  outline: none;
}
.form-input-date:focus {
  border-color: #0284c7;
}
.pill-today {
  background-color: #ecfdf5;
  color: #065f46;
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  border: 1px solid #a7f3d0;
}
.pill-future-blocked {
  background-color: #fef2f2;
  color: #991b1b;
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  border: 1px solid #fecaca;
}

.roster-metrics-strip {
  display: flex;
  gap: 1.25rem;
  align-items: center;
  background-color: #f8fafc;
  padding: 0.4rem 1rem;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}
.strip-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.strip-item.highlight {
  color: #0284c7;
  font-weight: 800;
}
.strip-label {
  font-size: 0.6875rem;
  text-transform: uppercase;
  color: #64748b;
  font-weight: 600;
}
.strip-num {
  font-size: 1.125rem;
  font-weight: 800;
}

.marker-actions {
  display: flex;
  gap: 0.65rem;
}

/* Status Radio Group (Pill Buttons) */
.status-radio-group {
  display: inline-flex;
  gap: 0.35rem;
  background-color: #f1f5f9;
  padding: 0.2rem;
  border-radius: 6px;
}
.status-choice-btn {
  border: none;
  background: none;
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 0.25rem 0.55rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s ease;
  color: #64748b;
}
.status-choice-btn.present.selected {
  background-color: #10b981;
  color: #ffffff;
}
.status-choice-btn.absent.selected {
  background-color: #ef4444;
  color: #ffffff;
}
.status-choice-btn.late.selected {
  background-color: #f59e0b;
  color: #ffffff;
}
.status-choice-btn.on-leave.selected {
  background-color: #0284c7;
  color: #ffffff;
}

.reason-input {
  width: 100%;
  padding: 0.35rem 0.65rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.75rem;
  color: #1e293b;
  outline: none;
}
.reason-input:focus {
  border-color: #0284c7;
}

/* Filter Card */
.filter-card {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1rem 1.25rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}
.filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  align-items: center;
}
.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.filter-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #475569;
}
.filter-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.8125rem;
  color: #1e293b;
  background-color: #ffffff;
  outline: none;
}
.filter-select:focus {
  border-color: #ea580c;
}
.threshold-group {
  display: flex;
  flex-direction: column;
}
.threshold-input-wrap {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.threshold-range {
  flex: 1;
  accent-color: #ea580c;
}
.threshold-badge {
  background-color: #fef2f2;
  color: #dc2626;
  font-weight: 700;
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  border: 1px solid #fca5a5;
}

/* Navigation Tabs */
.nav-tabs-wrapper {
  border-bottom: 2px solid #e2e8f0;
}
.nav-tabs-list {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
}
.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
  border: none;
  background: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  margin-bottom: -2px;
  transition: all 0.2s ease;
  white-space: nowrap;
}
.tab-btn:hover {
  color: #0f172a;
}
.tab-btn.active {
  color: #ea580c;
  border-bottom-color: #ea580c;
}
.teacher-section-wrap .tab-btn.active {
  color: #0284c7;
  border-bottom-color: #0284c7;
}
.tab-icon {
  width: 18px;
  height: 18px;
}
.badge-alert {
  background-color: #ef4444;
  color: #ffffff;
  font-size: 0.6875rem;
  padding: 0.1rem 0.4rem;
  border-radius: 9999px;
  font-weight: 700;
}

/* Tab Content */
.tab-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* KPI Cards */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}
.kpi-card {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.1rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}
.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.kpi-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.kpi-icon-wrap {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.kpi-value {
  font-size: 1.75rem;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.1;
}
.kpi-footer {
  font-size: 0.6875rem;
}

/* Panels */
.content-panel {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
}
.panel-title {
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}
.panel-sub {
  font-size: 0.75rem;
  color: #64748b;
}

/* Split Grid */
.dashboard-split-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}
@media (max-width: 900px) {
  .dashboard-split-grid {
    grid-template-columns: 1fr;
  }
}

/* Daily Chart Bars */
.daily-chart-list {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}
.daily-bar-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.date-col {
  width: 60px;
  display: flex;
  flex-direction: column;
}
.day-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #1e293b;
}
.date-sub {
  font-size: 0.6875rem;
  color: #64748b;
}
.bar-track {
  flex: 1;
  height: 12px;
  background-color: #f1f5f9;
  border-radius: 9999px;
  overflow: hidden;
  display: flex;
}
.bar-present {
  background-color: #10b981;
  height: 100%;
}
.bar-absent {
  background-color: #ef4444;
  height: 100%;
}
.stat-col {
  width: 100px;
  text-align: right;
  display: flex;
  flex-direction: column;
}
.stat-pct {
  font-size: 0.75rem;
  font-weight: 700;
  color: #10b981;
}
.stat-pct.low {
  color: #ef4444;
}
.stat-counts {
  font-size: 0.6875rem;
  color: #64748b;
}

/* Session feed */
.session-feed {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  max-height: 380px;
  overflow-y: auto;
}
.session-card {
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background-color: #f8fafc;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.sess-header {
  display: flex;
  justify-content: space-between;
}
.sess-class {
  font-weight: 700;
  font-size: 0.8125rem;
  color: #0f172a;
}
.sess-date {
  font-size: 0.6875rem;
  color: #64748b;
}
.sess-sub-line {
  font-size: 0.75rem;
  color: #475569;
}
.sess-meta-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.25rem;
}
.sess-teacher {
  font-size: 0.6875rem;
  color: #64748b;
}
.sess-badge {
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
}
.sess-badge.good {
  background-color: #ecfdf5;
  color: #047857;
}
.sess-badge.alert {
  background-color: #fef2f2;
  color: #b91c1c;
}

/* Tables */
.table-responsive {
  overflow-x: auto;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8125rem;
}
.data-table th {
  background-color: #f8fafc;
  color: #475569;
  font-weight: 600;
  text-align: left;
  padding: 0.65rem 0.75rem;
  border-bottom: 1px solid #cbd5e1;
  white-space: nowrap;
}
.data-table td {
  padding: 0.65rem 0.75rem;
  border-bottom: 1px solid #e2e8f0;
  vertical-align: middle;
}
.data-table tr:hover {
  background-color: #f8fafc;
}

/* Pills */
.status-pill {
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border-radius: 9999px;
  display: inline-block;
}
.pill-good, .pill-present {
  background-color: #ecfdf5;
  color: #065f46;
}
.pill-warn, .pill-late {
  background-color: #fffbeb;
  color: #b45309;
}
.pill-absent {
  background-color: #fef2f2;
  color: #991b1b;
}
.pill-leave {
  background-color: #f0f9ff;
  color: #0369a1;
}

.pct-pill {
  font-weight: 700;
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
}
.pct-good {
  background-color: #ecfdf5;
  color: #047857;
}
.pct-warn {
  background-color: #fffbeb;
  color: #b45309;
}
.pct-danger {
  background-color: #fef2f2;
  color: #b91c1c;
}

.absence-chips-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  align-items: center;
}
.absence-badge {
  background-color: #fee2e2;
  color: #991b1b;
  font-size: 0.6875rem;
  font-weight: 600;
  padding: 0.15rem 0.35rem;
  border-radius: 4px;
}
.more-badge {
  background-color: #e2e8f0;
  color: #475569;
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 0.15rem 0.35rem;
  border-radius: 4px;
  cursor: pointer;
}

.badge-critical {
  background-color: #ef4444;
  color: #ffffff;
  font-size: 0.625rem;
  font-weight: 700;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  margin-left: 0.5rem;
}
.badge-warning {
  background-color: #f97316;
  color: #ffffff;
  font-size: 0.625rem;
  font-weight: 700;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  margin-left: 0.5rem;
}

.rank-circle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #f1f5f9;
  font-size: 0.75rem;
}
.rank-circle.top-rank {
  background-color: #fee2e2;
  color: #dc2626;
  font-weight: 800;
}

.guardian-contact-cell {
  display: flex;
  flex-direction: column;
}
.g-name {
  font-size: 0.75rem;
  font-weight: 600;
  color: #1e293b;
}
.g-phone {
  font-size: 0.6875rem;
  color: #0284c7;
  text-decoration: none;
}
.btn-inspect {
  font-size: 0.6875rem;
  font-weight: 600;
  color: #ea580c;
  background: #fff7ed;
  border: 1px solid #ffedd5;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
}
.btn-breakdown {
  color: #1e3a8a;
  background: #eff6ff;
  border-color: #dbeafe;
}
.btn-breakdown:hover {
  background: #dbeafe;
  color: #1d4ed8;
}
.btn-student-link {
  background: none;
  border: none;
  padding: 0;
  font-weight: 600;
  color: #1e3a8a;
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 2px;
}
.btn-student-link:hover {
  color: #2563eb;
}

.class-summary-card {
  background: linear-gradient(135deg, #0f172a, #1e293b);
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  color: #ffffff;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.cls-title-box {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
}
.cls-name {
  font-size: 1.25rem;
  font-weight: 800;
  margin: 0;
}
.cls-meta-chips {
  display: flex;
  gap: 0.5rem;
}
.chip {
  background-color: rgba(255, 255, 255, 0.12);
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  font-size: 0.75rem;
}
.cls-stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 0.75rem;
}
.stat-tile {
  background-color: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
}
.stat-tile.highlight {
  background-color: rgba(2, 132, 199, 0.2);
  border-color: rgba(2, 132, 199, 0.4);
}
.tile-val {
  font-size: 1.5rem;
  font-weight: 800;
}
.tile-lbl {
  font-size: 0.6875rem;
  color: #94a3b8;
  margin-top: 0.2rem;
}

.action-buttons-wrap {
  display: flex;
  gap: 0.5rem;
}

.select-prompt-card {
  background-color: #ffffff;
  border: 2px dashed #cbd5e1;
  border-radius: 12px;
  padding: 3rem 1.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}
.prompt-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}
.prompt-sub {
  font-size: 0.8125rem;
  color: #64748b;
  max-width: 440px;
  margin: 0;
}

.inline-filters-row {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}
.search-box {
  display: flex;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  overflow: hidden;
}
.search-input {
  border: none;
  padding: 0.4rem 0.65rem;
  font-size: 0.75rem;
  outline: none;
  width: 190px;
}
.filter-search-input {
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  padding: 0.4rem 0.75rem;
  font-size: 0.75rem;
  outline: none;
  width: 240px;
  background-color: #ffffff;
  color: #1e293b;
  transition: border-color 0.15s ease;
}
.filter-search-input:focus {
  border-color: #ea580c;
  box-shadow: 0 0 0 2px rgba(234, 88, 12, 0.15);
}
.search-btn {
  background-color: #f1f5f9;
  border: none;
  border-left: 1px solid #cbd5e1;
  padding: 0.4rem 0.65rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
}
.filter-select-sm {
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  padding: 0.4rem 0.65rem;
  font-size: 0.75rem;
  background-color: #ffffff;
  outline: none;
}

.pagination-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.75rem;
  border-top: 1px solid #e2e8f0;
}
.pg-btn {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  padding: 0.35rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #334155;
  cursor: pointer;
}
.pg-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.pg-info {
  font-size: 0.75rem;
  color: #64748b;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(2px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}
.modal-dialog {
  background-color: #ffffff;
  border-radius: 12px;
  width: 100%;
  max-width: 580px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  max-height: 85vh;
}
.modal-dialog.modal-lg {
  max-width: 900px;
}
.modal-header {
  padding: 1.25rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.modal-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}
.modal-sub {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0.25rem 0 0 0;
}
.modal-close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #94a3b8;
  cursor: pointer;
  line-height: 1;
}
.modal-body {
  padding: 1.25rem;
  overflow-y: auto;
}
.modal-footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
}
.absence-log-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.absence-log-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.65rem 0.85rem;
  border: 1px solid #fecaca;
  border-radius: 8px;
  background-color: #fef2f2;
}
.abs-log-date {
  display: flex;
  flex-direction: column;
}
.abs-log-detail {
  display: flex;
  flex-direction: column;
}
</style>
