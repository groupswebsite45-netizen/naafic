import { apiClient } from './api';

export type PromotionActionType = 'PROMOTE' | 'REPEAT' | 'TRANSFER' | 'GRADUATE' | 'EXCLUDE' | 'NO_CHANGE';

export interface StudentPromotionOverrideItem {
  student_id: number;
  action: PromotionActionType;
  target_class_id?: number | null;
  reason?: string | null;
}

export interface ClassPromotionMappingItem {
  from_class_id: number;
  to_class_id?: number | null;
  action: 'PROMOTE' | 'GRADUATE' | 'NO_CHANGE';
}

export interface ClassPromotionMappingSuggestion {
  from_class_id: number;
  from_class_name: string;
  from_class_code: string;
  education_level?: 'PRIMARY' | 'SECONDARY' | string | null;
  level_name?: string | null;
  level_number?: number | null;
  section?: string | null;
  to_class_id?: number | null;
  to_class_name?: string | null;
  to_class_code?: string | null;
  action: 'PROMOTE' | 'GRADUATE' | 'NO_CHANGE';
  student_count: number;
  is_terminal_class: boolean;
  missing_destination_warning: boolean;
  warning_message?: string | null;
}

export interface TargetClassOption {
  id: number;
  name: string;
  code: string;
  division?: string | null;
  level?: string | null;
  section?: string | null;
  academic_year: string;
  capacity: number;
  enrolled_count: number;
  status: string;
}

export interface SuggestedMappingsResponse {
  source_academic_year: string;
  target_academic_year: string;
  education_level?: 'PRIMARY' | 'SECONDARY' | string | null;
  mappings: ClassPromotionMappingSuggestion[];
  available_target_classes: TargetClassOption[];
  academic_years: string[];
}

export interface StudentPromotionPreviewItem {
  student_id: number;
  admission_number: string;
  student_name: string;
  gender?: string | null;
  education_level?: string | null;
  current_class_id: number;
  current_class_name: string;
  current_section?: string | null;
  target_class_id?: number | null;
  target_class_name?: string | null;
  target_section?: string | null;
  source_academic_year?: string | null;
  target_academic_year?: string | null;
  action: 'PROMOTED' | 'REPEATED' | 'TRANSFERRED' | 'GRADUATED' | 'EXCLUDED' | 'SKIPPED' | string;
  status: 'READY' | 'VALIDATION_ERROR' | 'ALREADY_ENROLLED' | 'GRADUATING' | 'REPEATING' | 'EXCLUDED' | string;
  is_valid: boolean;
  validation_message?: string | null;
}

export interface ClassMappingPreviewSummary {
  from_class_id: number;
  from_class_name: string;
  from_class_code: string;
  education_level?: string | null;
  section?: string | null;
  to_class_id?: number | null;
  to_class_name?: string | null;
  to_class_code?: string | null;
  action: string;
  students_count: number;
  valid_count: number;
  error_count: number;
  warning_message?: string | null;
}

export interface BulkPromotionPreviewResponse {
  source_academic_year: string;
  target_academic_year: string;
  education_level?: string | null;
  total_students_affected: number;
  total_to_promote: number;
  total_to_repeat: number;
  total_to_graduate: number;
  total_excluded: number;
  total_validation_errors: number;
  missing_destination_classes_count: number;
  can_execute: boolean;
  class_summaries: ClassMappingPreviewSummary[];
  student_previews: StudentPromotionPreviewItem[];
  validation_errors: string[];
}

export interface ExecuteBulkPromotionPayload {
  source_academic_year: string;
  target_academic_year: string;
  education_level?: string | null;
  mappings: ClassPromotionMappingItem[];
  student_overrides?: StudentPromotionOverrideItem[];
  reason?: string;
}

export interface IndividualClassChangePayload {
  new_class_id: number;
  academic_year: string;
  reason?: string;
  is_promotion?: boolean;
  preserve_history?: boolean;
}

export interface IndividualClassChangeResponse {
  message: string;
  student_id: number;
  student_name: string;
  old_class_name?: string | null;
  new_class_name: string;
  academic_year: string;
  enrollment_id: number;
  batch_code?: string | null;
  timestamp: string;
}

export interface ClassLevelPromotionPayload {
  from_class_id: number;
  to_class_id?: number | null;
  source_academic_year: string;
  target_academic_year: string;
  action?: 'PROMOTE' | 'GRADUATE';
  student_ids?: number[];
  student_overrides?: StudentPromotionOverrideItem[];
  reason?: string;
}

