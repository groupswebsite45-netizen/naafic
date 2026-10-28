import { apiClient } from './api';
import {
  TeacherDashboardData,
  TeacherPortalProfile,
  TeacherAssignedStudent,
  TeacherClassDetailResponse,
} from '../types/portal';
import { Subject, TimetableEntry, Exam, ExamResult, TeacherAssignment } from '../types/school';
import { BulkResultEntry } from './examService';

export const teacherPortalService = {
  async getMe(): Promise<{ user_id: number; teacher_id: number; teacher_number: string; name: string; email: string; role: string; status: string }> {
    const res = await apiClient.get('/teacher/me');
    return res.data;
  },

  async getDashboard(): Promise<TeacherDashboardData> {
    const res = await apiClient.get<TeacherDashboardData>('/teacher-portal/dashboard');
    return res.data;
  },

  async getProfile(): Promise<TeacherPortalProfile> {
    const res = await apiClient.get<TeacherPortalProfile>('/teacher-portal/profile');
    return res.data;
  },

  async getMyClasses(): Promise<TeacherAssignment[]> {
    const res = await apiClient.get<TeacherAssignment[]>('/teacher-portal/classes');
    return res.data;
  },

  async getClassDetail(classId: number): Promise<TeacherClassDetailResponse> {
    const res = await apiClient.get<TeacherClassDetailResponse>(`/teacher-portal/classes/${classId}/detail`);
    return res.data;
  },

  async getMySubjects(): Promise<Subject[]> {
    const res = await apiClient.get<Subject[]>('/teacher-portal/subjects');
    return res.data;
  },

  async getMyTimetable(): Promise<TimetableEntry[]> {
    const res = await apiClient.get<TimetableEntry[]>('/teacher-portal/timetable');
    return res.data;
  },

  async getMyStudents(classId?: number, query?: string): Promise<TeacherAssignedStudent[]> {
    const res = await apiClient.get<TeacherAssignedStudent[]>('/teacher-portal/students', {
      params: {
        class_id: classId || undefined,
        query: query ? query.trim() : undefined,
      },
    });
    return res.data;
  },

  async getMyExams(): Promise<Exam[]> {
    const res = await apiClient.get<Exam[]>('/teacher-portal/exams');
    return res.data;
  },

  /**
   * Get available options for exam creation.
   * Returns ONLY academic years, subjects, and classes from teacher's active assignments.
   * Subject → classes is cascaded: if subject_id is provided, only returns classes
   * where the teacher teaches that specific subject.
   */
  async getExamOptions(params?: { academic_year?: string; subject_id?: number }): Promise<{
    academic_years: string[];
    subjects: Array<{ id: number; name: string; code: string; division: string }>;
    classes: Array<{ id: number; name: string; code: string; division: string; level: string; section: string; academic_year: string; student_count: number }>;
    teacher_id: number;
    teacher_name: string;
  }> {
    const queryParams: Record<string, any> = {};
    if (params?.academic_year) queryParams.academic_year = params.academic_year;
    if (params?.subject_id) queryParams.subject_id = params.subject_id;
    const res = await apiClient.get('/teacher-portal/exam-options', { params: queryParams });
    return res.data;
  },



  async getExamResults(examId: number): Promise<ExamResult[]> {
    const res = await apiClient.get<ExamResult[]>(`/teacher-portal/exams/${examId}/results`);
    return res.data;
  },

  async submitExamResults(examId: number, results: BulkResultEntry[]): Promise<ExamResult[]> {
    const res = await apiClient.post<ExamResult[]>(`/teacher-portal/exams/${examId}/results`, { results });
    return res.data;
  },

  async createExam(payload: {
    name: string;
    exam_type: string;
    academic_year: string;
    class_id: number;
    subject_id: number;
    start_date: string;
    end_date?: string | null;
    max_marks?: number;
    pass_marks?: number;
    instructions?: string | null;
  }): Promise<Exam> {
    const res = await apiClient.post<Exam>('/teacher-portal/exams', payload);
    return res.data;
  },

  async getExamRoster(examId: number): Promise<any> {
    const res = await apiClient.get(`/teacher-portal/exams/${examId}/roster`);
    return res.data;
  },

  async saveDraftResults(examId: number, results: any[]): Promise<any> {
    const res = await apiClient.post(`/teacher-portal/exams/${examId}/draft`, { results });
    return res.data;
  },

  async submitExamToAdmin(examId: number, results?: any[], confirmationNotes?: string): Promise<any> {
    const res = await apiClient.post(`/teacher-portal/exams/${examId}/submit`, {
      results,
      confirmation_notes: confirmationNotes,
    });
    return res.data;
  },

  async recallExamResults(examId: number): Promise<any> {
    const res = await apiClient.post(`/teacher-portal/exams/${examId}/recall`);
    return res.data;
  },

  async uploadExamPaper(examId: number, studentId: number, file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post(`/teacher-portal/exams/${examId}/students/${studentId}/paper`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },

  async deleteExamPaper(examId: number, studentId: number): Promise<any> {
    const res = await apiClient.delete(`/teacher-portal/exams/${examId}/students/${studentId}/paper`);
    return res.data;
  },

  getExamPaperUrl(examId: number, studentId: number): string {
    const baseURL = apiClient.defaults.baseURL || '/api/v1';
    return `${baseURL}/teacher-portal/exams/${examId}/students/${studentId}/paper`;
  },

  async getExamPaperBlob(examId: number, studentId: number): Promise<{ blob: Blob; contentType: string }> {
    const res = await apiClient.get(`/teacher-portal/exams/${examId}/students/${studentId}/paper`, {
      responseType: 'blob',
    });
    return {
      blob: res.data,
      contentType: String(res.headers['content-type'] || 'application/octet-stream'),
    };
  },
};
