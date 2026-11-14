import { apiClient } from './api';
import {
  AdminAttendanceFilterOptionsResponse,
  AdminAttendanceDashboardResponse,
  AdminAttendanceRecordsListResponse,
  AdminClassAttendanceReportResponse,
  AdminAttendanceFrequentAbsenteeItem,
} from '../types/adminAttendance';
import { StudentAttendanceHistoryDetailResponse } from '../types/attendance';

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
  link.parentNode?.removeChild(link);
  window.URL.revokeObjectURL(url);
}

export const adminAttendanceService = {
  async getFilterOptions(params?: {
    academic_year?: string;
    class_id?: number;
    subject_id?: number;
  }): Promise<AdminAttendanceFilterOptionsResponse> {
    const res = await apiClient.get<AdminAttendanceFilterOptionsResponse>('/admin/attendance/filter-options', {
      params,
    });
    return res.data;
  },

  async getDashboard(params?: {
    academic_year?: string;
    month?: number;
    year?: number;
    class_id?: number;
    subject_id?: number;
    teacher_id?: number;
    date?: string;
    threshold?: number;
  }): Promise<AdminAttendanceDashboardResponse> {
    const res = await apiClient.get<AdminAttendanceDashboardResponse>('/admin/attendance/dashboard', {
      params,
    });
    return res.data;
  },

  async getRecords(params?: {
    academic_year?: string;
    month?: number;
    year?: number;
    start_date?: string;
    end_date?: string;
    class_id?: number;
    subject_id?: number;
    teacher_id?: number;
    student_id?: number;
    status?: string;
    search?: string;
    date?: string;
    page?: number;
    page_size?: number;
  }): Promise<AdminAttendanceRecordsListResponse> {
    const res = await apiClient.get<AdminAttendanceRecordsListResponse>('/admin/attendance/records', {
      params,
    });
    return res.data;
  },

  async getClassReport(
    classId: number,
    params?: {
      subject_id?: number;
      teacher_id?: number;
      academic_year?: string;
      month?: number;
      year?: number;
      start_date?: string;
      end_date?: string;
      date?: string;
    }
  ): Promise<AdminClassAttendanceReportResponse> {
    const res = await apiClient.get<AdminClassAttendanceReportResponse>(
      `/admin/attendance/classes/${classId}/report`,
      { params }
    );
    return res.data;
  },

  async getFrequentAbsences(params?: {
    class_id?: number;
    subject_id?: number;
    teacher_id?: number;
    academic_year?: string;
    month?: number;
    year?: number;
    threshold?: number;
    percentage_threshold?: number;
  }): Promise<AdminAttendanceFrequentAbsenteeItem[]> {
    const res = await apiClient.get<AdminAttendanceFrequentAbsenteeItem[]>('/admin/attendance/frequent-absences', {
      params,
    });
    return res.data;
  },

  async getStudentBreakdown(
    studentId: number,
    academicYear?: string
  ): Promise<StudentAttendanceHistoryDetailResponse> {
    const res = await apiClient.get<StudentAttendanceHistoryDetailResponse>(
      `/admin/attendance/students/${studentId}/breakdown`,
      {
        params: { academic_year: academicYear },
      }
    );
    return res.data;
  },

  async downloadExcel(params: {
    report_type: 'class_report' | 'frequent_absentees';
    class_id?: number;
    subject_id?: number;
    teacher_id?: number;
    academic_year?: string;
    month?: number;
    year?: number;
    threshold?: number;
  }): Promise<void> {
    const res = await apiClient.get('/admin/attendance/export/excel', {
      params,
      responseType: 'blob',
    });
    let defaultName =
      params.report_type === 'class_report'
        ? `Class_${params.class_id}_Attendance.xlsx`
        : 'Frequent_Absentees.xlsx';
    if (params.subject_id) {
      defaultName = defaultName.replace('.xlsx', `_Subj_${params.subject_id}.xlsx`);
    }
    triggerBlobDownload(
      new Blob([res.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      }),
      defaultName,
      res.headers['content-disposition']
    );
  },

  async downloadPdf(params: {
    report_type: 'class_report' | 'frequent_absentees';
    class_id?: number;
    subject_id?: number;
    teacher_id?: number;
    academic_year?: string;
    month?: number;
    year?: number;
    threshold?: number;
  }): Promise<void> {
    const res = await apiClient.get('/admin/attendance/export/pdf', {
      params,
      responseType: 'blob',
    });
    let defaultName =
      params.report_type === 'class_report'
        ? `Class_${params.class_id}_Attendance.pdf`
        : 'Frequent_Absentees.pdf';
    if (params.subject_id) {
      defaultName = defaultName.replace('.pdf', `_Subj_${params.subject_id}.pdf`);
    }
    triggerBlobDownload(
      new Blob([res.data], { type: 'application/pdf' }),
      defaultName,
      res.headers['content-disposition']
    );
  },
};

