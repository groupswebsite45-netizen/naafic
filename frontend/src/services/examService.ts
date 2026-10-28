import { apiClient } from './api';
import {
  Exam,
  ExamResult,
  ExamSummary,
  ExamFilterOptions,
  ExamProfile,
  ReportCardData,
  ConflictCheckResponse
} from '../types/school';

export interface CreateExamPayload {
  name: string;
  exam_type: string;
  academic_year: string;
  class_id: number;
  subject_id: number;
  start_date: string;
  end_date?: string | null;
  start_time?: string | null;
  end_time?: string | null;
  result_submission_deadline?: string | null;
  instructions?: string | null;
  max_marks?: number;
  pass_marks?: number;
  total_marks?: number;
  passing_marks?: number;
  exam_date?: string | null;
  status?: string;
}

export interface BatchCreateExamPayload {
  name: string;
  exam_type: string;
  academic_year: string;
  class_ids: number[];
  subject_ids: number[];
  start_date: string;
  end_date?: string | null;
  start_time?: string | null;
  end_time?: string | null;
  result_submission_deadline?: string | null;
  instructions?: string | null;
  max_marks?: number;
  pass_marks?: number;
  status?: string;
}

export interface BulkResultEntry {
  student_id: number;
  marks_obtained: number;
  remarks?: string | null;
}

export interface ConflictCheckPayload {
  class_id: number;
  start_date: string;
  end_date?: string | null;
  exclude_exam_id?: number | null;
}

export const examService = {
  async getSummary(academicYear?: string): Promise<ExamSummary> {
    const params = academicYear ? { academic_year: academicYear } : {};
    const res = await apiClient.get<ExamSummary>('/exams/summary', { params });
    return res.data;
  },

  async getFilterOptions(): Promise<ExamFilterOptions> {
    const res = await apiClient.get<ExamFilterOptions>('/exams/filter-options');
    return res.data;
  },

  async getExams(params?: {
    query?: string;
    class_id?: number;
    subject_id?: number;
    academic_year?: string;
    exam_type?: string;
    status?: string;
    skip?: number;
    limit?: number;
    page?: number;
    page_size?: number;
  }): Promise<Exam[]> {
    const queryParams: Record<string, any> = {};
    if (params?.query) queryParams.query = params.query;
    if (params?.class_id) queryParams.class_id = params.class_id;
    if (params?.subject_id) queryParams.subject_id = params.subject_id;
    if (params?.academic_year) queryParams.academic_year = params.academic_year;
    if (params?.exam_type) queryParams.exam_type = params.exam_type;
    if (params?.status) queryParams.status = params.status;
    if (params?.skip !== undefined) queryParams.skip = params.skip;
    if (params?.limit !== undefined) queryParams.limit = params.limit;
    if (params?.page && params?.page_size) {
      queryParams.skip = (params.page - 1) * params.page_size;
      queryParams.limit = params.page_size;
    }
    const res = await apiClient.get<Exam[]>('/exams', { params: queryParams });
    return res.data;
  },

  async getExamById(id: number): Promise<Exam> {
    const res = await apiClient.get<Exam>(`/exams/${id}`);
    return res.data;
  },

  async getExamProfile(id: number): Promise<ExamProfile> {
    const res = await apiClient.get<ExamProfile>(`/exams/${id}/profile`);
    return res.data;
  },

  async createExam(payload: CreateExamPayload): Promise<Exam> {
    const body = {
      ...payload,
      start_date: payload.start_date || payload.exam_date || new Date().toISOString().split('T')[0],
      max_marks: payload.max_marks ?? payload.total_marks ?? 100,
      pass_marks: payload.pass_marks ?? payload.passing_marks ?? 50,
      status: payload.status || 'SCHEDULED'
    };
    const res = await apiClient.post<Exam>('/exams', body);
    return res.data;
  },

  async createBatchExams(payload: BatchCreateExamPayload): Promise<Exam[]> {
    const res = await apiClient.post<Exam[]>('/exams/batch', payload);
    return res.data;
  },

  async updateExam(id: number, payload: Partial<CreateExamPayload>): Promise<Exam> {
    const res = await apiClient.put<Exam>(`/exams/${id}`, payload);
    return res.data;
  },

  async deleteExam(id: number): Promise<{ success: boolean; message: string }> {
    const res = await apiClient.delete(`/exams/${id}`);
    return res.data;
  },

  async getExamResults(examId: number): Promise<ExamResult[]> {
    const res = await apiClient.get<ExamResult[]>(`/exams/${examId}/results`);
    return res.data;
  },

  async submitBulkExamResults(examId: number, results: BulkResultEntry[]): Promise<ExamResult[]> {
    const res = await apiClient.post<ExamResult[]>(`/exams/${examId}/results`, {
      exam_id: examId,
      results
    });
    return res.data;
  },

  async publishResults(examId: number, publish: boolean = true): Promise<Exam> {
    const res = await apiClient.post<Exam>(`/exams/${examId}/publish`, { publish });
    return res.data;
  },

  async checkConflict(payload: ConflictCheckPayload): Promise<ConflictCheckResponse> {
    const res = await apiClient.post<ConflictCheckResponse>('/exams/check-conflict', payload);
    return res.data;
  },

  async getReportCard(examId: number, studentId: number): Promise<ReportCardData> {
    const res = await apiClient.get<ReportCardData>(`/exams/${examId}/report-card/${studentId}`);
    return res.data;
  },

  async extendDeadline(examId: number, payload: { new_deadline: string; reason?: string }): Promise<Exam> {
    const res = await apiClient.post<Exam>(`/exams/${examId}/extend-deadline`, payload);
    return res.data;
  },

  async reopenSubmissions(examId: number, payload: { new_deadline?: string; reason?: string }): Promise<Exam> {
    const res = await apiClient.post<Exam>(`/exams/${examId}/reopen`, payload);
    return res.data;
  },

  async updateExamStatus(examId: number, status: string): Promise<Exam> {
    const res = await apiClient.patch<Exam>(`/exams/${examId}/status`, { status });
    return res.data;
  },

  async dispatchToTeachers(examId: number): Promise<{ success: boolean; message: string; teacher_name?: string }> {
    const res = await apiClient.post(`/exams/${examId}/dispatch-to-teachers`);
    return res.data;
  }
};

