export type WorkflowStatus =
  | 'NOT_STARTED'
  | 'DRAFT'
  | 'PARTIAL'
  | 'READY_TO_SUBMIT'
  | 'SUBMITTED'
  | 'UNDER_REVIEW'
  | 'RETURNED'
  | 'APPROVED'
  | 'RELEASED'
  | 'COMPLETE'
  | 'PENDING'
  | 'REVIEW';

export type AttendanceStatus = 'PRESENT' | 'ABSENT' | 'EXCUSED';

export interface ResultFilterOptions {
  academic_years: string[];
  selected_academic_year: string;
  exam_names: string[];
  teachers?: { id: number; name: string; email: string }[];
  classes?: { id: number; name: string; code: string }[];
  subjects?: { id: number; name: string; code: string }[];
}

export interface ResultOverviewStats {
  academic_year: string;
  exam_name: string;
  classes_count: number;
  submissions_completed: number;
  submissions_total: number;
  pending_count: number;
  approved_count: number;
  released_count: number;
}

export interface ClassResultSummaryItem {
  class_id: number;
  class_name: string;
  class_code: string;
  academic_year: string;
  students_count: number;
  subjects_count: number;
  complete_subjects_count?: number;
  pending_subjects_count?: number;
  released_subjects_count?: number;
  submitted_subjects_count?: number;
  progress_percent?: number;
  expected_results: number;
  submitted_results: number;
  pending_results: number;
  approved_results: number;
  released_results: number;
  viewed_results: number;
  status: string;
}

export interface ClassSubjectMatrixItem {
  subject_id: number;
  subject_name: string;
  subject_code: string;
  teacher_id: number | null;
  teacher_name: string;
  teacher_email?: string;
  exam_id?: number;
  submission_id?: number;
  status: WorkflowStatus | string;
  release_status: 'RELEASED' | 'NOT RELEASED' | string;
  is_complete: boolean;
  expected_students: number;
  attended_students: number;
  marks_entered: number;
  marks_submitted: number;
  marks_approved: number;
  marks_released: number;
  pending_students: number;
  absent_students: number;
  submitted_at?: string;
  approved_at?: string;
  return_reason?: string;
}

export interface StudentSubjectScoreItem {
  subject_id: number;
  subject_name: string;
  subject_code: string;
  attendance_status: AttendanceStatus;
  marks_obtained?: number | null;
  max_marks: number;
  pass_marks: number;
  grade?: string;
  remarks?: string;
  status: string;
}

export interface ClassStudentMatrixRow {
  student_id: number;
  admission_number: string;
  student_name: string;
  roll_number?: string;
  gender?: string;
  scores: Record<string, StudentSubjectScoreItem>;
  total_marks?: number | null;
  average_marks?: number | null;
  passed_all: boolean;
}

export interface ClassResultDashboardResponse {
  class_id: number;
  class_name: string;
  class_code?: string;
  academic_year: string;
  exam_name: string;
  students_count: number;
  subjects_count: number;
  complete_subjects_count: number;
  pending_subjects_count: number;
  released_subjects_count: number;
  not_released_subjects_count: number;
  expected_results: number;
  submitted_results: number;
  pending_results: number;
  approved_results: number;
  released_results: number;
  viewed_results: number;
  status: string;
  subjects_matrix: ClassSubjectMatrixItem[];
  student_matrix: ClassStudentMatrixRow[];
  can_release_full: boolean;
  can_release_partial: boolean;
  release_batch_code?: string;
  released_at?: string;
}

export interface TeacherSubmissionItem {
  id: number;
  teacher_id: number;
  teacher_name: string;
  teacher_number?: string;
  subject_id: number;
  subject_name: string;
  subject_code?: string;
  class_id: number;
  class_name: string;
  class_section?: string;
  exam_id: number;
  exam_name: string;
  academic_year: string;
  expected_students: number;
  completed_students: number;
  pending_students: number;
  absent_students?: number;
  present_students?: number;
  complaints_count?: number;
  status: WorkflowStatus | string;
  submitted_at?: string;
  reviewed_at?: string;
  approved_at?: string;
  returned_at?: string;
  return_reason?: string;
  submission_deadline?: string;
  is_overdue?: boolean;
  deadline_status?: string;
  completion_percentage?: number;
  exam_type?: string;
  exam_status?: string;
  start_time?: string;
  end_time?: string;
  instructions?: string;
  revisions?: any[];
}

