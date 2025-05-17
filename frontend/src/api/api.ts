import axios from 'axios';
import { useAuthStore } from '@/api/stores/authStore';

// Create a base axios instance
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to attach token to all requests
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshed = await useAuthStore.getState().refreshAccessToken();
      if (refreshed) {
        const token = useAuthStore.getState().token;
        originalRequest.headers['Authorization'] = `Bearer ${token}`;
        return api(originalRequest);
      }
    }
    
    return Promise.reject(error);
  }
);

// Export API methods for different resources

// Workflows
export const workflowsApi = {
  getAll: async () => {
    const response = await api.get('/api/workflows');
    return response.data;
  },
  
  getById: async (workflowId: string) => {
    const response = await api.get(`/api/workflows/${workflowId}`);
    return response.data;
  },
  
  create: async (workflow: any) => {
    const response = await api.post('/api/workflows', workflow);
    return response.data;
  },
  
  update: async (workflowId: string, workflow: any) => {
    const response = await api.put(`/api/workflows/${workflowId}`, workflow);
    return response.data;
  },
  
  delete: async (workflowId: string) => {
    const response = await api.delete(`/api/workflows/${workflowId}`);
    return response.data;
  },
  
  getDags: async () => {
    const response = await api.get('/api/get_dags');
    return response.data;
  },
  
  uploadFile: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// Export the api instance
export default api; 