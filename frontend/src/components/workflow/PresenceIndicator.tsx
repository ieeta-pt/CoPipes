"use client";

import { useRealtimeCollaboration, Presence } from "@/hooks/useRealtimeCollaboration";
import AvatarStack from "./AvatarStack";

interface PresenceIndicatorProps {
  workflowId?: string;
  className?: string;
}

export default function PresenceIndicator({ 
  workflowId, 
  className = "" 
}: PresenceIndicatorProps) {
  const { otherUsers, isConnected } = useRealtimeCollaboration({
    workflowId,
    enabled: !!workflowId
  });

  if (!workflowId || !isConnected || otherUsers.length === 0) {
    return null;
  }

  // Convert presence data to collaborator emails for AvatarStack
  const collaboratorEmails = otherUsers.map(user => user.email);

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div className="flex items-center gap-1">
        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
        <span className="text-sm text-base-content/70">
          {otherUsers.length} online
        </span>
      </div>
      <AvatarStack 
        collaborators={collaboratorEmails}
        maxVisible={5}
        size="sm"
      />
    </div>
  );
}

// Activity feed component
export function ActivityFeed({ workflowId }: { workflowId?: string }) {
  const { otherUsers, isConnected } = useRealtimeCollaboration({
    workflowId,
    enabled: !!workflowId
  });

  if (!workflowId || !isConnected) {
    return null;
  }

  return (
    <div className="bg-base-100 border border-base-200 rounded-lg p-3 max-w-sm">
      <div className="flex items-center gap-2 mb-2">
        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
        <span className="font-medium text-sm">Live Activity</span>
      </div>
      
      <div className="space-y-2">
        {otherUsers.length === 0 ? (
          <p className="text-sm text-base-content/60">
            No other users currently active
          </p>
        ) : (
          otherUsers.map((user) => (
            <div key={user.user_id} className="flex items-center gap-2 text-sm">
              <div className="w-6 h-6 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white text-xs font-medium">
                {(user.full_name || user.email).charAt(0).toUpperCase()}
              </div>
              <div className="flex-1">
                <span className="font-medium">
                  {user.full_name || user.email.split('@')[0]}
                </span>
                <div className="text-xs text-base-content/60">
                  {user.current_section === 'workflow-editor' && 'Editing workflow'}
                  {user.current_section === 'collaborators' && 'Managing collaborators'}
                  {!user.current_section && 'Active'}
                </div>
              </div>
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}