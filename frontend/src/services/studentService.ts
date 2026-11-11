import { apiClient } from './api';
import {
  Student,
  StudentEnrollment,
  StudentSummary,
  StudentFullProfile,
  StudentFilterParams,
} from '../types/school';

export interface CreateStudentPayload {
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
  status?: string;
  initial_class_id?: number | null;
  academic_year?: string | null;
  create_portal_account?: boolean;
  portal_username?: string | null;
  portal_password?: string | null;
}

export interface EnrollStudentPayload {
  class_id: number;
  academic_year: string;
  roll_number?: string | null;
  start_date?: string | null;
}

export const studentService = {
  async getSummary(academicYear?: string): Promise<StudentSummary> {
    const res = await apiClient.get<StudentSummary>('/students/summary', {
      params: academicYear ? { academic_year: academicYear } : undefined,
    });
    return res.data;
  },

  async getStudents(params?: StudentFilterParams): Promise<Student[]> {
    const queryParams: Record<string, any> = {};
    if (params?.search) queryParams.query = params.search;
    if (params?.class_id) queryParams.class_id = params.class_id;
    if (params?.academic_year) queryParams.academic_year = params.academic_year;
    if (params?.gender) queryParams.gender = params.gender;
    if (params?.status) queryParams.status = params.status;
    if (params?.has_portal !== undefined) queryParams.has_portal = params.has_portal;
    if (params?.page && params?.page_size) {
      queryParams.skip = (params.page - 1) * params.page_size;
      queryParams.limit = params.page_size;
    } else {
      if (params?.skip !== undefined) queryParams.skip = params.skip;
      if (params?.limit !== undefined) queryParams.limit = params.limit;
      else if (params?.page_size !== undefined) queryParams.limit = params.page_size;
    }
    const res = await apiClient.get<Student[]>('/students', { params: queryParams });
    const data = res.data;
    const items: any = Array.isArray(data) ? data : (data as any)?.items || (data as any)?.data || [];
    const totalHeader = res.headers ? (res.headers['x-total-count'] || res.headers['X-Total-Count']) : undefined;
    if (totalHeader !== undefined) {
      const parsed = parseInt(String(totalHeader), 10);
      if (!isNaN(parsed)) {
        items.total = parsed;
      }
    }
    return items;
  },

  async getStudentById(id: number): Promise<Student> {
    const res = await apiClient.get<Student>(`/students/${id}`);
    return res.data;
  },

  async getFullProfile(id: number): Promise<StudentFullProfile> {
    const res = await apiClient.get<StudentFullProfile>(`/students/${id}/profile`);
    return res.data;
  },

  async createStudent(payload: CreateStudentPayload): Promise<Student> {
    const res = await apiClient.post<Student>('/students', payload);
    return res.data;
  },

  async updateStudent(id: number, payload: Partial<CreateStudentPayload>): Promise<Student> {
    const res = await apiClient.put<Student>(`/students/${id}`, payload);
    return res.data;
  },

  async uploadPhoto(id: number, file: File): Promise<Student> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post<Student>(`/students/${id}/photo`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },

  async deletePhoto(id: number): Promise<Student> {
    const res = await apiClient.delete<Student>(`/students/${id}/photo`);
    return res.data;
  },

  getPhotoUrl(id?: number | null, photoPath?: string | null): string | null {
    if (!id || !photoPath) return null;
    const token = typeof window !== 'undefined' ? localStorage.getItem('sms_access_token') : null;
    let extraParams = '';
    if (typeof window !== 'undefined') {
      const activeInstStr = localStorage.getItem('sms_active_institution');
      if (activeInstStr) {
        try {
          const inst = JSON.parse(activeInstStr);
          if (inst?.id) {
            extraParams += `&institution_id=${encodeURIComponent(inst.id)}`;
          }
        } catch (e) {
          // ignore
        }
      }
    }
    const tokenQuery = token ? `?token=${encodeURIComponent(token)}${extraParams}` : (extraParams ? `?${extraParams.slice(1)}` : '');
    return `/api/v1/students/${id}/photo${tokenQuery}`;
  },

  async updateStatus(id: number, status: string, reason?: string): Promise<Student> {
    const res = await apiClient.patch<Student>(`/students/${id}/status`, { status, reason });
    return res.data;
  },

  async suggestPortalUsername(id: number): Promise<{ suggested_username: string; student_name: string; admission_number: string }> {
    const res = await apiClient.get<{ suggested_username: string; student_name: string; admission_number: string }>(`/students/${id}/account/suggest-username`);
    return res.data;
  },

  async createPortalAccount(id: number, payload: { username: string; password: string }): Promise<{ message: string; username: string }> {
    const res = await apiClient.post<{ message: string; username: string }>(`/students/${id}/account`, payload);
    return res.data;
  },

  async resetPortalPassword(id: number, password: string): Promise<{ message: string; username: string }> {
    const res = await apiClient.post<{ message: string; username: string }>(`/students/${id}/account/reset-password`, { password });
    return res.data;
  },

  async togglePortalAccess(id: number, isActive: boolean): Promise<{ message: string; is_active: boolean; portal_status: string }> {
    const res = await apiClient.patch<{ message: string; is_active: boolean; portal_status: string }>(`/students/${id}/account/status`, { is_active: isActive });
    return res.data;
  },

  async changePortalUsername(id: number, username: string): Promise<{ message: string; old_username: string; new_username: string }> {
    const res = await apiClient.patch<{ message: string; old_username: string; new_username: string }>(`/students/${id}/account/username`, { username });
    return res.data;
  },

  async batchEnablePortals(payload?: { academic_year?: string; class_id?: number; default_password?: string; student_ids?: number[] }): Promise<any> {
    const res = await apiClient.post('/students/portal/batch-enable', payload || {});
    return res.data;
  },

  async togglePortalQuick(studentId: number, isActive?: boolean): Promise<{ student_id: number; has_portal_access: boolean; portal_username: string; portal_is_active: boolean; message: string }> {
    const res = await apiClient.post(`/students/${studentId}/portal/toggle`, { is_active: isActive });
    return res.data;
  },

  async loginAsStudent(studentId: number): Promise<{ access_token: string; portal_url: string; student_name: string; username: string }> {
    const res = await apiClient.post(`/students/${studentId}/portal-login`);
    return res.data;
  },

  async enrollStudent(studentId: number, payload: EnrollStudentPayload): Promise<StudentEnrollment> {
    const res = await apiClient.post<StudentEnrollment>(`/students/${studentId}/enroll`, payload);
    return res.data;
  },

  async downloadImportTemplate(): Promise<Blob> {
    const res = await apiClient.get('/admin/students/import/template', {
      responseType: 'blob',
    });
    return res.data;
  },

  async previewImportExcel(file: File, classId: number, academicYear: string): Promise<StudentImportPreviewResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('class_id', classId.toString());
    formData.append('academic_year', academicYear);
    formData.append('academic_year_id', academicYear);

    const res = await apiClient.post<StudentImportPreviewResponse>('/admin/students/import/preview', formData, {
      headers: {
        'Content-Type': undefined,
      },
    });
    return res.data;
  },

  async executeImport(payload: StudentImportExecuteRequest): Promise<StudentImportSummaryResponse> {
    const res = await apiClient.post<StudentImportSummaryResponse>('/admin/students/import/execute', payload);
    return res.data;
  },

  async getImportHistory(limit = 50): Promise<StudentImportLogResponse[]> {
    const res = await apiClient.get<StudentImportLogResponse[]>('/admin/students/import/history', {
      params: { limit },
    });
    return res.data;
  },
};

