"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiClient } from "@/services/api";

interface User {
  id: string;
  email: string;
  full_name?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
  isAuthenticated: boolean;
  sessionId: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [sessionId, setSessionId] = useState<string>('');
  const router = useRouter();

  // Initialize session ID safely on client side
  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Check if we already have a session ID for this tab/window
    const existingSessionId = sessionStorage.getItem('auth_session_id');
    if (existingSessionId) {
      setSessionId(existingSessionId);
      return;
    }
    
    // Generate new unique session ID for this tab/window
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
    sessionStorage.setItem('auth_session_id', newSessionId);
    setSessionId(newSessionId);
  }, []);

  useEffect(() => {
    // Only check for auth in browser environment and when sessionId is available
    if (typeof window === 'undefined') {
      setLoading(false);
      return;
    }

    if (!sessionId) {
      // Don't set loading to false yet - wait for sessionId to be initialized
      return;
    }

    // Check for existing auth on mount using session-based storage
    const storedToken = localStorage.getItem(`access_token_${sessionId}`);
    const storedUser = localStorage.getItem(`user_${sessionId}`);

    if (storedToken && storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        setToken(storedToken);
        setUser(parsedUser);
        
        // Configure API client IMMEDIATELY
        apiClient.setAuth(storedToken, logout);
        
        // Verify token is still valid (but don't block)
        verifyToken(storedToken);
      } catch (error) {
        console.error("Error parsing stored user data:", error);
        logout();
      }
    }
    setLoading(false);
  }, [sessionId]);

  const verifyToken = async (token: string) => {
    try {
      // Use apiClient to ensure consistent token handling
      await apiClient.get("/api/auth/me");
    } catch (error) {
      console.error("Token verification failed:", error);
      logout();
    }
  };

  const login = (newToken: string, newUser: User) => {
    
    // Configure API client FIRST to ensure it's ready for immediate use
    apiClient.setAuth(newToken, logout);
    
    if (typeof window !== 'undefined' && sessionId) {
      localStorage.setItem(`access_token_${sessionId}`, newToken);
      localStorage.setItem(`user_${sessionId}`, JSON.stringify(newUser));
    }
    setToken(newToken);
    setUser(newUser);
  };

  const logout = () => {
    if (typeof window !== 'undefined' && sessionId) {
      localStorage.removeItem(`access_token_${sessionId}`);
      localStorage.removeItem(`user_${sessionId}`);
    }
    setToken(null);
    setUser(null);
    // Clear API client auth
    apiClient.setAuth(null);
    router.push("/auth/login");
  };

  // Update API client whenever token changes
  useEffect(() => {
    apiClient.setAuth(token, logout);
  }, [token]);

  const value = {
    user,
    token,
    loading,
    login,
    logout,
    isAuthenticated: !!token && !!user,
    sessionId,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

// Higher-order component for protecting routes
export function withAuth<P extends object>(
  WrappedComponent: React.ComponentType<P>
) {
  return function AuthenticatedComponent(props: P) {
    const { isAuthenticated, loading } = useAuth();
    const router = useRouter();

    useEffect(() => {
      if (!loading && !isAuthenticated) {
        router.push("/auth/login");
      }
    }, [isAuthenticated, loading, router]);

    if (loading) {
      return (
        <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
          <div className="loading loading-spinner loading-lg"></div>
        </div>
      );
    }

    if (!isAuthenticated) {
      return null;
    }

    return <WrappedComponent {...props} />;
  };
}