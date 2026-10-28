export interface Role {
  id: number;
  name: string;
  description?: string;
  is_system: boolean;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  phone_number?: string;
  is_active: boolean;
  is_superuser: boolean;
  last_login_at?: string;
  created_at: string;
  updated_at: string;
  roles: Role[];
}

export interface UserProfileUpdatePayload {
  full_name?: string;
  phone_number?: string;
}
