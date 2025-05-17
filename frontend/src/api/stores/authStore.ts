import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import axios from 'axios';

// Define the API base URL
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Define types
interface User {
  id: string;
  email: string;
  full_name?: string;
  created_at: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshAccessToken: () => Promise<boolean>;
  fetchUserProfile: () => Promise<void>;
}

// Create the auth store with persistence
export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Login function
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await axios.post(`${API_URL}/api/auth/token`, 
            new URLSearchParams({
              'username': email,
              'password': password,
            }), 
            {
              headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
              },
            }
          );

          const { access_token, refresh_token, expires_in, user } = response.data;
          
          // Set auth state
          set({ 
            token: access_token, 
            refreshToken: refresh_token,
            user, 
            isAuthenticated: true, 
            isLoading: false 
          });
          
          // Set up axios interceptor for authenticated requests
          setupAuthInterceptor();
          
        } catch (error: any) {
          set({ 
            isLoading: false, 
            error: error.response?.data?.detail || 'Failed to login' 
          });
          throw error;
        }
      },

      // Register function
      register: async (email: string, password: string, fullName?: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await axios.post(`${API_URL}/api/auth/register`, {
            email,
            password,
            full_name: fullName
          });
          
          // Auto login after registration
          await get().login(email, password);
          
        } catch (error: any) {
          set({ 
            isLoading: false, 
            error: error.response?.data?.detail || 'Failed to register' 
          });
          throw error;
        }
      },

      // Logout function
      logout: async () => {
        set({ isLoading: true });
        try {
          // Call logout API endpoint if refresh token is available
          if (get().refreshToken) {
            await axios.post(`${API_URL}/api/auth/logout`, {
              refresh_token: get().refreshToken
            });
          }
          
          // Clear auth state
          set({ 
            user: null, 
            token: null, 
            refreshToken: null, 
            isAuthenticated: false, 
            isLoading: false 
          });
          
        } catch (error) {
          // Even if API call fails, we still clear local state
          set({ 
            user: null, 
            token: null, 
            refreshToken: null, 
            isAuthenticated: false, 
            isLoading: false 
          });
        }
      },

      // Refresh token function
      refreshAccessToken: async () => {
        const { refreshToken } = get();
        if (!refreshToken) return false;
        
        try {
          const response = await axios.post(`${API_URL}/api/auth/refresh`, {
            refresh_token: refreshToken
          });
          
          const { access_token, refresh_token, user } = response.data;
          
          set({ 
            token: access_token, 
            refreshToken: refresh_token,
            user, 
            isAuthenticated: true 
          });
          
          return true;
        } catch (error) {
          // If refresh fails, logout the user
          await get().logout();
          return false;
        }
      },

      // Fetch user profile
      fetchUserProfile: async () => {
        const { token } = get();
        if (!token) return;
        
        try {
          const response = await axios.get(`${API_URL}/api/auth/me`, {
            headers: {
              Authorization: `Bearer ${token}`
            }
          });
          
          set({ user: response.data });
        } catch (error) {
          // If profile fetch fails, try to refresh token once
          const refreshed = await get().refreshAccessToken();
          if (refreshed) {
            // Try again with new token
            await get().fetchUserProfile();
          }
        }
      }
    }),
    {
      name: 'auth-storage', // Name for localStorage
      partialize: (state) => ({ 
        token: state.token, 
        refreshToken: state.refreshToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated
      }),
    }
  )
);

// Setup axios interceptor for authenticated requests
function setupAuthInterceptor() {
  axios.interceptors.request.use(
    (config) => {
      const { token } = useAuthStore.getState();
      if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  axios.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;
      
      // If error is 401 and we haven't already tried to refresh
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;
        
        const refreshed = await useAuthStore.getState().refreshAccessToken();
        if (refreshed) {
          // Update the token in the request
          const { token } = useAuthStore.getState();
          originalRequest.headers['Authorization'] = `Bearer ${token}`;
          
          // Retry the request
          return axios(originalRequest);
        }
      }
      
      return Promise.reject(error);
    }
  );
} 