import { TimetableEntry, Exam, ExamResult, TeacherAssignment } from './school';

export interface TeacherPortalProfile {
  id: number;
  teacher_number: string;
  first_name: string;
  middle_name?: string | null;
  last_name: string;
  gender: string;
  email: string;
  phone?: string | null;
  address?: string | null;
  qualification?: string | null;
  hire_date?: string | null;
  status: string;
  full_name: string;
  assignments: TeacherAssignment[];
}

export interface TeacherTodayAttendanceItem {
  class_id: number;
  class_name: string;
  subject_id: number;
  subject_name: string;
  period?: string | null;
  is_recorded: boolean;
  total_students: number;
  present_count: number;
  absent_count: number;
}

export interface TeacherPendingSubmissionWidget {
  exam_id: number;
  exam_name: string;
  class_id: number;
  class_name: string;
  subject_id: number;
  subject_name: string;
  academic_year: string;
  status: string;
  total_students: number;
  completed_students: number;
  pending_students: number;
}

export interface TeacherDashboardData {
  teacher: TeacherPortalProfile;
  total_classes: number;
  total_subjects: number;
  total_students: number;
  today_classes_count: number;
  pending_results_count?: number;
  today_attendance_summary?: TeacherTodayAttendanceItem[];
  pending_submissions?: TeacherPendingSubmissionWidget[];
  assigned_classes: TeacherAssignment[];
  upcoming_timetables: TimetableEntry[];
  active_exams: Exam[];
}

export interface TeacherClassDetailSubject {
  id: number;
  name: string;
  code: string;
}

export interface TeacherClassDetailResponse {
  class_id: number;
  name: string;
  code: string;
  section?: string | null;
  academic_year: string;
  capacity: number;
  enrolled_students_count: number;
  my_subjects: TeacherClassDetailSubject[];
  students: {
    id: number;
    first_name: string;
    middle_name?: string | null;
    last_name: string;
    admission_number: string;
    gender: string;
    status: string;
    has_portal_access: boolean;
  }[];
  timetables: TimetableEntry[];
  exams: Exam[];
  attendance_rate: number;
}

export interface TeacherAssignedStudent {
  student_id: number;
  admission_number: string;
  first_name: string;
  middle_name?: string | null;
  last_name: string;
  gender: string;
  class_id: number;
  class_name: string;
  academic_year: string;
  section?: string | null;
}

export interface StudentPortalProfile {
  id: number;
  admission_number: string;
  first_name: string;
  middle_name?: string | null;
  last_name: string;
  gender: string;
  date_of_birth?: string | null;
  phone?: string | null;
  address?: string | null;
  guardian_name?: string | null;
  guardian_phone?: string | null;
  admission_date?: string | null;
  status: string;
  full_name: string;
  current_class?: {
    id: number;
    name: string;
    code: string;
    academic_year: string;
    section?: string | null;
  } | null;
}

export interface StudentDashboardData {
  student: StudentPortalProfile;
  current_class?: {
    id: number;
    name: string;
    code: string;
    academic_year: string;
  } | null;
  enrolled_subjects_count: number;
  total_fees_due: number;
  total_fees_paid: number;
  outstanding_balance: number;
  today_schedule: TimetableEntry[];
  recent_exam_results: ExamResult[];
}
