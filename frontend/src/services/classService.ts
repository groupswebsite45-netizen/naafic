import { apiClient } from './api';
import {
  SchoolClass,
  ClassSummary,
  ClassFilterParams,
  ClassFullProfile
} from '../types/school';

export const classService = {
  async getSummary(): Promise<ClassSummary> {
    const res = await apiClient.get<ClassSummary>('/classes/summary');
    return res.data;
  },

  async getClasses(params?: ClassFilterParams): Promise<SchoolClass[]> {
    const queryParams: Record<string, any> = {};
    if (params?.query) queryParams.query = params.query;
    if (params?.academic_year) queryParams.academic_year = params.academic_year;
    if (params?.division) queryParams.division = params.division;
    if (params?.status) queryParams.status = params.status;
    if (params?.level) queryParams.level = params.level;
    if (params?.section) queryParams.section = params.section;
    if (params?.capacity_filter) queryParams.capacity_filter = params.capacity_filter;

    if (params?.page && params?.page_size) {
      queryParams.skip = (params.page - 1) * params.page_size;
      queryParams.limit = params.page_size;
    } else {
      if (params?.skip !== undefined) queryParams.skip = params.skip;
      if (params?.limit !== undefined) queryParams.limit = params.limit;
      else if (params?.page_size !== undefined) queryParams.limit = params.page_size;
    }

    const res = await apiClient.get<SchoolClass[]>('/classes', { params: queryParams });
    const data = res.data;
    return Array.isArray(data) ? data : (data as any)?.items || (data as any)?.data || [];
  },

  /**
   * CORE BUSINESS RULE ENFORCED:
   * Returns only active classes with >= 1 enrolled student.
   * Use this for ALL class selector dropdowns — admin students, teacher portal, results.
   * Never returns empty, test, or inactive classes.
   */
  async getActiveClassesWithStudents(params?: { academic_year?: string; division?: string }): Promise<SchoolClass[]> {
    const queryParams: Record<string, any> = {};
    if (params?.academic_year) queryParams.academic_year = params.academic_year;
    if (params?.division) queryParams.division = params.division;
    const res = await apiClient.get<SchoolClass[]>('/classes/active', { params: queryParams });
    const data = res.data;
    return Array.isArray(data) ? data : [];
  },



  async getClassById(id: number): Promise<SchoolClass> {
    const res = await apiClient.get<SchoolClass>(`/classes/${id}`);
    return res.data;
  },

  async getFullProfile(id: number): Promise<ClassFullProfile> {
    const res = await apiClient.get<ClassFullProfile>(`/classes/${id}/full`);
    return res.data;
  },

  async createClass(payload: Partial<SchoolClass>): Promise<SchoolClass> {
    const res = await apiClient.post<SchoolClass>('/classes', payload);
    return res.data;
  },

  async updateClass(id: number, payload: Partial<SchoolClass>): Promise<SchoolClass> {
    const res = await apiClient.put<SchoolClass>(`/classes/${id}`, payload);
    return res.data;
  },

  async updateStatus(id: number, status: string, reason?: string): Promise<SchoolClass> {
    const res = await apiClient.patch<SchoolClass>(`/classes/${id}/status`, { status, reason });
    return res.data;
  },

  async deleteClass(id: number): Promise<{ message: string }> {
    const res = await apiClient.delete<{ message: string }>(`/classes/${id}`);
    return res.data;
  },

  async enrollStudent(
    classId: number,
    studentId: number,
    academicYear: string,
    enrollmentDate?: string
  ): Promise<{ message: string; enrollment_id: number }> {
    const res = await apiClient.post<{ message: string; enrollment_id: number }>(`/classes/${classId}/students`, {
      student_id: studentId,
      academic_year: academicYear,
      enrollment_date: enrollmentDate,
    });
    return res.data;
  },

  async removeStudent(classId: number, studentId: number): Promise<{ message: string }> {
    const res = await apiClient.delete<{ message: string }>(`/classes/${classId}/students/${studentId}`);
    return res.data;
  },

  async assignTeacher(
    classId: number,
    payload: { teacher_id: number; subject_id: number; academic_year: string }
  ): Promise<{ message: string; assignment_id: number }> {
    const res = await apiClient.post<{ message: string; assignment_id: number }>(`/classes/${classId}/teachers`, payload);
    return res.data;
  },

  async removeTeacher(classId: number, assignmentId: number): Promise<{ message: string }> {
    const res = await apiClient.delete<{ message: string }>(`/classes/${classId}/teachers/${assignmentId}`);
    return res.data;
  },
};
