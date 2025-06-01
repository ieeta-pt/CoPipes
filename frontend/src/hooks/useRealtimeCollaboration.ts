"use client";

import { useState, useEffect, useRef } from "react";
import { createClient } from "@supabase/supabase-js";

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

export function useRealtimeCollaboration({
  workflowId,
  enabled = true
}: RealtimeCollaborationOptions = {}) {
  const [presence, setPresence] = useState<Record<string, Presence>>({});
  const [isConnected, setIsConnected] = useState(false);
  const channelRef = useRef<any>(null);
  const [currentUser, setCurrentUser] = useState<any>(null);

  // Get current user
  useEffect(() => {
    const getCurrentUser = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      setCurrentUser(user);
    };
    getCurrentUser();
  }, []);

  // Setup realtime channel
  useEffect(() => {
    if (!enabled || !workflowId || !currentUser || !supabase) return;

    const channel = supabase.channel(`workflow-${workflowId}`, {
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
      .on('presence', { event: 'join' }, ({ key, newPresences }) => {
        console.log('User joined:', key, newPresences);
      })
      .on('presence', { event: 'leave' }, ({ key, leftPresences }) => {
        console.log('User left:', key, leftPresences);
      })
      .subscribe(async (status) => {
        if (status === 'SUBSCRIBED') {
          // Track current user presence
          await channel.track({
            user_id: currentUser.id,
            email: currentUser.email,
            full_name: currentUser.user_metadata?.full_name,
            avatar_url: currentUser.user_metadata?.avatar_url,
            current_section: 'workflow-editor',
            last_seen: new Date().toISOString(),
          });
        }
      });

    channelRef.current = channel;

    return () => {
      if (channelRef.current) {
        supabase.removeChannel(channelRef.current);
        channelRef.current = null;
      }
      setIsConnected(false);
      setPresence({});
    };
  }, [workflowId, enabled, currentUser]);

  // Update cursor position
  const updateCursor = async (x: number, y: number) => {
    if (!channelRef.current || !currentUser || !supabase) return;

    await channelRef.current.track({
      user_id: currentUser.id,
      email: currentUser.email,
      full_name: currentUser.user_metadata?.full_name,
      avatar_url: currentUser.user_metadata?.avatar_url,
      cursor: { x, y },
      current_section: 'workflow-editor',
      last_seen: new Date().toISOString(),
    });
  };

  // Update current section
  const updateSection = async (section: string) => {
    if (!channelRef.current || !currentUser || !supabase) return;

    await channelRef.current.track({
      user_id: currentUser.id,
      email: currentUser.email,
      full_name: currentUser.user_metadata?.full_name,
      avatar_url: currentUser.user_metadata?.avatar_url,
      current_section: section,
      last_seen: new Date().toISOString(),
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