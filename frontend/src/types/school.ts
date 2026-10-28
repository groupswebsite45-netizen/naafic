export interface SchoolClass {
  id: number;
  name: string;
  code: string;
  division: 'PRIMARY' | 'SECONDARY' | string;
  level: string;
  academic_year: string;
  section?: string | null;
  capacity: number;
  description?: string | null;
  status: string;
  created_at: string;
  updated_at: string;
  students_count?: number;
  teachers_count?: number;
  subjects_count?: number;
  available_seats?: number;
  utilization_rate?: number;
  capacity_status?: 'NORMAL' | 'NEAR_CAPACITY' | 'FULL' | 'OVER_CAPACITY' | string;
}

export interface ClassSummary {
  total_classes: number;
  active_classes: number;
  total_students_enrolled: number;
  available_seats: number;
  near_capacity_classes: number;
}

export interface ClassFilterParams {
  query?: string;
  academic_year?: string;
  division?: string;
  status?: string;
  level?: string;
  section?: string;
  capacity_filter?: string;
  skip?: number;
  limit?: number;
  page?: number;
  page_size?: number;
}

export interface ClassCapacityMetrics {
  enrolled: number;
  capacity: number;
  available_seats: number;
  utilization_rate: number;
  capacity_status: 'NORMAL' | 'NEAR_CAPACITY' | 'FULL' | 'OVER_CAPACITY' | string;
}

export interface ClassEnrollmentStudent {
  id: number;
  student_id: number;
  admission_number: string;
  full_name: string;
  gender: string;
  status: string;
  has_portal_access: boolean;
  enrollment_date: string;
  academic_year: string;
}

export interface ClassTeacherAssignmentItem {
  id: number;
  teacher_id: number;
  teacher_number: string;
  full_name: string;
  subject_id: number;
  subject_name: string;
  subject_code: string;
  academic_year: string;
  status: string;
}

export interface ClassSubjectItem {
  id: number;
  code: string;
  name: string;
  department?: string | null;
  teacher_id?: number | null;
  teacher_name?: string | null;
  status: string;
}

export interface ClassTimetableItem {
  id: number;
  day_of_week: string;
  start_time: string;
  end_time: string;
  subject_name: string;
  subject_code: string;
  teacher_name?: string | null;
  room?: string | null;
  status: string;
}

export interface ClassExamItem {
  id: number;
  name: string;
  exam_type: string;
  academic_year: string;
  term?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  status: string;
}

export interface ClassFullProfile extends SchoolClass {
  capacity_metrics: ClassCapacityMetrics;
  students: ClassEnrollmentStudent[];
  teachers: ClassTeacherAssignmentItem[];
  subjects: ClassSubjectItem[];
  timetables: ClassTimetableItem[];
  exams: ClassExamItem[];
}

export interface Subject {
  id: number;
  name: string;
  code: string;
  division?: 'PRIMARY' | 'SECONDARY' | 'ALL' | string;
  applicable_levels?: string | null;
  department?: string | null;
  description?: string | null;
  status: string;
  created_at: string;
  updated_at: string;
  classes_count?: number;
  teachers_count?: number;
  timetables_count?: number;
  exams_count?: number;
}

export interface SubjectSummary {
  total_subjects: number;
  active_subjects: number;
  assigned_subjects: number;
  unassigned_subjects: number;
  departments_count: number;
}

export interface SubjectFilterParams {
  query?: string;
  search?: string;
  division?: string;
  level?: string;
  class_id?: number;
  department?: string;
  status?: string;
  section?: string;
  assignment_state?: string;
  assigned_filter?: string;
  academic_year?: string;
  skip?: number;
  limit?: number;
  page?: number;
  page_size?: number;
}

export interface SubjectClassAssignmentItem {
  id: number;
  class_id: number;
  class_name: string;
  class_code: string;
  section?: string | null;
  academic_year: string;
  teacher_id?: number | null;
  teacher_name?: string | null;
  periods_per_week?: number | null;
  students_count: number;
  status: string;
}

export interface SubjectTeacherAssignmentItem {
  id: number;
  teacher_id: number;
  teacher_number: string;
  full_name: string;
  teacher_name?: string;
  email?: string;
  section?: string | null;
  class_id: number;
  class_name: string;
  academic_year: string;
  status: string;
}

export interface SubjectTimetableItem {
  id: number;
  day_of_week: string;
  start_time: string;
  end_time: string;
  class_name: string;
  class_code: string;
  teacher_name?: string | null;
  room?: string | null;
  status: string;
}