export interface IndividualStudentPromotionPayload {
  student_id: number;
  source_academic_year: string;
  target_academic_year: string;
  action: 'PROMOTE' | 'REPEAT' | 'TRANSFER' | 'GRADUATE' | 'EXCLUDE';
  target_class_id?: number | null;
  reason?: string;
}

export interface StudentSearchForPromotionItem {
  student_id: number;
  admission_number: string;
  student_name: string;
  gender?: string | null;
  current_class_id?: number | null;
  current_class_name?: string | null;
  current_division?: string | null;
  current_level?: string | null;
  current_section?: string | null;
  current_academic_year?: string | null;
  status: string;
  suggested_next_class_id?: number | null;
  suggested_next_class_name?: string | null;
  is_terminal: boolean;
}

export interface PromotionRecordItem {
  id: number;
  batch_id: number;
  student_id: number;
  student_name: string;
  admission_number: string;
  from_class_name?: string | null;
  to_class_name?: string | null;
  source_academic_year: string;
  target_academic_year: string;
  action: string;
  status: string;
  reason?: string | null;
  created_at: string;
}

export interface PromotionBatch {
  id: number;
  batch_code: string;
  source_academic_year: string;
  target_academic_year: string;
  promotion_type: string;
  status: string;
  total_promoted: number;
  total_graduated: number;
  total_skipped: number;
  reason?: string | null;
  created_by_name?: string | null;
  created_at: string;
  records_count: number;
  records?: PromotionRecordItem[];
}

export interface BatchRollbackResponse {
  success: boolean;
  message: string;
  batch_code: string;
  restored_students_count: number;
}

export const classPromotionService = {
  async getSuggestedMappings(
    sourceYear?: string,
    targetYear?: string,
    educationLevel?: 'PRIMARY' | 'SECONDARY' | string
  ): Promise<SuggestedMappingsResponse> {
    const res = await apiClient.get<SuggestedMappingsResponse>('/class-promotions/suggested-mappings', {
      params: {
        source_year: sourceYear,
        target_year: targetYear,
        education_level: educationLevel,
      },
    });
    return res.data;
  },

  async previewBulkPromotion(payload: {
    source_academic_year: string;
    target_academic_year: string;
    education_level?: string | null;
    mappings: ClassPromotionMappingItem[];
    student_overrides?: StudentPromotionOverrideItem[];
  }): Promise<BulkPromotionPreviewResponse> {
    const res = await apiClient.post<BulkPromotionPreviewResponse>('/class-promotions/preview', payload);
    return res.data;
  },

  async executeBulkPromotion(payload: ExecuteBulkPromotionPayload): Promise<PromotionBatch> {
    const res = await apiClient.post<PromotionBatch>('/class-promotions/bulk', payload);
    return res.data;
  },

  async executeClassLevelPromotion(payload: ClassLevelPromotionPayload): Promise<PromotionBatch> {
    const res = await apiClient.post<PromotionBatch>('/class-promotions/class-level', payload);
    return res.data;
  },

  async executeIndividualPromotion(payload: IndividualStudentPromotionPayload): Promise<PromotionBatch> {
    const res = await apiClient.post<PromotionBatch>('/class-promotions/individual-promote', payload);
    return res.data;
  },

  async searchStudentsForPromotion(params: {
    q?: string;
    class_id?: number;
    education_level?: string;
    academic_year?: string;
    limit?: number;
  }): Promise<StudentSearchForPromotionItem[]> {
    const res = await apiClient.get<StudentSearchForPromotionItem[]>('/class-promotions/students/search', { params });
    return res.data;
  },

  async changeStudentClass(
    studentId: number,
    payload: IndividualClassChangePayload
  ): Promise<IndividualClassChangeResponse> {
    const res = await apiClient.post<IndividualClassChangeResponse>(
      `/class-promotions/students/${studentId}/change-class`,
      payload
    );
    return res.data;
  },

  async listHistory(params?: {
    academic_year?: string;
    promotion_type?: string;
    status?: string;
    skip?: number;
    limit?: number;
  }): Promise<PromotionBatch[]> {
    const res = await apiClient.get<PromotionBatch[]>('/class-promotions/history', { params });
    return res.data;
  },

  async getBatchDetails(batchId: number): Promise<PromotionBatch> {
    const res = await apiClient.get<PromotionBatch>(`/class-promotions/history/${batchId}`);
    return res.data;
  },

  async rollbackBatch(batchId: number): Promise<BatchRollbackResponse> {
    const res = await apiClient.post<BatchRollbackResponse>(`/class-promotions/history/${batchId}/rollback`);
    return res.data;
  },
};
