import { apiClient } from './api';
import {
  TimetableEntry,
  TimetableSummary,
  TimetableFilterOptions,
  TimetableFilterParams,
  TimetableCheckConflictPayload,
  TimetableConflictCheckResponse,
  TimetableSetting,
  TeacherAvailability,
  ClassTimetableOverview,
  TimetableGeneratePayload,
  TimetableGenerateResponse
} from '../types/school';

export interface CreateTimetablePayload {
  class_id: number;
  subject_id: number;
  teacher_id?: number | null;
  classroom_id?: number | null;
  academic_year: string;
  day_of_week: string;
  period_number?: number | null;
  start_time: string;
  end_time: string;
  room?: string | null;
  room_number?: string | null;
  status?: string;
  is_break?: boolean;
}

export interface TimetablePublishPayload {
  class_id?: number | null;
  academic_year?: string | null;
  timetable_ids?: number[];
}

export interface TimetableBatchSavePayload {
  class_id: number;
  academic_year: string;
  slots: Array<{
    id?: number | null;
    subject_id: number;
    teacher_id?: number | null;
    classroom_id?: number | null;
    day_of_week: string;
    period_number?: number | null;
    start_time: string;
    end_time: string;
    room_number?: string | null;
    is_break?: boolean;
    status?: string;
  }>;
  delete_unlisted?: boolean;
}

export interface TimetableMoveSlotPayload {
  slot_id: number;
  target_day: string;
  target_period_number?: number | null;
  target_start_time: string;
  target_end_time: string;
  target_room?: string | null;
}

export interface TimetableSwapSlotsPayload {
  slot_id_1: number;
  slot_id_2: number;
}

