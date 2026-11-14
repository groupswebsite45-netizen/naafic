export interface TeacherRosterAttendanceItem {
  teacher_id: number;
  teacher_number: string;
  teacher_name: string;
  gender?: string | null;
  phone?: string | null;
  email?: string | null;
  qualification?: string | null;
  employment_status?: string | null;
  status: 'PRESENT' | 'ABSENT' | 'LATE' | 'ON_LEAVE';
  reason?: string | null;
  attendance_id?: number | null;
  is_saved: boolean;
}

export interface TeacherDailyRosterResponse {
  date: string;
  academic_year: string;
  is_recorded: boolean;
  total_teachers: number;
  present_count: number;
  absent_count: number;
  late_count: number;
  on_leave_count: number;
  teachers: TeacherRosterAttendanceItem[];
}

export interface TeacherSaveEntry {
  teacher_id: number;
  status: 'PRESENT' | 'ABSENT' | 'LATE' | 'ON_LEAVE';
  reason?: string | null;
}

export interface TeacherBulkSavePayload {
  date: string;
  academic_year: string;
  entries: TeacherSaveEntry[];
}

export interface TeacherAttendanceKPIs {
  total_teachers: number;
  today_present: number;
  today_absent: number;
  today_late: number;
  today_on_leave: number;
  today_attendance_percentage: number;
  overall_attendance_percentage: number;
}

export interface TeacherAttendanceDailySummaryItem {
  date: string;
  day_name: string;
  present_count: number;
  absent_count: number;
  late_count: number;
  on_leave_count: number;
  attendance_percentage: number;
}

export interface TeacherAttendanceMonthlySummaryItem {
  month_name: string;
  month: number;
  year: number;
  present_count: number;
  absent_count: number;
  late_count: number;
  on_leave_count: number;
  attendance_percentage: number;
}

export interface TeacherAttendanceDashboardResponse {
  kpis: TeacherAttendanceKPIs;
  daily_summary: TeacherAttendanceDailySummaryItem[];
  monthly_summary: TeacherAttendanceMonthlySummaryItem[];
}

export interface TeacherAttendanceRecordItem {
  id: number;
  teacher_id: number;
  teacher_name: string;
  teacher_number: string;
  phone?: string | null;
  email?: string | null;
  date: string;
  academic_year: string;
  status: 'PRESENT' | 'ABSENT' | 'LATE' | 'ON_LEAVE';
  reason?: string | null;
  recorded_by_name?: string | null;
  recorded_at?: string | null;
}

export interface TeacherAttendanceRecordsResponse {
  items: TeacherAttendanceRecordItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface TeacherStaffAttendanceSummaryItem {
  teacher_id: number;
  teacher_name: string;
  teacher_number: string;
  gender?: string | null;
  phone?: string | null;
  email?: string | null;
  total_days: number;
  days_present: number;
  days_absent: number;
  days_late: number;
  days_on_leave: number;
  attendance_percentage: number;
  last_attendance_date?: string | null;
  last_status?: string | null;
}

export interface StaffAttendanceSummaryResponse {
  academic_year: string;
  period_label: string;
  total_teachers: number;
  overall_percentage: number;
  total_present_days: number;
  total_absent_days: number;
  total_late_days: number;
  total_leave_days: number;
  teachers: TeacherStaffAttendanceSummaryItem[];
}