export interface SubjectExamItem {
  id: number;
  name: string;
  exam_title?: string;
  exam_type: string;
  class_name: string;
  academic_year: string;
  term?: string;
  start_date?: string | null;
  exam_date?: string | null;
  max_marks: number;
  status: string;
}

export interface SubjectFullProfile extends Subject {
  classes: SubjectClassAssignmentItem[];
  teachers: SubjectTeacherAssignmentItem[];
  timetables: SubjectTimetableItem[];
  exams: SubjectExamItem[];
}

export interface TeacherAssignment {
  id: number;
  assignment_id?: number;
  teacher_id: number;
  class_id: number;
  subject_id: number;
  academic_year: string;
  section?: string | null;
  status: string;
  class_name?: string;
  class_code?: string;
  subject_name?: string;
  subject_code?: string;
  department?: string | null;
  teacher_name?: string;
  teacher_number?: string;
  student_count?: number;
  is_current_academic_year?: boolean;
  display_status?: 'ACTIVE' | 'HISTORICAL' | 'INACTIVE' | string;
  school_class?: SchoolClass | null;
  subject?: Subject | null;
  created_at: string;
}

export interface Teacher {
  id: number;
  teacher_number?: string;
  employee_id?: string;
  first_name: string;
  middle_name?: string | null;
  last_name: string;
  full_name?: string;
  gender: string;
  date_of_birth?: string | null;
  phone?: string | null;
  email: string;
  address?: string | null;
  qualification?: string | null;
  hire_date?: string | null;
  profile_photo_url?: string | null;
  status: string;
  user_id?: number | null;
  has_portal_access?: boolean;
  portal_username?: string | null;
  created_at: string;
  updated_at: string;
  assignments?: TeacherAssignment[];
  classes_count?: number;
  subjects_count?: number;
}

export interface TeacherSummary {
  total_teachers: number;
  active_teachers: number;
  inactive_teachers: number;
  unassigned_teachers: number;
}

export interface TeacherFilterParams {
  search?: string;
  status?: string;
  class_id?: number;
  subject_id?: number;
  has_portal?: boolean;
  academic_year?: string;
  page?: number;
  page_size?: number;
}

export interface TeacherTimetableSlot {
  id: number;
  class_id: number;
  subject_id: number;
  teacher_id?: number | null;
  academic_year: string;
  day_of_week: string;
  start_time: string;
  end_time: string;
  room?: string | null;
  status: string;
  school_class?: SchoolClass | null;
  subject?: Subject | null;
}

export interface TeacherFullProfile extends Teacher {
  portal_username?: string | null;
  portal_email?: string | null;
  timetables?: TeacherTimetableSlot[];
}

export interface StudentEnrollment {
  id: number;
  student_id: number;
  class_id: number;
  academic_year: string;
  section?: string | null;
  roll_number?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  enrollment_date?: string;
  status: string;
  class_name?: string;
  class_code?: string;
  school_class?: SchoolClass | null;
  created_at: string;
}

export interface Student {
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
  guardian_email?: string | null;
  guardian_relationship?: string | null;
  admission_date?: string | null;
  status: string;
  user_id?: number | null;
  full_name?: string;
  has_portal_access?: boolean;
  portal_username?: string | null;
  portal_is_active?: boolean;
  current_class?: SchoolClass | null;
  current_enrollment?: StudentEnrollment | null;
  enrollments?: StudentEnrollment[];
  created_at: string;
  updated_at: string;
}

export interface StudentSummary {
  total_students: number;
  active_students: number;
  inactive_students: number;
  unassigned_students: number;
}

export interface StudentFeeRecord {
  id: number;
  fee_name: string;
  academic_year: string;
  total_amount: number;
  paid_amount: number;
  balance: number;
  status: string;
  due_date?: string | null;
  created_at: string;
}

export interface StudentExamRecord {
  id: number;
  exam_name: string;
  exam_type: string;
  subject_name: string;
  academic_year: string;
  marks_obtained: number;
  total_marks: number;
  grade?: string | null;
  remarks?: string | null;
  exam_date?: string | null;
}

export interface StudentFullProfile extends Student {
  financial_summary: {
    total_billed: number;
    total_paid: number;
    outstanding_balance: number;
    fees_count?: number;
  };
  fees: StudentFeeRecord[];
  exam_results: StudentExamRecord[];
}

export interface StudentFilterParams {
  search?: string;
  class_id?: number;
  academic_year?: string;
  gender?: string;
  status?: string;
  has_portal?: boolean;
  page?: number;
  page_size?: number;
  skip?: number;
  limit?: number;
}

