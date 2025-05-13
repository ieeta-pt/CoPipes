"use client";

import { House, ChevronDown } from "lucide-react";
import { useState } from "react";
import Image from "next/image";

export function Header() {
  return (
    <div className="navbar shadow-md bg-base-100">
      <div className="navbar-start ml-4">
        <button className="btn btn-ghost" onClick={() => window.location.href = '/dashboard'}>
          <House className="h-6 w-6"/>
        </button>
      </div>
      <div className="navbar-end mr-4">
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
              {/* <ChevronDown className="h-4 w-4 opacity-50" /> */}
            </label>
        </div>
    </div>
  );
}
