"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { apiClient } from "@/services/api";
import ProfileOrganizations from "@/components/profile/ProfileOrganizations";

function validatePassword(password: string): string | null {
  if (password.length < 12) {
    return "Password must be at least 12 characters long";
  }
  
  if (!/[A-Z]/.test(password)) {
    return "Password must contain at least one uppercase letter";
  }
  
  if (!/[a-z]/.test(password)) {
    return "Password must contain at least one lowercase letter";
  }
  
  if (!/\d/.test(password)) {
    return "Password must contain at least one number";
  }
  
  if (!/[!@#$%^&*()_+\-=\[\]{};:,.<>?]/.test(password)) {
    return "Password must contain at least one special character";
  }
  
  return null;
}

interface User {
  id: string;
  email: string;
  full_name?: string;
  organizations?: Array<{
    organization_id: string;
    organization_name: string;
    role: string;
  }>;
}

export default function ProfilePage() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const router = useRouter();
  const { user, token, logout, isAuthenticated } = useAuth();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/auth/login");
      return;
    }

    if (user) {
      setFullName(user.full_name || "");
      setEmail(user.email || "");
    }
  }, [user, isAuthenticated, router]);

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    // Validate password change if attempted
    if (newPassword) {
      const passwordError = validatePassword(newPassword);
      if (passwordError) {
        setError(passwordError);
        setLoading(false);
        return;
      }
      if (newPassword !== confirmPassword) {
        setError("New passwords do not match");
        setLoading(false);
        return;
      }
    }

    try {
      const updateData: any = {};
      
      if (fullName !== user?.full_name) {
        updateData.full_name = fullName;
      }
      
      if (email !== user?.email) {
        updateData.email = email;
      }
      
      if (newPassword) {
        updateData.password = newPassword;
      }

      const data = await apiClient.put("/api/auth/update-profile", updateData);
      
      setSuccess(data.message);
      
      // Note: In a session-based auth system, we'd need to update the AuthContext
      // For now, just clear password fields
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (error) {
      setError(error instanceof Error ? error.message : "Update failed");
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = () => {
    logout();
  };

  if (!user) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
        <div className="loading loading-spinner loading-lg"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Organizations Section */}
      <ProfileOrganizations />

      {/* Profile Settings Section */}
      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <h2 className="card-title text-2xl font-bold mb-6">Profile Settings</h2>
          
          {error && (
            <div className="alert alert-error mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{error}</span>
            </div>
          )}
          
          {success && (
            <div className="alert alert-success mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{success}</span>
            </div>
          )}

          <form onSubmit={handleUpdateProfile} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="form-control">
                <label className="label">
                  <span className="label-text">Full Name</span>
                </label>
                <input
                  type="text"
                  placeholder="Enter your full name"
                  className="input input-bordered w-full"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                />
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text">Email</span>
                </label>
                <input
                  type="email"
                  placeholder="Enter your email"
                  className="input input-bordered w-full"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            </div>

            <div className="divider">Change Password</div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="form-control">
                <label className="label">
                  <span className="label-text">New Password</span>
                </label>
                <input
                  type="password"
                  placeholder="Enter new password"
                  className="input input-bordered w-full"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  minLength={12}
                />
                <label className="label">
                  <span className="label-text-alt">12+ characters with uppercase, lowercase, number, and special character</span>
                </label>
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text">Confirm New Password</span>
                </label>
                <input
                  type="password"
                  placeholder="Confirm new password"
                  className="input input-bordered w-full"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                />
              </div>
            </div>

            <div className="card-actions justify-between items-center pt-4">
              <button
                type="button"
                className="btn btn-outline btn-error"
                onClick={handleSignOut}
              >
                Sign Out
              </button>
              
              <button
                type="submit"
                className={`btn btn-primary ${loading ? "loading" : ""}`}
                disabled={loading}
              >
                {loading ? "Updating..." : "Update Profile"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}