import axios, { AxiosRequestConfig, AxiosResponse } from 'axios';

// Base API configuration
const API_URL = 'http://localhost:8000/api/v1';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Define API endpoints
export const apiEndpoints = {
  // Auth endpoints
  auth: {
    login: '/accounts/login/',
    register: '/accounts/register/',
    logout: '/accounts/logout/',
    refreshToken: '/accounts/token/refresh/',
    resetPassword: '/accounts/password-reset/',
    resetPasswordConfirm: '/accounts/password-reset/confirm/',
    changePassword: '/accounts/password/change/',
    profile: '/accounts/profile/',
  },
  // User endpoints
  users: {
    list: '/accounts/users/',
    detail: (id: string) => `/accounts/users/${id}/`,
    create: '/accounts/users/',
    update: (id: string) => `/accounts/users/${id}/`,
    delete: (id: string) => `/accounts/users/${id}/`,
  },
  // Role endpoints
  roles: {
    list: '/accounts/roles/',
    detail: (id: string) => `/accounts/roles/${id}/`,
    create: '/accounts/roles/',
    update: (id: string) => `/accounts/roles/${id}/`,
    delete: (id: string) => `/accounts/roles/${id}/`,
  },
  // Permission endpoints
  permissions: {
    list: '/accounts/permissions/',
    detail: (id: string) => `/accounts/permissions/${id}/`,
  },
};

// Generic request function
export const apiRequest = async <T = any>(
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE',
  endpoint: string,
  data?: any,
  options?: Omit<AxiosRequestConfig, 'method' | 'url' | 'data'>
): Promise<AxiosResponse<T>> => {
  const config: AxiosRequestConfig = {
    method,
    url: endpoint,
    ...options,
  };

  if (data) {
    config.data = data;
  }

  try {
    return await api(config);
  } catch (error) {
    console.error('API Request Error:', error);
    throw error;
  }
};

// Export default
export default api; 