import { apiClient } from './api';
import {
  TeacherAttendanceOptionsResponse,
  TeacherAttendanceRosterResponse,
  TeacherSaveAttendancePayload,
  TeacherAttendanceSessionItem,
  TeacherAttendanceSummaryResponse,
  StudentAttendanceHistoryDetailResponse,
} from '../types/attendance';

export const attendanceService = {
  async getOptions(params?: {
    academic_year?: string;
    class_id?: number;
  }): Promise<TeacherAttendanceOptionsResponse> {
    const res = await apiClient.get<TeacherAttendanceOptionsResponse>('/teacher-portal/attendance/options', {
      params,
    });
    return res.data;
  },

  async getRoster(params: {
    class_id: number;
    subject_id: number;
    date: string;
    academic_year?: string;
    period?: string;
  }): Promise<TeacherAttendanceRosterResponse> {
    const res = await apiClient.get<TeacherAttendanceRosterResponse>('/teacher-portal/attendance/roster', {
      params,
    });
    return res.data;
  },

  async saveAttendance(payload: TeacherSaveAttendancePayload): Promise<{
    message: string;
    class_id: number;
    class_name: string;
    subject_id: number;
    subject_name: string;
    date: string;
    period?: string;
    total_saved: number;
    present_count: number;
    late_count: number;
    absent_count: number;
  }> {
    const res = await apiClient.post('/teacher-portal/attendance/save', payload);
    return res.data;
  },

  async getHistory(params?: {
    class_id?: number;
    subject_id?: number;
    academic_year?: string;
    month?: number;
    date?: string;
  }): Promise<TeacherAttendanceSessionItem[]> {
    const res = await apiClient.get<TeacherAttendanceSessionItem[]>('/teacher-portal/attendance/history', {
      params,
    });
    return res.data;
  },

  async getSummary(params: {
    class_id: number;
    subject_id?: number;
    start_date?: string;
    end_date?: string;
  }): Promise<TeacherAttendanceSummaryResponse> {
    const res = await apiClient.get<TeacherAttendanceSummaryResponse>('/teacher-portal/attendance/summary', {
      params,
    });
    return res.data;
  },

  async getStudentBreakdown(
    studentId: number,
    academicYear?: string
  ): Promise<StudentAttendanceHistoryDetailResponse> {
    const res = await apiClient.get<StudentAttendanceHistoryDetailResponse>(
      `/teacher-portal/attendance/students/${studentId}/breakdown`,
      {
        params: { academic_year: academicYear },
      }
    );
    return res.data;
  },
};
