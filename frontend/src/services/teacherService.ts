import { apiClient } from './api';
import { Teacher, TeacherAssignment, TeacherSummary, TeacherFullProfile, TeacherFilterParams } from '../types/school';

export interface CreateTeacherPayload {
  teacher_number?: string;
  employee_id?: string;
  first_name: string;
  middle_name?: string | null;
  last_name: string;
  gender: string;
  date_of_birth?: string | null;
  phone?: string | null;
  email: string;
  address?: string | null;
  qualification?: string | null;
  hire_date?: string | null;
  status?: string;
  create_portal_account?: boolean;
  portal_username?: string;
  portal_password?: string;
}

export interface AssignTeacherPayload {
  class_id: number;
  subject_id: number;
  academic_year: string;
  section?: string | null;
}

export const teacherService = {
  async getSummary(): Promise<TeacherSummary> {
    const res = await apiClient.get<TeacherSummary>('/teachers/summary');
    return res.data;
  },

  async getTeachers(params?: TeacherFilterParams): Promise<Teacher[]> {
    const queryParams: Record<string, any> = {};
    if (params?.search) queryParams.query = params.search;
    if (params?.status) queryParams.status = params.status;
    if (params?.class_id) queryParams.class_id = params.class_id;
    if (params?.subject_id) queryParams.subject_id = params.subject_id;
    if (params?.has_portal !== undefined) queryParams.has_portal = params.has_portal;
    if (params?.academic_year) queryParams.academic_year = params.academic_year;
    if (params?.page && params?.page_size) {
      queryParams.skip = (params.page - 1) * params.page_size;
      queryParams.limit = params.page_size;
    }
    const res = await apiClient.get<Teacher[]>('/teachers', { params: queryParams });
    return res.data;
  },

  async getTeacherById(id: number): Promise<Teacher> {
    const res = await apiClient.get<Teacher>(`/teachers/${id}`);
    return res.data;
  },

  async getFullProfile(id: number): Promise<TeacherFullProfile> {
    const res = await apiClient.get<TeacherFullProfile>(`/teachers/${id}/full`);
    return res.data;
  },

  async createTeacher(payload: CreateTeacherPayload): Promise<Teacher> {
    // Ensure teacher_number is present
    const body = {
      ...payload,
      teacher_number: payload.teacher_number || payload.employee_id || `TCH-${Math.floor(1000 + Math.random() * 9000)}`,
    };
    const res = await apiClient.post<Teacher>('/teachers', body);
    return res.data;
  },

  async updateTeacher(id: number, payload: Partial<Teacher>): Promise<Teacher> {
    const res = await apiClient.put<Teacher>(`/teachers/${id}`, payload);
    return res.data;
  },

  async updateStatus(id: number, status: string, reason?: string): Promise<Teacher> {
    const res = await apiClient.patch<Teacher>(`/teachers/${id}/status`, { status, reason });
    return res.data;
  },

  async createPortalAccount(teacherId: number, payload: { username: string; password?: string }) {
    const res = await apiClient.post(`/teachers/${teacherId}/account`, payload);
    return res.data;
  },

  async assignTeacher(teacherId: number, payload: AssignTeacherPayload): Promise<TeacherAssignment> {
    const res = await apiClient.post<TeacherAssignment>(`/teachers/${teacherId}/assignments`, payload);
    return res.data;
  },

  async removeAssignment(assignmentId: number) {
    const res = await apiClient.delete(`/teachers/assignments/${assignmentId}`);
    return res.data;
  },
};
