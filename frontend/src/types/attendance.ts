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
  total_students: number;
  present_count: number;
  absent_count: number;
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
