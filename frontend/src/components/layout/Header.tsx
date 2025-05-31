"use client";

import { House, ChevronDown, User, LogOut } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";

export function Header() {
  const { user, isAuthenticated, logout } = useAuth();
  const router = useRouter();

  const handleLogoClick = () => {
    if (isAuthenticated) {
      router.push('/dashboard');
    } else {
      router.push('/');
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="navbar shadow-md bg-base-100">
        <div className="navbar-start ml-4">
          <button className="btn btn-ghost" onClick={handleLogoClick}>
            <House className="h-6 w-6"/>
          </button>
        </div>
        <div className="navbar-end mr-4">
          <div className="flex gap-2">
            <Link href="/auth/login" className="btn btn-ghost">
              Sign In
            </Link>
            <Link href="/auth/signup" className="btn btn-primary">
              Sign Up
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="navbar shadow-md bg-base-100">
      <div className="navbar-start ml-4">
        <button className="btn btn-ghost" onClick={handleLogoClick}>
          <House className="h-6 w-6"/>
        </button>
      </div>
      <div className="navbar-end mr-4">
        <div className="dropdown dropdown-end">
          <div 
            tabIndex={0} 
            role="button" 
            className="btn btn-ghost px-2 gap-2"
          >
            <div className="avatar">
              <div className="w-8 rounded-full">
                <Image
                  src="/profile_pic.png"
                  alt="User"
                  width={32}
                  height={32}
                />
              </div>
            </div>
            <span className="hidden md:inline font-medium">
              {user?.full_name || user?.email?.split('@')[0] || 'User'}
            </span>
            <ChevronDown className="h-4 w-4 opacity-50" />
          </div>
          <ul 
            tabIndex={0} 
            className="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52"
          >
            <li>
              <Link href="/profile" className="flex items-center gap-2">
                <User className="h-4 w-4" />
                Profile
              </Link>
            </li>
            <li>
              <button 
                onClick={logout}
                className="flex items-center gap-2 w-full text-left"
              >
                <LogOut className="h-4 w-4" />
                Sign Out
              </button>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
