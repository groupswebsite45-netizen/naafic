export interface TeacherAttendanceClassOption {
  id: number;
  name: string;
  code: string;
  academic_year: string;
}

export interface TeacherAttendanceSubjectOption {
  id: number;
  name: string;
  code: string;
  class_id: number;
  academic_year?: string | null;
}

export interface TeacherAttendanceOptionsResponse {
  academic_years: string[];
  classes: TeacherAttendanceClassOption[];
  subjects: TeacherAttendanceSubjectOption[];
}

export interface StudentAttendanceRosterItem {
  student_id: number;
  student_name: string;
  admission_number: string;
  gender?: string;
  attendance_id?: number | null;
  status: 'PRESENT' | 'ABSENT' | 'EXCUSED' | 'LATE';
  remarks?: string | null;
}

export interface TeacherAttendanceRosterResponse {
  class_id: number;
  class_name: string;
  subject_id: number;
  subject_name: string;
  academic_year: string;
  date: string;
  period?: string | null;
  is_recorded: boolean;
  is_locked?: boolean;
  submitted_at?: string | null;
  submitted_by_name?: string | null;
  total_students: number;
  present_count: number;
  absent_count: number;
  late_count: number;
  students: StudentAttendanceRosterItem[];
}

export interface StudentAttendanceEntry {
  student_id: number;
  status: 'PRESENT' | 'ABSENT' | 'EXCUSED' | 'LATE';
  remarks?: string | null;
}

export interface TeacherSaveAttendancePayload {
  class_id: number;
  subject_id: number;
  academic_year: string;
  date: string;
  period?: string | null;
  entries: StudentAttendanceEntry[];
}

export interface TeacherAttendanceSessionItem {
  session_key: string;
  date: string;
  period?: string | null;
  class_id: number;
  class_name: string;
  subject_id: number;
  subject_name: string;
  academic_year: string;
  total_students: number;
  present_count: number;
  absent_count: number;
  late_count: number;
  attendance_percentage: number;
  recorded_at?: string | null;
}

export interface AbsentRecordDetail {
  date: string;
  period?: string | null;
  subject_name?: string | null;
  status: string;
  remarks?: string | null;
}

export interface TeacherStudentAttendanceSummaryItem {
  student_id: number;
  student_name: string;
  admission_number: string;
  class_id: number;
  class_name: string;
  total_sessions: number;
  present_count: number;
  absent_count: number;
  late_count: number;
  excused_count: number;
  attendance_percentage: number;
  absent_history: AbsentRecordDetail[];
}

export interface TeacherAttendanceSummaryResponse {
  class_id: number;
  class_name: string;
  subject_id?: number | null;
  subject_name?: string | null;
  total_sessions: number;
  students: TeacherStudentAttendanceSummaryItem[];
}

export interface StudentSubjectAttendanceBreakdown {
  subject_id: number;
  subject_name: string;
  subject_code?: string | null;
  present_count: number;
  absent_count: number;
  late_count: number;
  excused_count: number;
  total_sessions: number;
  attendance_percentage: number;
}

export interface AttendanceRecordResponse {
  id: number;
  date: string;
  subject_id: number;
  subject_name: string;
  subject_code?: string | null;
  period?: string | null;
  status: string;
  teacher_name?: string | null;
  remarks?: string | null;
}

export interface StudentAttendanceHistoryDetailResponse {
  student_id: number;
  student_name: string;
  admission_number: string;
  class_id: number;
  class_name: string;
  academic_year: string;
  total_sessions: number;
  total_present: number;
  total_absent: number;
  total_late: number;
  overall_percentage: number;
  by_subject: StudentSubjectAttendanceBreakdown[];
  records: AttendanceRecordResponse[];
}
