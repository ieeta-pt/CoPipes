import { useEffect, useState, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/api/stores/authStore";

interface AuthGuardProps {
  children: ReactNode;
  fallbackUrl?: string;
}

export default function AuthGuard({
  children,
  fallbackUrl = "/login",
}: AuthGuardProps) {
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);

  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const token = useAuthStore((state) => state.token);
  const refreshAccessToken = useAuthStore((state) => state.refreshAccessToken);

  useEffect(() => {
    const checkAuth = async () => {
      if (!isAuthenticated || !token) {
        // Try to refresh the token first
        const refreshed = await refreshAccessToken();

        if (!refreshed) {
          // If not authenticated and refresh failed, redirect to login
          router.push(fallbackUrl);
        }
      }

      setIsChecking(false);
    };

    checkAuth();
  }, [isAuthenticated, token, refreshAccessToken, router, fallbackUrl]);

  // Show nothing while checking authentication
  if (isChecking) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  // If authenticated, render children
  return isAuthenticated ? <>{children}</> : null;
}
