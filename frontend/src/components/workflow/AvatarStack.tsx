"use client";

import { useState, useEffect } from "react";
import Image from "next/image";

interface User {
  email: string;
  avatar_url?: string | null;
  full_name?: string;
}

interface AvatarStackProps {
  collaborators: string[];
  maxVisible?: number;
  size?: "sm" | "md" | "lg";
}

export default function AvatarStack({
  collaborators,
  maxVisible = 3,
  size = "sm",
}: AvatarStackProps) {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);

  const sizeClasses = {
    sm: "w-8 h-8 text-xs",
    md: "w-10 h-10 text-sm",
    lg: "w-12 h-12 text-base",
  };

  // Fetch user data for collaborators
  useEffect(() => {
    const fetchUserData = async () => {
      if (!collaborators.length) return;

      setLoading(true);
      try {
        // For now, we'll use email as the main identifier
        // TODO: Integrate with Supabase to get actual user profiles
        const userPromises = collaborators.map(async (email) => {
          // Mock user data - in real implementation, this would fetch from Supabase
          return {
            email,
            avatar_url: null, // Will use default avatar
            full_name: email.split("@")[0], // Extract name from email as fallback
          };
        });

        const userData = await Promise.all(userPromises);
        setUsers(userData);
      } catch (error) {
        console.error("Failed to fetch user data:", error);
        // Fallback to email-only data
        setUsers(
          collaborators.map((email) => ({
            email,
            avatar_url: null,
            full_name: email.split("@")[0],
          }))
        );
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, [collaborators]);

  if (!collaborators.length) {
    return (
      <span className="text-base-content/50 text-sm">No collaborators</span>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center">
        <div
          className={`${sizeClasses[size]} bg-base-200 rounded-full animate-pulse`}
        ></div>
      </div>
    );
  }

  const visibleUsers = users.slice(0, maxVisible);
  const remainingCount = Math.max(0, users.length - maxVisible);

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((part) => part.charAt(0))
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  const getAvatarSrc = (user: User) => {
    // Use user's avatar if available, otherwise return null for initials
    return user.avatar_url;
  };

  return (
    <div className="flex items-center">
      <div className="flex -space-x-2">
        {visibleUsers.map((user, index) => (
          <div
            key={user.email}
            className={`${sizeClasses[size]} rounded-full border-2 border-white bg-base-200 flex items-center justify-center overflow-hidden relative`}
            style={{ zIndex: maxVisible - index }}
            title={`${user.full_name || user.email} (${user.email})`}
          >
            {getAvatarSrc(user) ? (
              <Image
                src={getAvatarSrc(user)!}
                alt={user.full_name || user.email}
                width={size === "sm" ? 32 : size === "md" ? 40 : 48}
                height={size === "sm" ? 32 : size === "md" ? 40 : 48}
                className="rounded-full object-cover"
                onError={(e) => {
                  // Fallback to initials if image fails to load
                  const target = e.target as HTMLImageElement;
                  target.style.display = "none";
                  const parent = target.parentElement;
                  if (parent) {
                    parent.innerHTML = `<div class="w-full h-full flex items-center justify-center bg-blue-400 text-white font-medium">${getInitials(
                      user.full_name || user.email
                    )}</div>`;
                  }
                }}
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center bg-blue-400 text-white font-medium">
                {getInitials(user.full_name || user.email)}
              </div>
            )}
          </div>
        ))}

        {remainingCount > 0 && (
          <div
            className={`${sizeClasses[size]} rounded-full border-2 border-white bg-base-300 flex items-center justify-center text-base-content font-medium`}
            title={`+${remainingCount} more collaborator${
              remainingCount > 1 ? "s" : ""
            }`}
          >
            +{remainingCount}
          </div>
        )}
      </div>

      {users.length === 1 && (
        <span className="ml-2 text-sm text-base-content/70">
          {visibleUsers[0].full_name?.split(" ")[0] ||
            visibleUsers[0].email.split("@")[0]}
        </span>
      )}
    </div>
  );
}