export interface TeacherAccountabilitySummary {
  teacher_id: number;
  teacher_name: string;
  teacher_number?: string;
  total_assigned: number;
  submitted: number;
  partial: number;
  pending: number;
  approved: number;
  returned: number;
  released: number;
}

export interface StudentMarkItem {
  student_id: number;
  admission_number: string;
  student_name: string;
  roll_number?: string;
  gender?: string;
  attendance_status: AttendanceStatus;
  absence_reason?: string | null;
  complaint?: string | null;
  marks_obtained?: number | null;
  max_marks: number;
  pass_marks: number;
  grade?: string;
  remarks?: string;
  status: string;
  paper_file_path?: string;
  paper_original_name?: string;
}

export interface SubmissionReviewDetail {
  id: number;
  exam_id: number;
  exam_name: string;
  exam_type?: string;
  academic_year: string;
  class_id: number;
  class_name: string;
  class_section?: string;
  subject_id: number;
  subject_name: string;
  teacher_id: number;
  teacher_name: string;
  status: WorkflowStatus | string;
  expected_students: number;
  completed_students: number;
  pending_students: number;
  absent_students?: number;
  present_students?: number;
  sat_exam_students?: number;
  missing_marks_students?: number;
  recorded_absence_reasons_count?: number;
  complaints_count?: number;
  pass_marks?: number;
  max_marks?: number;
  is_complete?: boolean;
  submitted_at?: string;
  returned_at?: string;
  return_reason?: string;
  revisions?: any[];
  students: StudentMarkItem[];
}

export interface StudentReceiptStatusItem {
  student_id: number;
  admission_number: string;
  student_name: string;
  class_name: string;
  status: 'NOT_RELEASED' | 'RELEASED' | 'VIEWED';
  release_batch_code?: string;
  released_at?: string;
  first_viewed_at?: string;
  last_viewed_at?: string;
  view_count: number;
}

export interface ClassReceiptSummary {
  class_id: number;
  class_name: string;
  exam_name: string;
  academic_year: string;
  total_students: number;
  released_students: number;
  viewed_students: number;
  not_viewed_students: number;
  receipts: StudentReceiptStatusItem[];
}

export interface TeacherExamAssignmentItem {
  exam_id: number;
  exam_name: string;
  exam_type: string;
  exam_status?: string;
  academic_year: string;
  class_id: number;
  class_name: string;
  class_code: string;
  class_section?: string;
  subject_id: number;
  subject_name: string;
  subject_code: string;
  max_marks: number;
  pass_marks: number;
  submission_id?: number;
  status: WorkflowStatus | string;
  expected_students: number;
  completed_students: number;
  pending_students: number;
  absent_students?: number;
  complaints_count?: number;
  submitted_at?: string;
  returned_at?: string;
  return_reason?: string;
  start_date?: string;
  end_date?: string;
  start_time?: string;
  end_time?: string;
  result_submission_deadline?: string;
  deadline_status?: string;
  is_overdue?: boolean;
  remaining_time_human?: string;
  instructions?: string;
  revisions?: any[];
}

export interface DashboardStatistics {
  academic_year: string;
  exam_name: string;
  division: string;
  total_classes_with_students: number;
  total_eligible_students: number;
  total_submitted_sheets: number;
  completed_subjects: number;
  pending_teacher_submissions: number;
  students_sat_exam: number;
  absent_students: number;
  awaiting_admin_review: number;
  approved_results: number;
  published_results: number;
}

export interface ClassResultSheetSubject {
  id: number;
  name: string;
  code: string;
  teacher_id?: number | null;
  teacher_name?: string;
  max_marks: number;
  pass_marks: number;
}

export interface ClassResultSheetStudentScore {
  subject_id: number;
  subject_name: string;
  subject_code: string;
  marks_obtained?: number | null;
  max_marks: number;
  pass_marks: number;
  grade?: string;
  attendance_status: AttendanceStatus;
  absence_reason?: string;
  complaint?: string;
  is_absent: boolean;
  remarks?: string;
  status: string;
}

export interface ClassResultSheetStudent {
  student_id: number;
  admission_number: string;
  student_name: string;
  gender: string;
  roll_number?: string;
  subject_marks: Record<string, ClassResultSheetStudentScore>;
  total_obtained?: number | null;
  total_max: number;
  percentage?: number | null;
  grade?: string;
  pass_status: 'PASS' | 'FAIL';
  completed_subjects: number;
  absent_subjects: number;
  is_absent_all: boolean;
  rank: number;
  remarks?: string;
}

