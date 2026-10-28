import { User } from './user';

export interface ModuleStatus {
  id: string;
  name: string;
  description: string;
  status: 'AVAILABLE' | 'PLANNED' | 'DEVELOPMENT';
  is_installed: boolean;
  badge_color: string;
  route_path?: string | null;
}

export interface ActivityLog {
  id: number;
  action: string;
  status: string;
  ip_address?: string;
  created_at: string;
  details?: Record<string, any>;
}

export interface DashboardOverview {
  system_status: string;
  database_status: string;
  database_name: string;
  active_sessions_count: number;
  system_uptime_seconds: number;
  current_admin: User;
  modules: ModuleStatus[];
  recent_activity: ActivityLog[];
  metrics?: {
    total_students: number;
    active_students: number;
    total_teachers: number;
    active_teachers: number;
    total_classes: number;
    total_subjects: number;
    today_timetable_count: number;
    upcoming_exams_count: number;
    total_fees_billed: number;
    total_fees_collected: number;
    total_fees_outstanding: number;
  };
}

export interface SystemHealth {
  status: string;
  database_connected: boolean;
  database_name: string;
  server_time: string;
  app_version: string;
  environment: string;
}

export interface SystemSetting {
  id: number;
  key: string;
  value: string;
  description?: string;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}
