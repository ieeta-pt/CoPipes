"use client";

import { Presence, getUserColor } from "@/hooks/useRealtimeCollaboration";

interface RealtimeCursorProps {
  user: Presence;
}

export default function RealtimeCursor({ user }: RealtimeCursorProps) {
  if (!user.cursor) return null;

  const userColor = getUserColor(user.user_id);

  return (
    <div
      className="absolute pointer-events-none z-50 transition-all duration-150 ease-out"
      style={{
        left: user.cursor.x,
        top: user.cursor.y,
        transform: 'translate(-2px, -2px)',
      }}
    >
      {/* Cursor pointer */}
      <div className="relative">
        <svg
          width="20"
          height="20"
          viewBox="0 0 20 20"
          fill="none"
          className="drop-shadow-lg"
        >
          <path
            d="M2 2L14 8L8 10L6 16L2 2Z"
            fill={userColor}
            stroke="white"
            strokeWidth="1.5"
          />
        </svg>
        
        {/* User name label */}
        <div 
          className="absolute top-5 left-2 px-2 py-1 rounded text-white text-xs font-medium whitespace-nowrap drop-shadow-md"
          style={{ backgroundColor: userColor }}
        >
          {user.full_name || user.email.split('@')[0]}
        </div>
      </div>
    </div>
  );
}

// Cursor overlay component to render all cursors
export function CursorOverlay({ otherUsers }: { otherUsers: Presence[] }) {
  return (
    <>
      {otherUsers.map((user) => (
        <RealtimeCursor key={user.user_id} user={user} />
      ))}
    </>
  );
}