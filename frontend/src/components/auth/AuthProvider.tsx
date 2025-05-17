"use client";

import { ReactNode, useEffect } from "react";
import { useAuthStore } from "@/api/stores/authStore";

interface AuthProviderProps {
  children: ReactNode;
}

export default function AuthProvider({ children }: AuthProviderProps) {
  const fetchUserProfile = useAuthStore((state) => state.fetchUserProfile);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const token = useAuthStore((state) => state.token);

  // When the component mounts, try to fetch the user profile if we have a token
  useEffect(() => {
    if (isAuthenticated && token) {
      fetchUserProfile();
    }
  }, [isAuthenticated, token, fetchUserProfile]);

  return <>{children}</>;
}
