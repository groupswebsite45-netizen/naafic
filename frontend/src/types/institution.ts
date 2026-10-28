export interface Institution {
  id: number;
  code: string;
  name: string;
  type: string;
  logo_url?: string | null;
  contact_person?: string | null;
  email?: string | null;
  phone?: string | null;
  region?: string | null;
  city?: string | null;
  address?: string | null;
  status: 'ACTIVE' | 'SUSPENDED' | 'PENDING';
  database_name?: string | null;
  admin_email?: string | null;
  admin_username?: string | null;
  subscription_plan: string;
  subscription_status: string;
  subscription_start_date?: string | null;
  subscription_expiry_date?: string | null;
  admin_user_id?: number | null;
  total_students?: number;
  total_teachers?: number;
  created_at: string;
  updated_at: string;
}

export interface InstitutionUpdatePayload {
  name?: string;
  type?: string;
  logo_url?: string | null;
  contact_person?: string | null;
  email?: string | null;
  phone?: string | null;
  region?: string | null;
  city?: string | null;
  address?: string | null;
  status?: string;
  subscription_plan?: string;
  subscription_status?: string;
  subscription_start_date?: string | null;
  subscription_expiry_date?: string | null;
  admin_username?: string | null;
  admin_email?: string | null;
  admin_password?: string | null;
}

export interface AdminAccountCreate {
  full_name: string;
  email: string;
  username: string;
  password: string;
  phone_number?: string;
}

export interface InstitutionCreatePayload {
  name: string;
  type: string;
  logo_url?: string;
  contact_person?: string;
  email?: string;
  phone?: string;
  region?: string;
  city?: string;
  address?: string;
  subscription_plan: string;
  subscription_start_date?: string;
  subscription_expiry_date?: string;
  status: string;
  admin_account?: AdminAccountCreate;
}

export interface Subscription {
  id: number;
  institution_id: number;
  institution_name?: string;
  institution_code?: string;
  plan_name: string;
  billing_cycle: string;
  price: number;
  setup_fee: number;
  status: string;
  start_date: string;
  end_date: string;
  auto_renew: boolean;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface InstitutionPayment {
  id: number;
  institution_id: number;
  institution_name?: string;
  subscription_id?: number | null;
  reference: string;
  amount: number;
  currency: string;
  payment_method: string;
  payment_date: string;
  status: string;
  invoice_number?: string;
  notes?: string;
  created_at: string;
}

export interface TypeBreakdown {
  name: string;
  count: number;
  percentage: number;
}

export interface RecentActivityItem {
  id: number;
  type: 'registration' | 'subscription' | 'payment' | 'user';
  title: string;
  subtitle: string;
  timestamp: string;
  status?: string;
}

export interface StatusBreakdownItem {
  status: string;
  count: number;
  percentage: number;
}

export interface MonthlyRevenueItem {
  month: string;
  amount: number;
}

export interface SuperAdminDashboardStats {
  total_institutions: number;
  total_schools: number;
  total_academies: number;
  total_students?: number;
  total_teachers?: number;
  active_subscriptions: number;
  expired_subscriptions: number;
  pending_subscriptions?: number;
  total_revenue?: number;
  total_payments_amount: number;
  platform_usage?: number;
  type_breakdown: TypeBreakdown[];
  subscription_breakdown?: StatusBreakdownItem[];
  monthly_revenue?: MonthlyRevenueItem[];
  recent_institutions: Institution[];
  recent_payments?: InstitutionPayment[];
  recent_activities: RecentActivityItem[];
}

