import { apiClient } from './api';
import {
  StudentDashboardData,
  StudentProfileData,
  StudentClassDetails,
  TimetableSlot,
  StudentAttendanceData,
  StudentFeesData,
  StudentExamResultItem,
} from '../types/studentPortal';

export const studentPortalService = {
  async getDashboard(): Promise<StudentDashboardData> {
    const res = await apiClient.get<StudentDashboardData>('/student-portal/dashboard');
    return res.data;
  },

  async getProfile(): Promise<StudentProfileData> {
    const res = await apiClient.get<StudentProfileData>('/student-portal/profile');
    return res.data;
  },

  async getAcademicYears(): Promise<string[]> {
    const res = await apiClient.get<string[]>('/student-portal/academic-years');
    return res.data;
  },

  async getMyClass(academicYear?: string): Promise<StudentClassDetails> {
    const params = academicYear ? { academic_year: academicYear } : {};
    const res = await apiClient.get<StudentClassDetails>('/student-portal/class', { params });
    return res.data;
  },

  async getMyTimetable(academicYear?: string): Promise<TimetableSlot[]> {
    const params = academicYear ? { academic_year: academicYear } : {};
    const res = await apiClient.get<TimetableSlot[]>('/student-portal/timetable', { params });
    return res.data;
  },

  async getMyAttendance(filters?: {
    academic_year?: string;
    month?: number;
    subject_id?: number;
    status?: string;
  }): Promise<StudentAttendanceData> {
    const res = await apiClient.get<StudentAttendanceData>('/student-portal/attendance', {
      params: filters,
    });
    return res.data;
  },

  async getMyFees(academicYear?: string): Promise<StudentFeesData> {
    const params = academicYear ? { academic_year: academicYear } : {};
    const res = await apiClient.get<StudentFeesData>('/student-portal/fees', { params });
    return res.data;
  },

  async getMyExams(academicYear?: string): Promise<StudentExamResultItem[]> {
    const params = academicYear ? { academic_year: academicYear } : {};
    const res = await apiClient.get<StudentExamResultItem[]>('/student-portal/exams', { params });
    return res.data;
  },

  async recordExamView(payload: {
    exam_name: string;
    academic_year: string;
    class_id?: number | null;
  }): Promise<{ success: boolean; view_count: number }> {
    const res = await apiClient.post('/student-portal/exams/record-view', payload);
    return res.data;
  },
};