export interface TimetableConflictDetail {
  conflict_type: 'CLASS' | 'TEACHER' | 'ROOM';
  message: string;
  conflicting_slot_id: number;
  day_of_week: string;
  start_time: string;
  end_time: string;
  class_name: string;
  teacher_name?: string | null;
  room?: string | null;
  subject_name?: string | null;
}

export interface TimetableSummary {
  total_periods: number;
  scheduled_classes: number;
  assigned_teachers: number;
  active_rooms: number;
  conflicts_count: number;
  conflicts: TimetableConflictDetail[];
}

export interface TimetableFilterOptions {
  academic_years: string[];
  days_of_week: string[];
  rooms: string[];
}

export interface TimetableFilterParams {
  class_id?: number;
  teacher_id?: number;
  subject_id?: number;
  day_of_week?: string;
  academic_year?: string;
  room?: string;
  status?: string;
  skip?: number;
  limit?: number;
}

export interface TimetableCheckConflictPayload {
  class_id: number;
  subject_id: number;
  teacher_id?: number | null;
  academic_year: string;
  day_of_week: string;
  start_time: string;
  end_time: string;
  room?: string | null;
  exclude_id?: number | null;
}

export interface TimetableConflictCheckResponse {
  has_conflict: boolean;
  conflicts_count: number;
  conflicts: TimetableConflictDetail[];
}

export interface TimetableEntry {
  id: number;
  class_id: number;
  subject_id: number;
  teacher_id?: number | null;
  classroom_id?: number | null;
  academic_year: string;
  day_of_week: string;
  period_number?: number | null;
  start_time: string;
  end_time: string;
  room?: string | null;
  room_number?: string | null;
  status: string;
  is_break?: boolean;
  published_at?: string | null;
  published_by_id?: number | null;
  class_name?: string;
  class_code?: string;
  subject_name?: string;
  subject_code?: string;
  teacher_name?: string;
  school_class?: SchoolClass | null;
  subject?: Subject | null;
  teacher?: Teacher | null;
  created_at?: string;
  updated_at?: string;
}

