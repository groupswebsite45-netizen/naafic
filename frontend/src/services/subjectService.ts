import { apiClient } from './api';
import {
  Subject,
  SubjectSummary,
  SubjectFilterParams,
  SubjectFullProfile
} from '../types/school';

export const subjectService = {
  async getSummary(): Promise<SubjectSummary> {
    const res = await apiClient.get<SubjectSummary>('/subjects/summary');
    return res.data;
  },

  async getDepartments(): Promise<string[]> {
    const res = await apiClient.get<string[]>('/subjects/departments');
    return res.data;
  },

  async getSubjects(params?: SubjectFilterParams): Promise<Subject[]> {
    const queryParams: Record<string, any> = {};
    if (params?.search || params?.query) queryParams.query = params.search || params.query;
    if (params?.division) queryParams.division = params.division;
    if (params?.level) queryParams.level = params.level;
    if (params?.class_id) queryParams.class_id = params.class_id;
    if (params?.department) queryParams.department = params.department;
    if (params?.status) queryParams.status = params.status;
    if (params?.assigned_filter) queryParams.assigned_filter = params.assigned_filter;
    if (params?.academic_year) queryParams.academic_year = params.academic_year;

    if (params?.page && params?.page_size) {
      queryParams.skip = (params.page - 1) * params.page_size;
      queryParams.limit = params.page_size;
    } else if (params?.skip !== undefined) {
      queryParams.skip = params.skip;
      if (params.limit !== undefined) queryParams.limit = params.limit;
    }

    const res = await apiClient.get<Subject[]>('/subjects', { params: queryParams });
    return res.data;
  },

  async getSubjectById(id: number): Promise<Subject> {
    const res = await apiClient.get<Subject>(`/subjects/${id}`);
    return res.data;
  },

  async getFullProfile(id: number): Promise<SubjectFullProfile> {
    const res = await apiClient.get<SubjectFullProfile>(`/subjects/${id}/full`);
    return res.data;
  },

  async createSubject(payload: Partial<Subject>): Promise<Subject> {
    const res = await apiClient.post<Subject>('/subjects', payload);
    return res.data;
  },

  async updateSubject(id: number, payload: Partial<Subject>): Promise<Subject> {
    const res = await apiClient.put<Subject>(`/subjects/${id}`, payload);
    return res.data;
  },

  async updateStatus(id: number, status: string, reason?: string): Promise<Subject> {
    const res = await apiClient.patch<Subject>(`/subjects/${id}/status`, { status, reason });
    return res.data;
  },

  async deleteSubject(id: number): Promise<{ message: string }> {
    const res = await apiClient.delete<{ message: string }>(`/subjects/${id}`);
    return res.data;
  },

  async assignClass(
    subjectId: number,
    payload: { class_id: number; academic_year: string; teacher_id?: number | null }
  ): Promise<{ message: string; assignment_id: number }> {
    const res = await apiClient.post<{ message: string; assignment_id: number }>(`/subjects/${subjectId}/classes`, payload);
    return res.data;
  },

  async removeClass(subjectId: number, assignmentId: number): Promise<{ message: string }> {
    const res = await apiClient.delete<{ message: string }>(`/subjects/${subjectId}/classes/${assignmentId}`);
    return res.data;
  },

  async assignTeacher(
    subjectId: number,
    payload: { teacher_id: number; class_id: number; academic_year: string }
  ): Promise<{ message: string; assignment_id: number }> {
    const res = await apiClient.post<{ message: string; assignment_id: number }>(`/subjects/${subjectId}/teachers`, payload);
    return res.data;
  },

  async removeTeacher(subjectId: number, assignmentId: number): Promise<{ message: string }> {
    const res = await apiClient.delete<{ message: string }>(`/subjects/${subjectId}/teachers/${assignmentId}`);
    return res.data;
  },
};