export interface StudentImportRowPreview {
  row_number: number;
  admission_number?: string | null;
  student_name?: string | null;
  full_name?: string | null;
  first_name?: string | null;
  middle_name?: string | null;
  last_name?: string | null;
  gender?: string | null;
  date_of_birth?: string | null;
  guardian_name?: string | null;
  guardian_phone?: string | null;
  guardian_email?: string | null;
  guardian_relationship?: string | null;
  phone?: string | null;
  address?: string | null;
  status: 'VALID' | 'ERROR' | 'WARNING' | 'ALREADY_EXISTS';
  error_reason?: string | null;
  is_existing_student: boolean;
  is_already_enrolled: boolean;
  existing_student_id?: number | null;
  existing_class_name?: string | null;
}

export interface StudentImportPreviewResponse {
  success: boolean;
  total_rows: number;
  valid_rows: number;
  warning_rows: number;
  error_rows: number;
  already_exists_rows: number;
  class_id: number;
  class_name: string;
  academic_year: string;
  destination?: {
    class_id: number;
    class_name: string;
    academic_year: string;
  };
  summary?: {
    total_rows: number;
    valid_rows: number;
    invalid_rows: number;
    existing_rows: number;
  };
  rows: StudentImportRowPreview[];
}

export interface StudentImportExecuteRequest {
  class_id: number;
  academic_year: string;
  file_name?: string;
  rows: StudentImportRowPreview[];
  enroll_existing_students?: boolean;
}

export interface StudentImportSummaryResponse {
  success: boolean;
  total_rows: number;
  imported_count: number;
  already_enrolled_count: number;
  skipped_count: number;
  failed_count: number;
  class_id: number;
  class_name: string;
  academic_year: string;
  message: string;
  errors: string[];
}

export interface StudentImportLogResponse {
  id: number;
  file_name: string;
  class_id?: number | null;
  class_name?: string | null;
  academic_year: string;
  total_rows: number;
  imported_count: number;
  already_enrolled_count: number;
  skipped_count: number;
  failed_count: number;
  admin_name?: string | null;
  created_at?: string | null;
}

