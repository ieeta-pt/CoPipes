"use client";

import { useState, useEffect, useRef } from "react";
import { createClient } from "@supabase/supabase-js";
import { useAuth } from "@/contexts/AuthContext";

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

let supabase: any = null;

// Only initialize if environment variables are available
if (supabaseUrl && supabaseKey) {
  supabase = createClient(supabaseUrl, supabaseKey);
}

export interface Presence {
  user_id: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  cursor?: { x: number; y: number };
  current_section?: string;
  last_seen: string;
}

export interface RealtimeCollaborationOptions {
  workflowId?: string;
  enabled?: boolean;
}

export function useRealtimeCollaboration(
  workflowId?: string,
  options: { enabled?: boolean } = {}
) {
  const { enabled = true } = options;
  const [presence, setPresence] = useState<Record<string, Presence>>({});
  const [isConnected, setIsConnected] = useState(false);
  const [workflowUpdates, setWorkflowUpdates] = useState<any[]>([]);
  const channelRef = useRef<any>(null);
  const { user: currentUser, isAuthenticated } = useAuth();

  // Setup realtime channel
  useEffect(() => {
    if (!enabled || !workflowId || !currentUser || !isAuthenticated || !supabase) {
      return;
    }


    const channelName = `workflow:${workflowId}`;
    const channel = supabase.channel(channelName, {
      config: {
        presence: {
          key: currentUser.id,
        },
      },
    });

    // Track presence
    channel
      .on('presence', { event: 'sync' }, () => {
        const presenceState = channel.presenceState();
        const users: Record<string, Presence> = {};
        
        Object.keys(presenceState).forEach((userId) => {
          const userPresence = presenceState[userId];
          if (userPresence && userPresence.length > 0) {
            users[userId] = userPresence[0] as Presence;
          }
        });
        
        setPresence(users);
        setIsConnected(true);
      })
      .on('presence', { event: 'join' }, () => {
      })
      .on('presence', { event: 'leave' }, () => {
      })
      .on('broadcast', { event: 'workflow_update' }, ({ payload }: { payload: any }) => {
        if (payload.user_id !== currentUser.id) {
          setWorkflowUpdates(prev => [...prev, payload]);
        }
      })
      .subscribe(async (status: string) => {
        if (status === 'SUBSCRIBED') {
          // Track current user presence
          const userPresence = {
            user_id: currentUser.id,
            email: currentUser.email,
            full_name: currentUser.full_name,
            current_section: 'workflow-editor',
            last_seen: new Date().toISOString(),
          };
          await channel.track(userPresence);
        }
      });

    channelRef.current = channel;

    return () => {
      if (channelRef.current) {
        channelRef.current.untrack();
        supabase.removeChannel(channelRef.current);
        channelRef.current = null;
      }
      setIsConnected(false);
      setPresence({});
    };
  }, [workflowId, enabled, currentUser, isAuthenticated]);

  // Update cursor position
  const updateCursor = async (x: number, y: number) => {
    if (!channelRef.current || !currentUser || !supabase) return;

    const updatedPresence = {
      user_id: currentUser.id,
      email: currentUser.email,
      full_name: currentUser.full_name,
      cursor: { x, y },
      current_section: 'workflow-editor',
      last_seen: new Date().toISOString(),
    };

    await channelRef.current.track(updatedPresence);
  };

  // Update current section
  const updateSection = async (section: string) => {
    if (!channelRef.current || !currentUser || !supabase) return;

    const updatedPresence = {
      user_id: currentUser.id,
      email: currentUser.email,
      full_name: currentUser.full_name,
      current_section: section,
      last_seen: new Date().toISOString(),
    };

    await channelRef.current.track(updatedPresence);
  };

  // Broadcast workflow updates
  const broadcastWorkflowUpdate = async (update: any) => {
    if (!channelRef.current || !currentUser) return;

    await channelRef.current.send({
      type: 'broadcast',
      event: 'workflow_update',
      payload: {
        user_id: currentUser.id,
        email: currentUser.email,
        update,
        timestamp: new Date().toISOString(),
      }
    });
  };

  // Get other users (exclude current user)
  const otherUsers = Object.values(presence).filter(
    user => user.user_id !== currentUser?.id
  );

  return {
    presence,
    otherUsers,
    isConnected,
    updateCursor,
    updateSection,
    broadcastWorkflowUpdate,
    workflowUpdates,
    currentUser,
  };
}

// Helper to generate consistent colors for users
export function getUserColor(userId: string): string {
  let hash = 0;
  if (userId.length === 0) return `hsl(0, 70%, 50%)`;
  for (let i = 0; i < userId.length; i++) {
    const char = userId.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return `hsl(${Math.abs(hash) % 360}, 70%, 50%)`;
}