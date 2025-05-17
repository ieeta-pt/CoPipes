"use client";

import { House, ChevronDown, Menu, User, LogIn } from "lucide-react";
import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { useAuthStore } from "@/api/stores/authStore";
// import { ModeToggle } from "./mode-toggle"

export function Header() {
  const [menuOpen, setMenuOpen] = useState(false);
  const { user, isAuthenticated, logout } = useAuthStore();

  return (
    <div className="navbar shadow-md bg-base-100">
      <div className="navbar-start ml-4">
        <Link href="/dashboard" className="btn btn-ghost">
          <House className="h-6 w-6" />
        </Link>
      </div>

      <div className="navbar-center hidden lg:flex">
        <ul className="menu menu-horizontal px-1 gap-2">
          <li>
            <Link href="/dashboard">Dashboard</Link>
          </li>
          <li>
            <Link href="/workflow">Workflows</Link>
          </li>
        </ul>
      </div>

      <div className="navbar-end mr-4">
        {isAuthenticated ? (
          <div className="dropdown dropdown-end">
            <label tabIndex={0} className="btn btn-ghost px-2 gap-2">
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
                {user?.full_name || user?.email || "User"}
              </span>
              <ChevronDown className="h-4 w-4 opacity-50" />
            </label>
            <ul
              tabIndex={0}
              className="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52"
            >
              <li>
                <Link href="/profile">Profile</Link>
              </li>
              <li>
                <button onClick={() => logout()}>Logout</button>
              </li>
            </ul>
          </div>
        ) : (
          <div className="flex gap-2">
            <Link href="/login" className="btn btn-ghost gap-2">
              <LogIn className="h-5 w-5" />
              <span className="hidden md:inline">Login</span>
            </Link>
            <Link href="/register" className="btn btn-primary gap-2">
              <User className="h-5 w-5" />
              <span className="hidden md:inline">Register</span>
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
