import { apiClient } from './api';

export interface FormMasterAssignment {
  id: number;
  teacher_id: number;
  teacher_name: string;
  teacher_number: string;
  teacher_email?: string;
  teacher_phone?: string;
  class_id: number;
  class_name: string;
  class_code: string;
  division?: string;
  level?: string;
  section?: string;
  academic_year: string;
  status: string;
  notes?: string;
  appointed_by_name?: string;
  appointed_at: string;
  revoked_by_name?: string;
  revoked_at?: string;
  created_at?: string;
}

export interface ClassFormMasterItem {
  class_id: number;
  class_name: string;
  class_code: string;
  division: string;
  level: string;
  section?: string;
  academic_year: string;
  capacity: number;
  student_count: number;
  assignment_id?: number;
  form_master_id?: number;
  form_master_name?: string;
  form_master_number?: string;
  form_master_email?: string;
  form_master_phone?: string;
  status: 'ASSIGNED' | 'UNASSIGNED';
  appointed_at?: string;
  notes?: string;
}

export interface AvailableTeacherItem {
  teacher_id: number;
  teacher_number: string;
  full_name: string;
  email: string;
  phone?: string;
  gender?: string;
  active_form_classes_count: number;
  can_assign: boolean;
  assigned_classes: string[];
}

export interface FormMasterAdminOverview {
  total_classes: number;
  assigned_classes_count: number;
  unassigned_classes_count: number;
  total_form_masters: number;
  academic_year: string;
}

export interface FormMasterClassSummary {
  id: number;
  name: string;
  code: string;
  division: string;
  level: string;
  section?: string;
  academic_year: string;
  capacity: number;
  student_count: number;
  assignment_id: number;
  appointed_at: string;
}

export interface FormMasterStudentItem {
  student_id: number;
  admission_number: string;
  first_name: string;
  last_name: string;
  full_name: string;
  gender: string;
  phone?: string;
  guardian_name?: string;
  guardian_phone?: string;
  guardian_email?: string;
  guardian_relationship?: string;
  enrollment_status: string;
  total_exams_taken: number;
  average_marks?: number;
  failing_subjects_count: number;
  has_poor_academic_performance: boolean;
  total_attendance_records: number;
  present_count: number;
  absent_count: number;
  late_count: number;
  attendance_rate: number;
  has_frequent_absences: boolean;
  fee_total_invoiced: number;
  fee_total_paid: number;
  fee_balance: number;
  fee_status: string;
  has_overdue_fees: boolean;
}

export interface FormMasterDashboardData {
  assigned_classes: FormMasterClassSummary[];
  selected_class: FormMasterClassSummary;
  total_students: number;
  attendance_rate: number;
  students_with_poor_performance_count: number;
  students_with_frequent_absences_count: number;
  students_with_outstanding_fees_count: number;
  total_outstanding_fees: number;
  poor_performance_students: any[];
  frequent_absences_students: any[];
  outstanding_fees_students: any[];
  recent_activity: any[];
  alerts: any[];
}

export interface FormMasterResultsData {
  class_id: number;
  class_name: string;
  class_code: string;
  academic_year: string;
  available_exam_types: string[];
  available_exams: any[];
  subjects: any[];
  students: any[];
  class_average: number;
  total_students: number;
  pass_rate: number;
  poor_performers_count: number;
  top_performers_count: number;
}

export interface FormMasterAttendanceData {
  class_id: number;
  class_name: string;
  class_code: string;
  academic_year: string;
  overall_stats: {
    total_records: number;
    present_count: number;
    absent_count: number;
    late_count: number;
    excused_count: number;
    attendance_rate: number;
  };
  students: any[];
  recent_records: any[];
  monthly_trend: any[];
}

export interface FormMasterFeesData {
  class_id: number;
  class_name: string;
  class_code: string;
  academic_year: string;
  summary: {
    total_invoiced: number;
    total_paid: number;
    total_outstanding: number;
    paid_students_count: number;
    partially_paid_students_count: number;
    unpaid_students_count: number;
    overdue_students_count: number;
    total_students: number;
  };
  students: any[];
}

