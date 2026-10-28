export interface StudentProfileData {
  id: number;
  user_id?: number | null;
  admission_number: string;
  first_name: string;
  middle_name?: string | null;
  last_name: string;
  full_name: string;
  gender: string;
  date_of_birth?: string | null;
  phone?: string | null;
  email?: string | null;
  address?: string | null;
  guardian_name?: string | null;
  guardian_phone?: string | null;
  guardian_email?: string | null;
  guardian_relationship?: string | null;
  admission_date?: string | null;
  status: string;
  current_class_name?: string | null;
  current_class_code?: string | null;
  academic_year?: string | null;
  portal_account_status: string;
}

export interface StudentSubjectDetail {
  id: number;
  name: string;
  code: string;
  department?: string | null;
  teacher_name?: string | null;
  status: string;
}

export interface EnrollmentHistoryItem {
  academic_year: string;
  class_name: string;
  class_code: string;
  section?: string | null;
  status: string;
  roll_number?: string | null;
}

export interface StudentClassDetails {
  school_class?: {
    id: number;
    name: string;
    code: string;
    section?: string | null;
    academic_year: string;
    capacity: number;
    description?: string | null;
    status: string;
  } | null;
  academic_year?: string | null;
  section?: string | null;
  class_teacher_name?: string | null;
  capacity: number;
  classmates_count: number;
  subjects: StudentSubjectDetail[];
  enrollment_history: EnrollmentHistoryItem[];
}

export interface TimetableSlot {
  id: number;
  class_id: number;
  subject_id: number;
  teacher_id?: number | null;
  academic_year: string;
  day_of_week: string;
  start_time: string;
  end_time: string;
  room?: string | null;
  room_number?: string | null;
  status: string;
  is_break?: boolean;
  period_number?: number | null;
  subject_name?: string | null;
  teacher_name?: string | null;
  subject?: {
    id: number;
    name: string;
    code: string;
  } | null;
  teacher?: {
    id: number;
    first_name: string;
    last_name: string;
    full_name?: string;
  } | null;
}

export interface AttendanceOverallSummary {
  total_classes: number;
  present_count: number;
  absent_count: number;
  excused_count: number;
  attendance_percentage: number;
}

export interface SubjectAttendanceSummary {
  subject_id: number;
  subject_name: string;
  subject_code?: string | null;
  total_classes: number;
  present_count: number;
  absent_count: number;
  excused_count: number;
  attendance_percentage: number;
}

export interface AttendanceRecordItem {
  id: number;
  date: string;
  subject_id: number;
  subject_name: string;
  subject_code?: string | null;
  period?: string | null;
  status: string; // "PRESENT", "ABSENT", "EXCUSED", "LATE"
  teacher_name?: string | null;
  remarks?: string | null;
}

export interface StudentAttendanceData {
  academic_year: string;
  summary: AttendanceOverallSummary;
  by_subject: SubjectAttendanceSummary[];
  history: AttendanceRecordItem[];
}

export interface FeePaymentItem {
  id: number;
  student_fee_id: number;
  student_id: number;
  receipt_number: string;
  amount_paid: number;
  payment_date: string;
  payment_method: string;
  reference_number?: string | null;
  notes?: string | null;
}

export interface StudentFeeItem {
  id: number;
  student_id: number;
  fee_structure_id: number;
  amount_due: number;
  discount_amount: number;
  due_date: string;
  status: string;
  net_amount: number;
  total_paid: number;
  balance_remaining: number;
  fee_structure?: {
    id: number;
    name: string;
    academic_year: string;
    amount: number;
    due_date: string;
    description?: string | null;
  } | null;
  payments: FeePaymentItem[];
}

export interface StudentFeesData {
  summary: {
    total_billed: number;
    total_paid: number;
    total_outstanding: number;
    is_cleared: boolean;
  };
  fees: StudentFeeItem[];
}

export interface LatestExamResultSummary {
  exam_name: string;
  academic_year: string;
  subject_name: string;
  marks_obtained?: number | null;
  total_marks: number;
  percentage?: number | null;
  grade?: string | null;
  released_at?: string | null;
}

export interface StudentExamResultItem {
  id: number;
  exam_id: number;
  class_id?: number | null;
  student_id: number;
  subject_id: number;
  marks_obtained?: number | null;
  grade?: string | null;
  remarks?: string | null;
  status: string;
  attendance_status: string;
  exam_name?: string | null;
  academic_year?: string | null;
  subject_name?: string | null;
  subject_code?: string | null;
  total_marks: number;
  percentage?: number | null;
  created_at?: string | null;
}

export interface StudentDashboardData {
  student: StudentProfileData;
  current_class?: {
    id: number;
    name: string;
    code: string;
    academic_year: string;
    section?: string | null;
  } | null;
  academic_year?: string | null;
  enrolled_subjects_count: number;
  attendance_summary?: AttendanceOverallSummary | null;
  total_fees_due: number;
  total_fees_paid: number;
  outstanding_balance: number;
  latest_exam_result?: LatestExamResultSummary | null;
  next_class_period?: TimetableSlot | null;
  today_schedule: TimetableSlot[];
  recent_exam_results: StudentExamResultItem[];
}