export const timetableService = {
  async getSummary(academicYear?: string): Promise<TimetableSummary> {
    const res = await apiClient.get<TimetableSummary>('/timetable/summary', {
      params: academicYear ? { academic_year: academicYear } : undefined,
    });
    return res.data;
  },

  async getFilterOptions(academicYear?: string): Promise<TimetableFilterOptions> {
    const res = await apiClient.get<TimetableFilterOptions>('/timetable/filter-options', {
      params: academicYear ? { academic_year: academicYear } : undefined,
    });
    return res.data;
  },

  async checkConflict(payload: TimetableCheckConflictPayload): Promise<TimetableConflictCheckResponse> {
    const res = await apiClient.post<TimetableConflictCheckResponse>('/timetable/check-conflict', payload);
    return res.data;
  },

  async getTimetable(params?: TimetableFilterParams): Promise<TimetableEntry[]> {
    const queryParams: Record<string, any> = {};
    if (params?.class_id) queryParams.class_id = params.class_id;
    if (params?.teacher_id) queryParams.teacher_id = params.teacher_id;
    if (params?.subject_id) queryParams.subject_id = params.subject_id;
    if (params?.day_of_week) queryParams.day_of_week = params.day_of_week;
    if (params?.academic_year) queryParams.academic_year = params.academic_year;
    if (params?.room) queryParams.room = params.room;
    if (params?.status) queryParams.status = params.status;
    if (params?.skip !== undefined) queryParams.skip = params.skip;
    if (params?.limit !== undefined) queryParams.limit = params.limit;

    const res = await apiClient.get<TimetableEntry[]>('/timetable', { params: queryParams });
    return res.data;
  },

  async getTimetableById(id: number): Promise<TimetableEntry> {
    const res = await apiClient.get<TimetableEntry>(`/timetable/${id}`);
    return res.data;
  },

  async createTimetable(payload: CreateTimetablePayload): Promise<TimetableEntry> {
    const res = await apiClient.post<TimetableEntry>('/timetable', payload);
    return res.data;
  },

  async updateTimetable(id: number, payload: Partial<CreateTimetablePayload>): Promise<TimetableEntry> {
    const res = await apiClient.put<TimetableEntry>(`/timetable/${id}`, payload);
    return res.data;
  },

  async deleteTimetable(id: number): Promise<{ message: string }> {
    const res = await apiClient.delete<{ message: string }>(`/timetable/${id}`);
    return res.data;
  },

  // --- Advanced Class-First & Generation APIs ---

  async getClassOverview(classId: number, academicYear?: string): Promise<ClassTimetableOverview> {
    const res = await apiClient.get<ClassTimetableOverview>(`/timetable/class-overview/${classId}`, {
      params: academicYear ? { academic_year: academicYear } : undefined
    });
    return res.data;
  },

  async generateTimetable(payload: TimetableGeneratePayload): Promise<TimetableGenerateResponse> {
    const res = await apiClient.post<TimetableGenerateResponse>('/timetable/generate', payload);
    return res.data;
  },

  async batchSaveTimetable(payload: TimetableBatchSavePayload): Promise<TimetableEntry[]> {
    const res = await apiClient.post<TimetableEntry[]>('/timetable/batch-save', payload);
    return res.data;
  },

  async moveSlot(payload: TimetableMoveSlotPayload): Promise<TimetableEntry> {
    const res = await apiClient.post<TimetableEntry>('/timetable/move-slot', payload);
    return res.data;
  },

  async swapSlots(payload: TimetableSwapSlotsPayload): Promise<TimetableEntry[]> {
    const res = await apiClient.post<TimetableEntry[]>('/timetable/swap-slots', payload);
    return res.data;
  },

  async publishTimetable(payload: TimetablePublishPayload): Promise<{ message: string; published_count: number }> {
    const res = await apiClient.post<{ message: string; published_count: number }>('/timetable/publish', payload);
    return res.data;
  },

  async unpublishTimetable(payload: TimetablePublishPayload): Promise<{ message: string; unpublished_count: number }> {
    const res = await apiClient.post<{ message: string; unpublished_count: number }>('/timetable/unpublish', payload);
    return res.data;
  },

  async getSettings(academicYear?: string, educationLevel?: string): Promise<TimetableSetting> {
    const res = await apiClient.get<TimetableSetting>('/timetable/settings', {
      params: {
        ...(academicYear ? { academic_year: academicYear } : {}),
        ...(educationLevel ? { education_level: educationLevel } : {})
      }
    });
    return res.data;
  },

  async saveSettings(payload: TimetableSetting): Promise<TimetableSetting> {
    const res = await apiClient.post<TimetableSetting>('/timetable/settings', payload);
    return res.data;
  },

  async getTeacherAvailability(teacherId: number, academicYear?: string): Promise<TeacherAvailability[]> {
    const res = await apiClient.get<TeacherAvailability[]>(`/timetable/teacher-availability/${teacherId}`, {
      params: academicYear ? { academic_year: academicYear } : undefined
    });
    return res.data;
  },

  async setTeacherAvailability(payload: {
    teacher_id: number;
    academic_year: string;
    availabilities: Array<{
      day_of_week: string;
      is_available: boolean;
      start_time?: string | null;
      end_time?: string | null;
      max_periods_per_day?: number | null;
      notes?: string | null;
    }>;
  }): Promise<{ message: string; saved_count: number }> {
    const res = await apiClient.post<{ message: string; saved_count: number }>('/timetable/teacher-availability', payload);
    return res.data;
  },

  async getAvailabilityMatrix(academicYear?: string): Promise<Record<string, Record<string, boolean>>> {
    const res = await apiClient.get<Record<string, Record<string, boolean>>>('/timetable/teacher-availability-matrix', {
      params: academicYear ? { academic_year: academicYear } : undefined
    });
    return res.data;
  },

  async validateTimetable(academicYear: string, classId?: number): Promise<{
    is_valid: boolean;
    total_conflicts: number;
    conflicts: any[];
  }> {
    const res = await apiClient.get('/timetable/validate', {
      params: {
        academic_year: academicYear,
        ...(classId ? { class_id: classId } : {})
      }
    });
    return res.data;
  },

  async downloadClassPdf(classId: number, academicYear: string): Promise<Blob> {
    const res = await apiClient.get(`/timetable/pdf/class/${classId}`, {
      params: { academic_year: academicYear },
      responseType: 'blob'
    });
    return res.data;
  },

  async downloadTeacherPdf(teacherId: number, academicYear: string): Promise<Blob> {
    const res = await apiClient.get(`/timetable/pdf/teacher/${teacherId}`, {
      params: { academic_year: academicYear },
      responseType: 'blob'
    });
    return res.data;
  }
};
