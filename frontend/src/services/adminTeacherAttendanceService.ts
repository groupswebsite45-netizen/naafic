import { apiClient } from './api';
import {
  TeacherDailyRosterResponse,
  TeacherBulkSavePayload,
  TeacherAttendanceDashboardResponse,
  TeacherAttendanceRecordsResponse,
  StaffAttendanceSummaryResponse,
} from '../types/adminTeacherAttendance';

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

export const adminTeacherAttendanceService = {
  async getDailyRoster(date: string, academic_year?: string): Promise<TeacherDailyRosterResponse> {
    const res = await apiClient.get<TeacherDailyRosterResponse>('/admin/teacher-attendance/roster', {
      params: { date, academic_year },
    });
    return res.data;
  },

  async saveAttendance(payload: TeacherBulkSavePayload): Promise<{
    message: string;
    date: string;
    total_saved: number;
    present_count: number;
    absent_count: number;
    late_count: number;
    on_leave_count: number;
  }> {
    const res = await apiClient.post('/admin/teacher-attendance/save', payload);
    return res.data;
  },

  async getDashboard(params?: {
    academic_year?: string;
    month?: number;
    year?: number;
  }): Promise<TeacherAttendanceDashboardResponse> {
    const res = await apiClient.get<TeacherAttendanceDashboardResponse>('/admin/teacher-attendance/dashboard', {
      params,
    });
    return res.data;
  },

  async getRecords(params?: {
    teacher_id?: number;
    academic_year?: string;
    month?: number;
    year?: number;
    start_date?: string;
    end_date?: string;
    status?: string;
    search?: string;
    page?: number;
    page_size?: number;
  }): Promise<TeacherAttendanceRecordsResponse> {
    const res = await apiClient.get<TeacherAttendanceRecordsResponse>('/admin/teacher-attendance/records', {
      params,
    });
    return res.data;
  },

  async getStaffSummary(params?: {
    academic_year?: string;
    month?: number;
    year?: number;
    start_date?: string;
    end_date?: string;
  }): Promise<StaffAttendanceSummaryResponse> {
    const res = await apiClient.get<StaffAttendanceSummaryResponse>('/admin/teacher-attendance/summary', {
      params,
    });
    return res.data;
  },

  async downloadExcel(params: {
    report_type: 'daily' | 'staff_summary';
    date?: string;
    teacher_id?: number;
    academic_year?: string;
    month?: number;
    year?: number;
  }): Promise<void> {
    const res = await apiClient.get('/admin/teacher-attendance/export/excel', {
      params,
      responseType: 'blob',
    });
    const defaultName =
      params.report_type === 'daily'
        ? `Teacher_Daily_Attendance_${params.date || 'today'}.xlsx`
        : 'Staff_Attendance_Summary.xlsx';
    triggerBlobDownload(
      new Blob([res.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      }),
      defaultName,
      res.headers['content-disposition']
    );
  },

  async downloadPdf(params: {
    report_type: 'daily' | 'staff_summary';
    date?: string;
    teacher_id?: number;
    academic_year?: string;
    month?: number;
    year?: number;
  }): Promise<void> {
    const res = await apiClient.get('/admin/teacher-attendance/export/pdf', {
      params,
      responseType: 'blob',
    });
    const defaultName =
      params.report_type === 'daily'
        ? `Teacher_Daily_Attendance_${params.date || 'today'}.pdf`
        : 'Staff_Attendance_Summary.pdf';
    triggerBlobDownload(
      new Blob([res.data], { type: 'application/pdf' }),
      defaultName,
      res.headers['content-disposition']
    );
  },
};

