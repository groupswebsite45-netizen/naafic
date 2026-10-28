import { User } from './user';

export interface LoginPayload {
  identifier: string;
  password: string;
  remember_me?: boolean;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface CurrentUserResponse {
  user: User;
  permissions: string[];
}

export interface PasswordChangePayload {
  current_password: string;
  new_password: string;
}
