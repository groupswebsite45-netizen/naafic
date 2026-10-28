import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

// Request Interceptor: Attach JWT Token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('sms_access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    const isLoginRequest = config.url && config.url.includes('/auth/login');
    const urlHasInst = typeof window !== 'undefined' && window.location.search && window.location.search.includes('institution=');

    const activeInstStr = localStorage.getItem('sms_active_institution');
    if (activeInstStr && config.headers && (!isLoginRequest || urlHasInst)) {
      try {
        const inst = JSON.parse(activeInstStr);
        if (inst && inst.id) {
          config.headers['X-Institution-Id'] = String(inst.id);
        }
        if (inst && inst.code) {
          config.headers['X-Institution-Code'] = String(inst.code);
        }
      } catch (e) {
        // ignore JSON parse error
      }
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle auth failures
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response && error.response.status === 401) {
      // Clear invalid session if unauthorized on protected endpoint
      if (!window.location.pathname.includes('/login')) {
        localStorage.removeItem('sms_access_token');
        localStorage.removeItem('sms_refresh_token');
        localStorage.removeItem('sms_user');
        window.location.href = '/login?expired=true';
      }
    }
    return Promise.reject(error);
  }
);
