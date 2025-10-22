"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ScrollArea } from "@/components/ui/scroll-area";
import { SessionItemComponent } from "@/components/sidebar/session-item";
import { useUser } from "@/lib/hooks/use-user";
import {
  fetchSessions,
  type SessionItem,
} from "@/lib/services/session-service";

export function SessionList() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { userId } = useUser();

  const [sessions, setSessions] = useState<SessionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Get active session from URL query param
  const activeSessionId = searchParams.get("session_id");

  useEffect(() => {
    if (!userId) return;

    async function loadSessions() {
      try {
        setLoading(true);
        setError(null);
        const response = await fetchSessions(userId, 50, 0);
        setSessions(response.sessions);
      } catch (err) {
        console.error("Failed to fetch sessions:", err);
        setError("Failed to load sessions");
      } finally {
        setLoading(false);
      }
    }

    loadSessions();
  }, [userId]);

  const handleSessionClick = (sessionId: string) => {
    // Navigate to battle page with session_id query param
    router.push(`/battle?session_id=${sessionId}`);
  };

  if (loading) {
    return (
      <div className="px-2 py-4 text-center">
        <p className="text-xs text-muted-foreground">Loading sessions...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="px-2 py-4 text-center">
        <p className="text-xs text-destructive">{error}</p>
      </div>
    );
  }

  if (sessions.length === 0) {
    return (
      <div className="px-2 py-4 text-center">
        <p className="text-xs text-muted-foreground">No sessions yet</p>
      </div>
    );
  }

  return (
    <ScrollArea className="flex-1">
      <div className="space-y-1 px-2 pb-2">
        {sessions.map((session) => (
          <SessionItemComponent
            key={session.session_id}
            session={session}
            isActive={session.session_id === activeSessionId}
            onClick={handleSessionClick}
          />
        ))}
      </div>
    </ScrollArea>
  );
}