export interface ClassResultSheetSummary {
  registered_students: number;
  sat_exam_students: number;
  absent_students: number;
  passed_students: number;
  failed_students: number;
  pass_percentage: number;
  class_average_percentage: number;
  highest_total: number;
  lowest_total: number;
  subject_performance: {
    subject_id: number;
    subject_name: string;
    subject_code: string;
    teacher_name: string;
    registered: number;
    sat: number;
    absent: number;
    missing: number;
    average_marks: number;
    highest_marks: number;
    lowest_marks: number;
    pass_count: number;
    fail_count: number;
    pass_rate: number;
    grade_distribution: Record<string, number>;
  }[];
}

export interface ClassResultSheetResponse {
  school: {
    name: string;
    motto: string;
    address: string;
    phone: string;
    email: string;
    logo_path?: string;
  };
  class_info: {
    id: number;
    name: string;
    code: string;
    division: string;
    level: string;
    section?: string;
    academic_year: string;
  };
  exam_info: {
    name: string;
    exam_type?: string;
    academic_year: string;
    start_date?: string;
    end_date?: string;
  };
  subjects: ClassResultSheetSubject[];
  students: ClassResultSheetStudent[];
  class_summary: ClassResultSheetSummary;
}

export interface ClassRankingItem {
  position: number;
  student_id: number;
  admission_number: string;
  student_name: string;
  gender: string;
  roll_number?: string;
  class_id: number;
  class_name: string;
  division: string;
  completed_subjects: number;
  absent_subjects: number;
  total_marks?: number | null;
  max_possible_marks?: number | null;
  percentage?: number | null;
  grade?: string;
  pass_fail: 'PASS' | 'FAIL';
  is_complete: boolean;
}

export interface ClassRankingResponse {
  school: {
    name: string;
    motto: string;
  };
  class_info: {
    id?: number | null;
    name: string;
    division: string;
    academic_year: string;
  };
  exam_info: {
    name: string;
    exam_type?: string;
    academic_year: string;
  };
  rankings: ClassRankingItem[];
}

export interface StudentResultReportSubject {
  subject_id?: number | null;
  subject_name: string;
  subject_code: string;
  teacher_name: string;
  marks_obtained?: number | null;
  max_marks: number;
  pass_marks: number;
  percentage?: number | null;
  grade?: string;
  attendance_status: string;
  absence_reason?: string;
  pass_status: string;
  remarks?: string;
  status: string;
}

export interface StudentResultReportResponse {
  school: {
    name: string;
    motto: string;
    address: string;
    phone: string;
    email: string;
    logo_path?: string;
  };
  student: {
    id: number;
    student_name: string;
    admission_number: string;
    gender: string;
    roll_number?: string;
  };
  class_info: {
    id?: number | null;
    name: string;
    division: string;
    academic_year: string;
  };
  exam_info: {
    name: string;
    academic_year: string;
  };
  subjects: StudentResultReportSubject[];
  overall: {
    total_obtained: number;
    total_max: number;
    overall_percentage: number;
    overall_grade: string;
    pass_status: string;
    rank_in_class: string | number;
    class_size: number;
    absent_subjects_count: number;
    teacher_remarks?: string;
  };
}

export interface SubjectPerformanceItem {
  exam_id: number;
  class_id: number;
  class_name: string;
  division: string;
  subject_id: number;
  subject_name: string;
  subject_code: string;
  teacher_id?: number | null;
  teacher_name: string;
  max_marks: number;
  pass_marks: number;
  total_registered: number;
  sat_exam: number;
  absent_count: number;
  missing_marks_count: number;
  highest_marks: number;
  lowest_marks: number;
  average_marks: number;
  pass_count: number;
  fail_count: number;
  pass_rate: number;
  grade_distribution: Record<string, number>;
  submission_status: string;
}

export interface AbsentStudentItem {
  result_id: number;
  student_id: number;
  admission_number: string;
  student_name: string;
  gender: string;
  class_id?: number | null;
  class_name: string;
  division: string;
  section?: string;
  subject_id?: number | null;
  subject_name: string;
  subject_code: string;
  exam_id?: number | null;
  exam_name: string;
  attendance_status: string;
  absence_reason?: string;
  complaint?: string;
  teacher_name: string;
}

