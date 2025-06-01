"use client";

import { Presence, getUserColor } from "@/hooks/useRealtimeCollaboration";

interface RealtimeCursorProps {
  user: Presence;
  position: { x: number; y: number };
}

export default function RealtimeCursor({ 
  user, 
  position 
}: RealtimeCursorProps) {
  return (
    <div
      className="absolute pointer-events-none z-50 transition-all duration-100"
      style={{
        left: position.x,
        top: position.y,
        transform: 'translate(-50%, -50%)',
      }}
    >
      {/* Cursor pointer */}
      <div className="relative">
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          className="drop-shadow-md"
        >
          <path
            d="M5.5 3.5L18.5 12L11 14L9 20.5L5.5 3.5Z"
            fill={getUserColor(user.user_id)}
            stroke="white"
            strokeWidth="1"
          />
        </svg>
        
        {/* User name label */}
        <div className="absolute top-6 left-0 bg-black/80 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
          {user.full_name || user.email.split('@')[0]}
        </div>
      </div>
    </div>
  );
}