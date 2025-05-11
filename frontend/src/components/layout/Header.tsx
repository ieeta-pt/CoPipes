"use client";

import { Menu, ChevronDown } from "lucide-react";
import { useState } from "react";
import Image from "next/image";
// import { ModeToggle } from "./mode-toggle"

export function Header() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="shadow-sm bg-base-100">
      <div className="flex h-16 items-center px-4">
        <button
          className="btn btn-ghost btn-circle mr-4"
          onClick={() => setMenuOpen(!menuOpen)}
        >
          <Menu className="h-5 w-5" />
          <span className="sr-only">Toggle menu</span>
        </button>

        <div className="ml-auto flex items-center gap-4">
          {/* <ModeToggle /> */}

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
              <span className="hidden md:inline font-medium">Musharof</span>
              <ChevronDown className="h-4 w-4 opacity-50" />
            </label>
            <ul
              tabIndex={0}
              className="dropdown-content menu p-2 shadow bg-base-100 rounded-box w-52"
            >
              <li className="menu-title">
                <span>My Account</span>
              </li>
              <li>
                <a>Profile</a>
              </li>
              <li>
                <a>Settings</a>
              </li>
              <li>
                <a>Dashboard</a>
              </li>
              <li className="divider" />
              <li>
                <a>Log out</a>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </header>
  );
}