export const formMasterService = {
  // =========================================================================
  // ADMIN API
  // =========================================================================
  async getOverview(academicYear?: string): Promise<FormMasterAdminOverview> {
    const params = academicYear ? { academic_year: academicYear } : {};
    const res = await apiClient.get<FormMasterAdminOverview>('/form-masters/overview', { params });
    return res.data;
  },

  async listClasses(params?: {
    academic_year?: string;
    division?: string;
    status?: string;
  }): Promise<ClassFormMasterItem[]> {
    const res = await apiClient.get<ClassFormMasterItem[]>('/form-masters/classes', { params });
    return res.data;
  },

  async listAvailableTeachers(academicYear?: string): Promise<AvailableTeacherItem[]> {
    const params = academicYear ? { academic_year: academicYear } : {};
    const res = await apiClient.get<AvailableTeacherItem[]>('/form-masters/available-teachers', { params });
    return res.data;
  },

  async appoint(payload: {
    teacher_id: number;
    class_ids: number[];
    academic_year: string;
    notes?: string;
  }): Promise<FormMasterAssignment[]> {
    const res = await apiClient.post<FormMasterAssignment[]>('/form-masters/appoint', payload);
    return res.data;
  },

  async replace(assignmentId: number, payload: {
    new_teacher_id: number;
    notes?: string;
  }): Promise<FormMasterAssignment> {
    const res = await apiClient.post<FormMasterAssignment>(`/form-masters/${assignmentId}/replace`, payload);
    return res.data;
  },

  async revoke(assignmentId: number, payload?: {
    notes?: string;
  }): Promise<FormMasterAssignment> {
    const res = await apiClient.post<FormMasterAssignment>(`/form-masters/${assignmentId}/revoke`, payload || {});
    return res.data;
  },

  // =========================================================================
  // TEACHER / FORM MASTER PORTAL API
  // =========================================================================
  async checkStatus(): Promise<{
    is_form_master: boolean;
    classes_count: number;
    classes: Array<{ class_id: number; class_name: string; academic_year: string }>;
  }> {
    const res = await apiClient.get('/form-master/check');
    return res.data;
  },

  async getMyClasses(academicYear?: string): Promise<FormMasterClassSummary[]> {
    const params = academicYear ? { academic_year: academicYear } : {};
    const res = await apiClient.get<FormMasterClassSummary[]>('/form-master/my-classes', { params });
    return res.data;
  },

  async getDashboard(classId: number, academicYear?: string): Promise<FormMasterDashboardData> {
    const params = academicYear ? { academic_year: academicYear } : {};
    const res = await apiClient.get<FormMasterDashboardData>(`/form-master/classes/${classId}/dashboard`, { params });
    return res.data;
  },

  async getStudents(classId: number, academicYear?: string): Promise<FormMasterStudentItem[]> {
    const params = academicYear ? { academic_year: academicYear } : {};
    const res = await apiClient.get<FormMasterStudentItem[]>(`/form-master/classes/${classId}/students`, { params });
    return res.data;
  },

  async getResults(classId: number, params?: {
    academic_year?: string;
    exam_type?: string;
    exam_id?: number;
    subject_id?: number;
  }): Promise<FormMasterResultsData> {
    const res = await apiClient.get<FormMasterResultsData>(`/form-master/classes/${classId}/results`, { params });
    return res.data;
  },

  async getAttendance(classId: number, params?: {
    academic_year?: string;
    start_date?: string;
    end_date?: string;
    subject_id?: number;
  }): Promise<FormMasterAttendanceData> {
    const res = await apiClient.get<FormMasterAttendanceData>(`/form-master/classes/${classId}/attendance`, { params });
    return res.data;
  },

  async getFees(classId: number, academicYear?: string): Promise<FormMasterFeesData> {
    const params = academicYear ? { academic_year: academicYear } : {};
    const res = await apiClient.get<FormMasterFeesData>(`/form-master/classes/${classId}/fees`, { params });
    return res.data;
  },
};
