"use client";

import AuthGuard from "@/components/auth/AuthGuard";
import UserProfile from "@/components/auth/UserProfile";

export default function ProfilePage() {
  return (
    <AuthGuard>
      <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold mb-8">Your Profile</h1>

        <UserProfile />
      </div>
    </AuthGuard>
  );
}
