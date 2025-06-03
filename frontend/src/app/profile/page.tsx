"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { Organization } from "@/types/organization";
import { organizationApi } from "@/api/organizations";

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
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [orgLoading, setOrgLoading] = useState(true);
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

    // Load user's organizations
    loadOrganizations();
  }, [user, isAuthenticated, router]);

  const loadOrganizations = async () => {
    try {
      setOrgLoading(true);
      const userOrgs = await organizationApi.getUserOrganizations();
      setOrganizations(userOrgs);
    } catch (err) {
      console.error("Failed to load organizations:", err);
    } finally {
      setOrgLoading(false);
    }
  };

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    // Validate password change if attempted
    if (newPassword) {
      if (newPassword.length < 6) {
        setError("New password must be at least 6 characters long");
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

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/update-profile`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify(updateData),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(data.message);
        
        // Note: In a session-based auth system, we'd need to update the AuthContext
        // For now, just clear password fields
        setCurrentPassword("");
        setNewPassword("");
        setConfirmPassword("");
      } else {
        setError(data.detail || "Update failed");
      }
    } catch (error) {
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = () => {
    logout();
  };

  const handleCreateOrganization = () => {
    router.push('/organizations');
  };

  const handleOrganizationClick = (orgId: string) => {
    router.push(`/organizations/${orgId}`);
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
      <div className="card bg-base-100 shadow-xl mb-6">
        <div className="card-body">
          <div className="flex justify-between items-center mb-4">
            <h2 className="card-title text-2xl font-bold">My Organizations</h2>
            <button 
              className="btn btn-primary"
              onClick={handleCreateOrganization}
            >
              Create Organization
            </button>
          </div>
          
          {orgLoading ? (
            <div className="flex justify-center py-8">
              <div className="loading loading-spinner loading-lg"></div>
            </div>
          ) : organizations.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {organizations.map((org) => (
                <div 
                  key={org.id} 
                  className="card bg-base-200 shadow-md cursor-pointer hover:shadow-lg transition-shadow"
                  onClick={() => handleOrganizationClick(org.id)}
                >
                  <div className="card-body p-4">
                    <h3 className="card-title text-lg">{org.name}</h3>
                    {org.description && (
                      <p className="text-sm text-base-content/70 line-clamp-2">{org.description}</p>
                    )}
                    <div className="flex justify-between items-center mt-2">
                      <div className="badge badge-outline badge-sm">
                        {org.member_count} member{org.member_count !== 1 ? 's' : ''}
                      </div>
                      <div className="text-xs text-base-content/60">
                        {new Date(org.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="text-base-content/60 mb-4">
                <svg className="w-16 h-16 mx-auto mb-4 text-base-content/30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
                You're not part of any organizations yet.
              </div>
              <button 
                className="btn btn-primary"
                onClick={handleCreateOrganization}
              >
                Create Your First Organization
              </button>
            </div>
          )}
        </div>
      </div>

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
                  minLength={6}
                />
                <label className="label">
                  <span className="label-text-alt">Leave blank to keep current password</span>
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