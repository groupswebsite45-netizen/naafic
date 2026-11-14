import { StudentSubjectAttendanceBreakdown } from './attendance';

export interface AdminTeacherOption {
  id: number;
  name: string;
  employee_number?: string | null;
  class_id?: number | null;
  subject_id?: number | null;
  academic_year?: string | null;
}

export interface AdminClassOption {
  id: number;
  name: string;
  code: string;
  academic_year: string;
  grade_level?: string | null;
  section?: string | null;
}

export interface AdminSubjectOption {
  id: number;
  name: string;
  code: string;
  class_id?: number | null;
  academic_year?: string | null;
}

export interface AdminMonthOption {
  value: number;
  name: string;
}

export interface AdminAttendanceFilterOptionsResponse {
  academic_years: string[];
  classes: AdminClassOption[];
  subjects: AdminSubjectOption[];
  teachers: AdminTeacherOption[];
  months: AdminMonthOption[];
}

export interface AdminAttendanceKPIs {
  total_students: number;
  today_present: number;
  today_absent: number;
  today_late: number;
  today_attendance_percentage: number;
  overall_attendance_percentage: number;
  frequent_absentees_count: number;
}

export interface AdminAttendanceDailySummaryItem {
  date: string;
  day_name: string;
  present_count: number;
  absent_count: number;
  late_count: number;
  attendance_percentage: number;
}

export interface AdminAttendanceWeeklySummaryItem {
  week_label: string;
  start_date: string;
  end_date: string;
  present_count: number;
  absent_count: number;
  attendance_percentage: number;
}

export interface AdminAttendanceMonthlySummaryItem {
  month_name: string;
  month: number;
  year: number;
  present_count: number;
  absent_count: number;
  attendance_percentage: number;
}

export interface AdminAttendanceRecentSessionItem {
  date: string;
  period?: string | null;
  class_id: number;
  class_name: string;
  subject_id: number;
  subject_name: string;
  teacher_name?: string | null;
  total_students: number;
  present_count: number;
  late_count?: number;
  absent_count: number;
  attendance_percentage: number;
  recorded_at?: string | null;
}

export interface AbsenceDateDetail {
  date: string;
  period?: string | null;
  subject_name?: string | null;
  status: string;
  remarks?: string | null;
}

export interface AdminAttendanceFrequentAbsenteeItem {
  student_id: number;
  student_name: string;
  admission_number: string;
  class_id: number;
  class_name: string;
  gender?: string | null;
  guardian_name?: string | null;
  guardian_phone?: string | null;
  total_sessions: number;
  present_count: number;
  absent_count: number;
  late_count: number;
  attendance_percentage: number;
  last_absent_date?: string | null;
  absence_dates: AbsenceDateDetail[];
}

export interface AdminAttendanceDashboardResponse {
  kpis: AdminAttendanceKPIs;
  daily_summary: AdminAttendanceDailySummaryItem[];
  weekly_summary: AdminAttendanceWeeklySummaryItem[];
  monthly_summary: AdminAttendanceMonthlySummaryItem[];
  frequent_absentees: AdminAttendanceFrequentAbsenteeItem[];
  recent_sessions: AdminAttendanceRecentSessionItem[];
}

export interface AdminAttendanceRecordItem {
  id: number;
  date: string;
  period?: string | null;
  student_id: number;
  student_name: string;
  admission_number: string;
  class_id: number;
  class_name: string;
  subject_id: number;
  subject_name: string;
  teacher_name?: string | null;
  status: string;
  remarks?: string | null;
  recorded_at?: string | null;
}

export interface AdminAttendanceRecordsListResponse {
  items: AdminAttendanceRecordItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface AdminClassInfo {
  id: number;
  name: string;
  code: string;
  academic_year: string;
  total_enrolled: number;
}

export interface AdminClassAttendanceSummaryStats {
  total_sessions: number;
  total_records: number;
  present_count: number;
  absent_count: number;
  late_count: number;
  attendance_percentage: number;
}

export interface AdminClassStudentAttendanceItem {
  student_id: number;
  student_name: string;
  admission_number: string;
  gender?: string | null;
  guardian_name?: string | null;
  guardian_phone?: string | null;
  total_sessions: number;
  days_present: number;
  days_absent: number;
  days_late: number;
  attendance_percentage: number;
  absence_dates: AbsenceDateDetail[];
  daily_status: Record<string, string>;
  subject_breakdown?: StudentSubjectAttendanceBreakdown[];
}

export interface AdminClassAttendanceReportResponse {
  class_info: AdminClassInfo;
  summary: AdminClassAttendanceSummaryStats;
  students: AdminClassStudentAttendanceItem[];
  dates_header: string[];
  academic_year: string;
  period_label: string;
}

