import { apiClient } from './api';
import {
  ResultFilterOptions,
  ResultOverviewStats,
  ClassResultSummaryItem,
  ClassResultDashboardResponse,
  TeacherSubmissionItem,
  TeacherAccountabilitySummary,
  SubmissionReviewDetail,
  ClassReceiptSummary,
  TeacherExamAssignmentItem,
  DashboardStatistics,
  ClassResultSheetResponse,
  ClassRankingResponse,
  StudentResultReportResponse,
  SubjectPerformanceItem,
  AbsentStudentItem,
} from '../types/resultWorkflow';

function triggerBlobDownload(blob: Blob, defaultFilename: string, contentDisposition?: string) {
  let filename = defaultFilename;
  if (contentDisposition) {
    const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
    if (match && match[1]) {
      filename = match[1].replace(/['"]/g, '');
    }
  }
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

export const resultWorkflowService = {
  // Filters & Global Scoping
  async getFilterOptions(academicYear?: string): Promise<ResultFilterOptions> {
    const res = await apiClient.get('/results/filter-options', {
      params: { academic_year: academicYear },
    });
    return res.data;
  },

  // Admin Overview Stats
  async getOverviewStats(academicYear: string, examName: string): Promise<ResultOverviewStats> {
    const res = await apiClient.get('/results/overview', {
      params: { academic_year: academicYear, exam_name: examName },
    });
    return res.data;
  },

  // Admin Class-First Result Monitoring
  async getClassesResultSummary(academicYear: string, examName: string): Promise<ClassResultSummaryItem[]> {
    const res = await apiClient.get('/results/classes', {
      params: { academic_year: academicYear, exam_name: examName },
    });
    return res.data;
  },

  // Class Detail & Subject Matrix
  async getClassResultDetail(
    classId: number,
    academicYear: string,
    examName: string
  ): Promise<ClassResultDashboardResponse> {
    const res = await apiClient.get(`/results/classes/${classId}`, {
      params: { academic_year: academicYear, exam_name: examName },
    });
    return res.data;
  },

  // Class Result Publication / Release
  async releaseClassResults(
    classId: number,
    payload: { academic_year: string; exam_name: string; release_type: 'FULL' | 'PARTIAL'; notes?: string }
  ): Promise<{ success: boolean; message: string; batch_code: string; results_count: number; released_at: string }> {
    const res = await apiClient.post(`/results/classes/${classId}/release`, payload);
    return res.data;
  },

  // Student Receipt & Delivery Verification
  async getClassReceiptStatus(
    classId: number,
    academicYear: string,
    examName: string
  ): Promise<ClassReceiptSummary> {
    const res = await apiClient.get(`/results/classes/${classId}/receipt`, {
      params: { academic_year: academicYear, exam_name: examName },
    });
    return res.data;
  },

  // Admin Teacher Submissions Monitoring
  async getTeacherSubmissions(params?: {
    academic_year?: string;
    exam_name?: string;
    exam_type?: string;
    teacher_id?: number;
    class_id?: number;
    subject_id?: number;
    status?: string;
  }): Promise<TeacherSubmissionItem[]> {
    const res = await apiClient.get('/results/submissions', { params });
    return res.data;
  },

  // Submission Detail for Admin Review Screen
  async getSubmissionDetail(submissionId: number): Promise<SubmissionReviewDetail> {
    const res = await apiClient.get(`/results/submissions/${submissionId}`);
    return res.data;
  },

  // Admin Action: Approve
  async approveSubmission(submissionId: number, notes?: string): Promise<{ success: boolean; message: string; status: string }> {
    const res = await apiClient.post(`/results/submissions/${submissionId}/approve`, { notes });
    return res.data;
  },

  // Admin Action: Return for Correction
  async returnSubmission(submissionId: number, reason: string): Promise<{ success: boolean; message: string; status: string; return_reason: string }> {
    const res = await apiClient.post(`/results/submissions/${submissionId}/return`, { reason });
    return res.data;
  },

  // Admin Action: Release Single Submission / Result Set
  async releaseSubmission(
    submissionId: number,
    notes?: string
  ): Promise<{ success: boolean; message: string; batch_code: string; results_count: number; status: string; released_at: string }> {
    const res = await apiClient.post(`/results/submissions/${submissionId}/release`, { notes });
    return res.data;
  },

  // Teacher Accountability Metrics
  async getTeacherAccountability(teacherId: number, academicYear?: string): Promise<TeacherAccountabilitySummary> {
    const res = await apiClient.get(`/results/teachers/${teacherId}/accountability`, {
      params: { academic_year: academicYear },
    });
    return res.data;
  },

  // Teacher Portal: Assigned streams
  async getTeacherAssignments(): Promise<TeacherExamAssignmentItem[]> {
    const res = await apiClient.get('/results/teacher/assignments');
    return res.data;
  },

  // Teacher Portal: Student roster for marks entry
  async getTeacherExamRoster(examId: number): Promise<any> {
    const res = await apiClient.get(`/results/teacher/exams/${examId}/roster`);
    return res.data;
  },

  // Teacher Portal: Save Draft
  async saveTeacherDraft(payload: {
    exam_id: number;
    class_id: number;
    subject_id: number;
    marks: { student_id: number; attendance_status: string; marks_obtained: number | null; remarks?: string }[];
  }): Promise<{ success: boolean; message: string; status: string }> {
    const res = await apiClient.post('/results/teacher/draft', payload);
    return res.data;
  },

  // Teacher Portal: Submit to Admin
  async submitTeacherResults(payload: {
    exam_id: number;
    class_id: number;
    subject_id: number;
    marks: { student_id: number; attendance_status: string; marks_obtained: number | null; remarks?: string }[];
    notes?: string;
  }): Promise<{ success: boolean; message: string; status: string; submission_id: number }> {
    const res = await apiClient.post('/results/teacher/submit', payload);
    return res.data;
  },

  // Student Portal: Get released results only
  async getStudentReleasedResults(): Promise<any[]> {
    const res = await apiClient.get('/results/student/my-results');
    return res.data;
  },

  // Student Portal: Record view tracking event
  async recordStudentView(payload: { exam_name: string; academic_year: string; class_id?: number }): Promise<any> {
    const res = await apiClient.post('/results/student/record-view', payload);
    return res.data;
  },

  // --- Advanced Results Management System Methods ---

  // 1. Dashboard 10 Real-Time KPIs
  async getDashboardStatistics(
    academicYear: string,
    examName: string,
    division?: string
  ): Promise<DashboardStatistics> {
    const res = await apiClient.get('/results/dashboard/statistics', {
      params: { academic_year: academicYear, exam_name: examName, division },
    });
    return res.data;
  },

  // 2. Class Result Sheet Matrix & Summaries
  async getClassResultSheet(
    classId: number,
    academicYear: string,
    examName: string
  ): Promise<ClassResultSheetResponse> {
    const res = await apiClient.get(`/results/classes/${classId}/sheet`, {
      params: { academic_year: academicYear, exam_name: examName },
    });
    return res.data;
  },

  // 3. Download Class Result Sheet PDF
  async downloadClassResultSheetPdf(
    classId: number,
    academicYear: string,
    examName: string
  ): Promise<void> {
    const res = await apiClient.get(`/results/classes/${classId}/sheet/pdf`, {
      params: { academic_year: academicYear, exam_name: examName },
      responseType: 'blob',
    });
    triggerBlobDownload(
      new Blob([res.data], { type: 'application/pdf' }),
      `Class_Result_Sheet_${classId}.pdf`,
      res.headers['content-disposition']
    );
  },

  // 4. Class Rankings & Merit List
  async getClassRankings(
    classId: number,
    academicYear: string,
    examName: string,
    division?: string
  ): Promise<ClassRankingResponse> {
    const res = await apiClient.get(`/results/classes/${classId}/rankings`, {
      params: { academic_year: academicYear, exam_name: examName, division },
    });
    return res.data;
  },

  // 5. Download Class Rankings PDF
  async downloadClassRankingsPdf(
    classId: number,
    academicYear: string,
    examName: string,
    division?: string
  ): Promise<void> {
    const res = await apiClient.get(`/results/classes/${classId}/rankings/pdf`, {
      params: { academic_year: academicYear, exam_name: examName, division },
      responseType: 'blob',
    });
    triggerBlobDownload(
      new Blob([res.data], { type: 'application/pdf' }),
      `Class_Rankings_${classId}.pdf`,
      res.headers['content-disposition']
    );
  },

  // 6. Download Class Rankings Excel
  async downloadClassRankingsExcel(
    classId: number,
    academicYear: string,
    examName: string,
    division?: string
  ): Promise<void> {
    const res = await apiClient.get(`/results/classes/${classId}/rankings/excel`, {
      params: { academic_year: academicYear, exam_name: examName, division },
      responseType: 'blob',
    });
    triggerBlobDownload(
      new Blob([res.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      }),
      `Class_Rankings_${classId}.xlsx`,
      res.headers['content-disposition']
    );
  },

  // 7. Student Result Report Card JSON
  async getStudentResultReport(
    studentId: number,
    academicYear: string,
    examName?: string
  ): Promise<StudentResultReportResponse> {
    const res = await apiClient.get(`/results/students/${studentId}/report`, {
      params: { academic_year: academicYear, exam_name: examName },
    });
    return res.data;
  },

  // 8. Download Student Report Card PDF
  async downloadStudentReportCardPdf(
    studentId: number,
    academicYear: string,
    examName?: string
  ): Promise<void> {
    const res = await apiClient.get(`/results/students/${studentId}/report/pdf`, {
      params: { academic_year: academicYear, exam_name: examName },
      responseType: 'blob',
    });
    triggerBlobDownload(
      new Blob([res.data], { type: 'application/pdf' }),
      `Student_Report_Card_${studentId}.pdf`,
      res.headers['content-disposition']
    );
  },

  // 9. Subject Performance List
  async getSubjectPerformanceList(params: {
    academic_year: string;
    exam_name: string;
    class_id?: number;
    subject_id?: number;
    division?: string;
  }): Promise<SubjectPerformanceItem[]> {
    const res = await apiClient.get('/results/subject-performance', { params });
    return res.data;
  },

  // 10. Absent Students List
  async getAbsentStudentsList(params: {
    academic_year: string;
    exam_name: string;
    class_id?: number;
    subject_id?: number;
    division?: string;
  }): Promise<AbsentStudentItem[]> {
    const res = await apiClient.get('/results/absent-students', { params });
    return res.data;
  },
};

