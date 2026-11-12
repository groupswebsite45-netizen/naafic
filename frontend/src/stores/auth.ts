import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { User } from '../types/user';
import { LoginPayload } from '../types/auth';
import { authService } from '../services/authService';

import { Institution } from '../types/institution';

function getInitialUser(): User | null {
  const saved = localStorage.getItem('sms_user');
  if (saved) {
    try {
      return JSON.parse(saved);
    } catch {
      return null;
    }
  }
  return null;
}

function getInitialActiveInstitution(): Institution | null {
  const saved = localStorage.getItem('sms_active_institution');
  if (saved) {
    try {
      return JSON.parse(saved);
    } catch {
      return null;
    }
  }
  return null;
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(getInitialUser());
  const activeInstitution = ref<Institution | null>(getInitialActiveInstitution());

  const accessToken = ref<string | null>(localStorage.getItem('sms_access_token'));
  const refreshToken = ref<string | null>(localStorage.getItem('sms_refresh_token'));
  const isLoading = ref<boolean>(false);
  const authError = ref<string | null>(null);

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value);

  const isSuperAdmin = computed(() => {
    if (!user.value) return false;
    if (user.value.is_superuser) return true;
    return user.value.roles?.some((r) => r.name.toUpperCase() === 'SUPER_ADMIN') ?? false;
  });

  const isAdmin = computed(() => {
    if (!user.value) return false;
    if (user.value.is_superuser) return true;
    return user.value.roles?.some((r) => r.name.toUpperCase() === 'ADMIN') ?? false;
  });

  const isTeacher = computed(() => {
    if (!user.value) return false;
    return user.value.roles?.some((r) => r.name.toUpperCase() === 'TEACHER') ?? false;
  });

  const isStudent = computed(() => {
    if (!user.value) return false;
    return user.value.roles?.some((r) => r.name.toUpperCase() === 'STUDENT') ?? false;
  });

  const defaultRoute = computed(() => {
    if (isSuperAdmin.value) return '/super-admin/dashboard';
    if (isAdmin.value) return '/admin/dashboard';
    if (isTeacher.value) return '/teacher/dashboard';
    if (isStudent.value) return '/student/dashboard';
    return '/login';
  });

  const userRolesList = computed(() => {
    if (!user.value?.roles) return [];
    return user.value.roles.map((r) => r.name);
  });

  function setActiveInstitution(inst: Institution) {
    activeInstitution.value = inst;
    localStorage.setItem('sms_active_institution', JSON.stringify(inst));
  }

  function clearActiveInstitution() {
    activeInstitution.value = null;
    localStorage.removeItem('sms_active_institution');
  }

  // Actions
  async function login(credentials: LoginPayload) {
    isLoading.value = true;
    authError.value = null;

    try {
      const response = await authService.login(credentials);
      
      accessToken.value = response.access_token;
      refreshToken.value = response.refresh_token;
      user.value = response.user;

      localStorage.setItem('sms_access_token', response.access_token);
      localStorage.setItem('sms_refresh_token', response.refresh_token);
      localStorage.setItem('sms_user', JSON.stringify(response.user));

      if (response.user.is_superuser || response.user.roles?.some((r: any) => r.name.toUpperCase() === 'SUPER_ADMIN')) {
        clearActiveInstitution();
      } else if ((response as any).institution) {
        setActiveInstitution((response as any).institution as Institution);
      }

      return response.user;
    } catch (err: any) {
      const msg = err.response?.data?.error?.message || err.response?.data?.detail || 'Authentication failed. Please check your credentials.';
      authError.value = msg;
      throw new Error(msg);
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchCurrentUser() {
    if (!accessToken.value) return null;
    try {
      const data = await authService.getCurrentUser();
      user.value = data.user;
      localStorage.setItem('sms_user', JSON.stringify(data.user));
      if ((data as any).institution) {
        setActiveInstitution((data as any).institution as Institution);
      }
      return data.user;
    } catch {
      logout();
      return null;
    }
  }

  async function logout() {
    const token = refreshToken.value;
    try {
      if (token) {
        await authService.logout(token);
      }
    } catch {
      // Ignore network errors on logout
    } finally {
      user.value = null;
      accessToken.value = null;
      refreshToken.value = null;
      localStorage.removeItem('sms_access_token');
      localStorage.removeItem('sms_refresh_token');
      localStorage.removeItem('sms_user');
      clearActiveInstitution();
    }
  }

  async function applyToken(token: string) {
    accessToken.value = token;
    localStorage.setItem('sms_access_token', token);
    return await fetchCurrentUser();
  }

  function updateUserProfile(updated: Partial<User>) {
    if (user.value) {
      user.value = { ...user.value, ...updated };
      localStorage.setItem('sms_user', JSON.stringify(user.value));
    }
  }

  return {
    user,
    accessToken,
    refreshToken,
    isLoading,
    authError,
    isAuthenticated,
    isSuperAdmin,
    isAdmin,
    isTeacher,
    isStudent,
    defaultRoute,
    activeInstitution,
    setActiveInstitution,
    clearActiveInstitution,
    userRolesList,
    login,
    logout,
    applyToken,
    fetchCurrentUser,
    updateUserProfile,
  };
});