export interface TimetableSetting {
  id?: number;
  school_id?: number;
  academic_year: string;
  education_level?: string | null;
  school_days: string[];
  start_time: string;
  end_time: string;
  period_duration_minutes: number;
  break_duration_minutes: number;
  lunch_duration_minutes: number;
  periods_per_day: number;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface TeacherAvailability {
  id?: number;
  school_id?: number;
  teacher_id: number;
  teacher_name?: string;
  academic_year: string;
  day_of_week: string;
  is_available: boolean;
  start_time?: string | null;
  end_time?: string | null;
  max_periods_per_day?: number | null;
  max_periods_per_week?: number | null;
  notes?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface ClassSubjectAssignmentInfo {
  subject_id: number;
  subject_name: string;
  subject_code?: string | null;
  teacher_id?: number | null;
  teacher_name?: string | null;
  weekly_lessons?: number;
}

export interface ClassTimetableOverview {
  class_id: number;
  class_name: string;
  academic_year: string;
  assigned_subjects: ClassSubjectAssignmentInfo[];
  existing_slots: TimetableEntry[];
  total_slots: number;
  published_slots: number;
  has_unresolved_conflicts: boolean;
  conflicts: TimetableConflictDetail[];
}

export interface TimetableGeneratePayload {
  class_id: number;
  academic_year: string;
  school_days?: string[];
  start_time?: string;
  end_time?: string;
  period_duration_minutes?: number;
  break_duration_minutes?: number;
  lunch_duration_minutes?: number;
  periods_per_day?: number;
  subject_lessons_distribution?: Record<string, number>;
  respect_teacher_availability?: boolean;
  overwrite_existing?: boolean;
}

export interface TimetableGenerateResponse {
  success: boolean;
  message: string;
  class_id: number;
  class_name: string;
  academic_year: string;
  total_slots_generated: number;
  unplaced_subjects: Array<{
    subject_id?: number;
    subject_name: string;
    requested: number;
    placed: number;
    reason: string;
  }>;
  conflicts: TimetableConflictDetail[];
  slots: TimetableEntry[];
}


export interface FeeStructure {
  id: number;
  name: string;
  academic_year: string;
  class_id?: number | null;
  amount: number;
  due_date?: string | null;
  description?: string | null;
  status: string;
  class_name?: string;
  class_code?: string;
  created_at: string;
  updated_at: string;
}

export interface FeePayment {
  id: number;
  student_fee_id: number;
  amount: number;
  payment_date: string;
  payment_method: string;
  reference_number?: string | null;
  received_by?: string | null;
  notes?: string | null;
  created_at: string;
}

export interface StudentFee {
  id: number;
  student_id: number;
  fee_structure_id: number;
  academic_year: string;
  amount_due: number;
  amount_paid: number;
  balance: number;
  status: string;
  due_date?: string | null;
  fee_name?: string;
  student_name?: string;
  admission_number?: string;
  payments?: FeePayment[];
  created_at: string;
  updated_at: string;
}

export interface Exam {
  id: number;
  name: string;
  exam_type: string;
  academic_year: string;
  term?: string | null;
  class_id: number;
  subject_id: number;
  start_date?: string | null;
  end_date?: string | null;
  exam_date?: string | null;
  max_marks?: number;
  pass_marks?: number;
  total_marks?: number;
  passing_marks?: number;
  start_time?: string | null;
  end_time?: string | null;
  status: string;
  result_submission_deadline?: string | null;
  instructions?: string | null;
  is_overdue?: boolean;
  deadline_status?: string | null;
  reopened_at?: string | null;
  reopened_by_id?: number | null;
  reopen_reason?: string | null;
  deadline_extensions?: Array<{
    id: number;
    previous_deadline?: string | null;
    new_deadline: string;
    reason?: string | null;
    created_at: string;
  }>;
  school_class?: SchoolClass | null;
  subject?: Subject | null;
  class_name?: string;
  class_code?: string;
  subject_name?: string;
  subject_code?: string;
  results_count?: number;
  enrolled_students_count?: number;
  completion_percentage?: number;
  created_at: string;
  updated_at: string;
}

export interface ExamResult {
  id: number;
  student_id: number;
  exam_id: number;
  subject_id: number;
  marks_obtained: number;
  total_marks: number;
  percentage: number;
  max_marks?: number;
  grade?: string | null;
  remarks?: string | null;
  recorded_by?: string | null;
  recorded_by_id?: number | null;
  student_name?: string;
  student_admission_number?: string;
  admission_number?: string;
  roll_number?: string | null;
  exam_name?: string;
  subject_name?: string;
  subject_code?: string;
  created_at: string;
  updated_at: string;
}

export interface ExamSummary {
  total_exams: number;
  upcoming_exams: number;
  ongoing_exams: number;
  completed_exams: number;
  published_results: number;
  total_students_assessed: number;
}

export interface ExamFilterOptions {
  academic_years: string[];
  exam_types: string[];
  statuses: string[];
  classes: { id: number; name: string; code: string; academic_year?: string }[];
  subjects: { id: number; name: string; code: string }[];
}

export interface ExamStudentSheetItem {
  student_id: number;
  admission_number: string;
  student_name: string;
  roll_number?: string | null;
  gender?: string | null;
  result_id?: number | null;
  marks_obtained?: number | null;
  grade?: string | null;
  remarks?: string | null;
  is_saved: boolean;
  updated_at?: string | null;
}

export interface ExamProfile {
  exam: Exam;
  enrolled_count: number;
  results_count: number;
  completion_percentage: number;
  average_score?: number | null;
  highest_score?: number | null;
  lowest_score?: number | null;
  pass_count: number;
  fail_count: number;
  pass_rate: number;
  student_sheet: ExamStudentSheetItem[];
}

export interface ReportCardSubject {
  subject_id: number;
  subject_name: string;
  subject_code: string;
  marks_obtained: number;
  max_marks: number;
  pass_marks: number;
  grade: string;
  percentage: number;
  remarks: string;
  is_passed: boolean;
}

export interface ReportCardStudent {
  id: number;
  admission_number: string;
  full_name: string;
  gender?: string | null;
  roll_number?: string | null;
  class_name: string;
  class_section?: string | null;
}

export interface ReportCardSummary {
  total_subjects: number;
  total_marks_obtained: number;
  total_possible_marks: number;
  overall_percentage: number;
  overall_grade: string;
  overall_remark: string;
  publication_status: string;
}

export interface ReportCardData {
  school_name: string;
  school_motto: string;
  academic_year: string;
  exam_name: string;
  exam_type: string;
  student: ReportCardStudent;
  subjects: ReportCardSubject[];
  summary: ReportCardSummary;
}

export interface ConflictCheckItem {
  conflict_type: string;
  exam_id: number;
  exam_name: string;
  subject_name: string;
  start_date: string;
  end_date: string;
  message: string;
}

export interface ConflictCheckResponse {
  has_conflict: boolean;
  conflicts_count: number;
  conflicts: ConflictCheckItem[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
