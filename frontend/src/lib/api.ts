import axios from 'axios';
import { useAuthStore } from '@/stores/authStore';

const api = axios.create({
  // baseURL: import.meta.env.VITE_BASE_API_URL || 'http://localhost:8000/api/v1',
  baseURL: import.meta.env.VITE_BASE_API_URL,
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) throw new Error('No refresh token found');

        // 🔸 Use form-encoded body for FastAPI
        const formData = new URLSearchParams();
        formData.append('refresh_token', refreshToken);

        const response = await axios.post(
          `${api.defaults.baseURL}/auth/refresh`,
          formData,
          {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          }
        );

        const data = response.data.data; // Adjust based on your backend response
        const access_token = data?.access_token || data; // fallback if "data" is just token

        localStorage.setItem('access_token', access_token);

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        useAuthStore.getState().logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
