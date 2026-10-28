export type InquiryStatus = 'UNREAD' | 'READ' | 'IN_REVIEW' | 'CONTACTED' | 'CONVERTED' | 'ARCHIVED';
export type InquiryPriority = 'LOW' | 'NORMAL' | 'HIGH' | 'URGENT';

export interface Inquiry {
  id: number;
  full_name: string;
  school_name: string;
  email: string;
  phone: string;
  plan?: string | null;
  message: string;
  status: InquiryStatus;
  priority: InquiryPriority;
  admin_notes?: string | null;
  contacted_by?: string | null;
  preferred_channel?: string | null;
  source: string;
  converted_institution_id?: number | null;
  created_at: string;
  updated_at: string;
}

export interface InquiryListResponse {
  items: Inquiry[];
  total: number;
  unread_count: number;
  in_review_count: number;
  contacted_count: number;
  converted_count: number;
  archived_count: number;
}

export interface InquiryStats {
  total: number;
  unread: number;
  in_review: number;
  contacted: number;
  converted: number;
  today: number;
}

export interface InquiryCreatePayload {
  full_name: string;
  school_name: string;
  email: string;
  phone: string;
  plan?: string;
  message: string;
  preferred_channel?: string;
}

export interface InquiryUpdatePayload {
  status?: InquiryStatus;
  priority?: InquiryPriority;
  admin_notes?: string;
  contacted_by?: string;
  preferred_channel?: string;
}

export interface InquiryConvertPayload {
  institution_type?: string;
  region?: string;
  city?: string;
  subscription_plan?: string;
  admin_username?: string;
}

export interface InquiryConvertResponse {
  success: boolean;
  message: string;
  institution_id: number;
  institution_code: string;
  institution_name: string;
  database_name: string;
  admin_username: string;
  temporary_password?: string;
}
